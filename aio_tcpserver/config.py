"""默认的配置.

包含两块:

* SERVER_CONFIG用于配置默认的服务器参数
* SERVER_LOGGING_CONFIG用于配置默认的log参数
"""

SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "loop": None,
    "ssl": None,
    "reuse_port": False,
    "sock": None,
    "backlog": 100,
    "debug": False,
    "run_multiple": False,
    "connections": None,
    "run_async": False,
    "graceful_shutdown_timeout": 1.0,
    "current_time": True
}

SERVER_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "loggers": {
        "aio-tcpsever": {
            "level": "INFO",
            "handlers": ["console"]
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": 'ext://sys.stdout'
        }
    },
    "formatters": {
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter"
        }
    }
}
