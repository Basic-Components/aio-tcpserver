"""定义钩子相关的操作和设定.

钩子接受参数为loop的协程函数用于注册

包括:

* @listener(event) 用于注册协程到钩子
* trigger_events(events, loop: asyncio.AbstractEventLoop)->None 用于执行钩子
"""
import inspect
import platform
from typing import (
    List,
    Awaitable,
    Callable
)
from .errors import ListenerError
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
LISTENERS = {
    "before_server_start": [],
    "after_server_start": [],
    "before_server_stop": [],
    "after_server_stop": []
}
HOOK_REVERSE = (
    ("before_server_start", False),
    ("after_server_start", False),
    ("before_server_stop", True),
    ("after_server_stop", True),
)


def listener(event: str)->Callable:
    """装饰器,用于装饰协程来为服务器注册钩子.

    Parameters

        event (str): - 注册的钩子类型
    """
    if event not in LISTENERS.keys():
        raise ListenerError("Illegal hook")

    def decorator(listener: Awaitable)->Awaitable:
        """装饰函数,装饰一个协程函数.

        Params:

        listener (Awaitable): - 注册的钩子

        """
        if not inspect.iscoroutinefunction(listener):
            raise ListenerError(
                "Illegal listener,"
                "listener must be a coroutinefunction")
        LISTENERS[event].append(listener)
        return listener

    return decorator


def trigger_events(events: List[Awaitable], loop: asyncio.AbstractEventLoop)->None:
    """用于执行钩子操作.

    Params:
        events (List[Awaitable]): - 钩子要执行的协程函数队列
        loop (): - 事件循环
    """
    for event in events:
        result = event(loop)
        if inspect.isawaitable(result):
            loop.run_until_complete(result)
