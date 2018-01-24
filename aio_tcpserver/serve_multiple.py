"""多进程执行tcp服务.

签名为:multiple_tcp_serve(server_settings: dict, workers: int)->None

"""
import os
from multiprocessing import Process
from typing import Dict, Any
from socket import (
    socket,
    SOL_SOCKET,
    SO_REUSEADDR
)
from signal import (
    SIGTERM, SIGINT,
    signal as signal_func,
    Signals
)
from .log import server_logger as logger
from .server_single import tcp_serve


def multiple_tcp_serve(server_settings: Dict[str, Any], workers: int)->None:
    """启动一个多进程的tcp服务,他们共享同一个socket对象.

    用multiple模式在每个子进程执行tcp服务,当执行完成后统一的回收资源

    Params:

        server_settings (Dicct[str, Any]) : - 每个单一进程的设置,

        workers (int) : - 执行的进程数

    """
    server_settings['reuse_port'] = True
    server_settings['run_multiple'] = True

    # Handling when custom socket is not provided.
    if server_settings.get('sock') is None:
        sock = socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((server_settings['host'], server_settings['port']))
        sock.set_inheritable(True)
        server_settings['sock'] = sock
        server_settings['host'] = None
        server_settings['port'] = None

    def sig_handler(signal: Any, frame: Any):
        """向子进程传送SIGTERM信号,用于关闭所有子进程中运行的事件循环.

        Params:

            signal (Any) : - 要处理的信号
            frame (Any) : - 执行到的帧
        """
        logger.info("Received signal %s. Shutting down.", Signals(signal).name)
        for process in processes:
            os.kill(process.pid, SIGTERM)

    signal_func(SIGINT, lambda s, f: sig_handler(s, f))
    signal_func(SIGTERM, lambda s, f: sig_handler(s, f))

    processes = []

    for _ in range(workers):
        process = Process(target=tcp_serve, kwargs=server_settings)
        process.daemon = True
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    # 使用join同步后,只有进程运行结束了才关闭子进程
    for process in processes:
        process.terminate()
    server_settings.get('sock').close()
