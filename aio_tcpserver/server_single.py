"""单进程单线程执行TCP服务.

提供的接口为

tcp_serve(
        host: str, port: int,
        serv_protocol: asyncio.Protocol, *,
        loop: asyncio.AbstractEventLoop=None,
        ssl: Optional[SSLContext]=None,
        reuse_port: bool=False,
        sock: Optional[socket]=None,
        backlog: int=100,
        signal: Optional[Signal]=None,
        debug: bool=False,
        run_multiple: bool = False,
        connections: set=None,
        run_async: bool=False,
        graceful_shutdown_timeout: float=15.0) -> None

"""
import os
import platform
from ssl import SSLContext
from socket import socket
from functools import partial
import warnings
from typing import (
    Optional
)
from .log import server_logger as logger
from .utils import (
    Signal,
    update_current_time,
    get_protocol_params
)
from .hook import (
    LISTENERS,
    HOOK_REVERSE,
    trigger_events
)
from signal import (
    SIGTERM, SIGINT,
    SIG_IGN,
    signal as signal_func
)

if platform.system() == "Windows":
    try:
        import aio_windows_patch as asyncio
    except:
        import warnings
        warnings.warn(
            "you should install aio_windows_patch to support windows",
            RuntimeWarning,
            stacklevel=3)
        import asyncio

else:
    import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


def tcp_serve(host: str,
              port: int,
              serv_protocol: asyncio.Protocol, *,
              signal: Optional[Signal]=None,
              loop: asyncio.AbstractEventLoop=None,
              ssl: Optional[SSLContext]=None,
              reuse_port: bool=False,
              sock: Optional[socket]=None,
              backlog: int=100,
              debug: bool=False,
              run_multiple: bool = False,
              connections: set=None,
              run_async: bool=False,
              graceful_shutdown_timeout: float=15.0,
              current_time: bool=True) -> None:
    """执行一个单一进程的协程服务.

    Params:

        host (str) : - 主机地址
        port (int) : - 主机端口
        serv_protocol (asyncio.Protocol) : - 协议类,需要有signal字段用于保存控制是否停止的信号实例
        loop (asyncio.AbstractEventLoop) : - 服务要使用的事件循环
        ssl (Optional[ssl.SSLContext]) : 使用ssl默认值为None
        reuse_port (bool) : - 是否重用端口默认为False
        sock (Optional[socket]) : - 指定套接字默认为None,注意如果用socket,host和port就必须为None
        backlog (int) :- 传递给队列的最大连接数,默认为100,
        signal (Optional[Signal]) : - 与协议中公用的一个信号,用于关闭协议,需要有stopped字段 默认为None,
        debug (bool) : - 是否要使用debug模式
        run_multiple (bool) : - 是否是多进程模式默认为False
        run_async (bool) : - 当设置为true的时候将创建的服务器协程返回,而不是执行这个协程,默认为False,
        connections (Optional[set]) : - 可以设定一个装载连接的容器,默认为None
        graceful_shutdown_timeout (float) : - 是否在关闭前等待一段时间,默认为15.0s    
        current_time (bool) : - 是否使用一个全局变量来维护当前时间
    """
    if not run_async:
        # create new event_loop after fork
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if debug:
        loop.set_debug(debug)
    listeners = {}
    for event_name, reverse in HOOK_REVERSE:
        listeners[event_name] = LISTENERS[event_name].copy()
        if reverse:
            listeners[event_name].reverse()

    # 管理连接,
    connections = connections if connections is not None else set()
    # 为协议添加与服务器相关的参数
    protocol_params = get_protocol_params(serv_protocol)
    if connections:
        if 'connections' in protocol_params:
            serv_protocol = partial(serv_protocol, connections=connections)
    if signal:
        if 'signal' in protocol_params:
            serv_protocol = partial(serv_protocol, signal=signal)
        else:
            warnings.warn(
                "protocol do not has param 'signal' ",
                RuntimeWarning,
                stacklevel=3)

    server_coroutine = loop.create_server(
        serv_protocol,
        host,
        port,
        ssl=ssl,
        reuse_port=reuse_port,
        sock=sock,
        backlog=backlog
    )

    # 每分钟更新一次当前时间
    if current_time:
        loop.call_soon(partial(update_current_time, loop))

    if run_async:
        return server_coroutine
    # 执行钩子before_start
    trigger_events(listeners["before_server_start"], loop)

    try:
        rpc_server = loop.run_until_complete(server_coroutine)
    except BaseException:
        logger.exception("Unable to start server")
        return
    # 执行钩子after_start
    trigger_events(listeners["after_server_start"], loop)

    # 多进程时是使用SIG_IGN函数处理信号SIGINT,让这个ctrl+c的信号被屏蔽(posix平台)
    if run_multiple:
        signal_func(SIGINT, SIG_IGN)

    # 为优雅的关闭服务而注册信号
    # 信号会被注册到loop中用于执行回调函数loop.stop
    # 当收到规定的信号后loop就会停止
    _singals = (SIGTERM,) if run_multiple else (SIGINT, SIGTERM)
    for _signal in _singals:
        try:
            loop.add_signal_handler(_signal, loop.stop)
        except NotImplementedError as ni:
            print(str(ni))
            logger.warning('tried to use loop.add_signal_handler '
                           'but it is not implemented on this platform.')
    # 获取进程id方便多进程时debug
    pid = os.getpid()
    try:
        # 服务运行
        logger.info('Starting worker [%s]', pid)
        loop.run_forever()
    finally:
        # 服务结束阶段
        logger.info("Stopping worker [%s]", pid)
        # 运行钩子 before_stop
        trigger_events(listeners["before_server_stop"], loop)
        # 关闭server
        rpc_server.close()
        loop.run_until_complete(rpc_server.wait_closed())
        # 关闭连接
        # 完成所有空转连接的关闭工作
        if signal:
            signal.stopped = True
        for connection in connections:
            connection.close_if_idle()

        # 等待由graceful_shutdown_timeout设置的时间
        # 让还在运转的连接关闭,防止连接一直被挂起
        start_shutdown = 0
        while connections and (start_shutdown < graceful_shutdown_timeout):
            loop.run_until_complete(asyncio.sleep(0.1))
            start_shutdown = start_shutdown + 0.1

        # 在等待graceful_shutdown_timeout设置的时间后
        # 强制关闭所有的连接
        for conn in connections:
            conn.close()
        # 收尾阶段关闭所有协程,
        loop.run_until_complete(loop.shutdown_asyncgens())
        # 执行钩子after_stop
        trigger_events(listeners["after_server_stop"], loop)
        # 关闭loop
        loop.close()
        logger.info("Stopped worker [%s]", pid)
