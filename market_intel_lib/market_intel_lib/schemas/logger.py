from enum import StrEnum


class LoggingLevel(StrEnum):
    """Logging levels for the service.

    Can be used to configure the logging level of the application based on the deployment or environment.
    """

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"