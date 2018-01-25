"""定义了服务器的错误.

包括:

* ListenerError  钩子注册错误
* MultipleProcessDone  通过抛出这个异常来中断多进程任务的主进程循环
"""


class ListenerError(Exception):
    """钩子注册错误."""

    pass


class MultipleProcessDone(Exception):
    """通过抛出这个异常来中断多进程任务的主进程循环."""

    pass
