"""aio_tcpserver.

@copyright 2017, hsz MIT License
@desc 一个简单的TCP服务器用于执行asyncio.Protocol的子类定义的协议,代码参考自sanic
"""
import platform
import logging.config
from typing import Optional, Dict, Any
from .server_single import tcp_serve
from .serve_multiple import multiple_tcp_serve
from .utils import Signal, CURRENT_TIME
from .hook import listener
from .log import server_logger as logger
from .config import SERVER_CONFIG, SERVER_LOGGING_CONFIG

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

SETABLE = ("host",
           "port",
           "username",
           "password",
           "loop",
           "ssl",
           "reuse_port",
           "sock",
           "backlog",
           "debug",
           "connections",
           "run_async",
           "graceful_shutdown_timeout",
           "current_time")


def tcp_server(
        serv_protocol: asyncio.Protocol, *,
        signal: Signal=Signal(),
        worker: int=None,
        costume_config: Optional[Dict[str, Any]]=None, **kwargs):
    """tcp服务器.

    用户可以自己在costume_config中指定设置,也可以利用关键字指定设置,优先顺序是:

    关键字 > 用户自定义设置 > 默认

    用户自定义设置具体参看config模块

    Parameters:

        host (str): - 主机地址

        port (int): - 主机端口

        serv_protocol (asyncio.Protocol): - 协议类,需要有signal字段用于保存控制是否停止的信号实例,\
需要__init__方法中有参数`signal`,`username`,`password`

        loop (asyncio.AbstractEventLoop): - 服务要使用的事件循环

        ssl (Optional[ssl.SSLContext]): - 使用ssl默认值为None

        reuse_port (bool): - 是否重用端口默认为False

        sock (Optional[socket]): - 指定套接字默认为None,注意如果用socket,host和port就必须为None

        backlog (int): - 传递给队列的最大连接数,默认为100,

        signal (Optional[Signal]): - 与协议中公用的一个信号,用于关闭协议,需要有stopped字段 默认为None,

        debug (bool): - 是否要使用debug模式

        run_multiple (bool): - 是否是多进程模式默认为False

        run_async (bool): - 当设置为true的时候将创建的服务器协程返回,而不是执行这个协程,默认为False,

        connections (Optional[set]): - 可以设定一个装载连接的容器,默认为None

        graceful_shutdown_timeout (float): - 是否在关闭前等待一段时间,默认为15.0s

        current_time (bool): - 是否使用一个全局变量来维护当前时间

        costume_config (Optional[Dict[str, Any]]): - 用户自定义设置
    """
    server_config = SERVER_CONFIG
    server_logging_config = SERVER_LOGGING_CONFIG

    if costume_config:
        if costume_config.get("SERVER_CONFIG"):
            server_config.update(costume_config.get("SERVER_CONFIG"))
        if costume_config.get("SERVER_LOGGING_CONFIG"):
            server_logging_config.update(costume_config.get(
                "SERVER_LOGGING_CONFIG"))

    logging.config.dictConfig(server_logging_config)
    server_config.update({
        "serv_protocol": serv_protocol,
        "signal": signal,
    })

    for i in SETABLE:
        if kwargs.get(i) is not None:
            server_config.update({
                i: kwargs.get(i)
            })

    if worker is not None and worker > 2:
        logger.info(
            'Multiple tcp server starting @{}:{}, Ctrl+C to exit'.format(
                server_config["host"],
                server_config["port"])
        )
        multiple_tcp_serve(server_config, worker)
    else:

        logger.info(
            'Single tcp server starting @{}:{}, Ctrl+C to exit'.format(
                server_config["host"],
                server_config["port"])
        )
        tcp_serve(**server_config)


__all__ = ["listener", 'tcp_server', 'CURRENT_TIME']
