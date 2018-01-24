"""公用的一些组件.

包括:

* 用于维护CURRENT_TIME为当前时间的函数update_current_time

* 用于管理协议是否继续执行的信号类Signal
"""
import asyncio
from time import time
from functools import partial
CURRENT_TIME = None


def update_current_time(loop: asyncio.AbstractEventLoop)->None:
    """缓存当前时间,用于管理timeout,缓存于全局变量CURRENT_TIME.

    Params:

        loop (asyncio.AbstractEventLoop) : - 服务使用的事件循环

    """
    global CURRENT_TIME
    CURRENT_TIME = time()
    loop.call_later(1, partial(update_current_time, loop))


class Signal:
    """用于管理协议是否继续执行.

    Attributs:

        stopped (bool) : - 控制协议是否终止执行

    """

    stopped = False
