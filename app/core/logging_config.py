import logging.config

# Configuration dictionary for logging
LOGGING_CONFIG = {
    'version': 1,  # Version of the logging configuration schema
    'disable_existing_loggers': False,  # Allow existing loggers to propagate
    'formatters': {
        'standard': {
            'format': 'Bulk Action API Service: %(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Define the log message format
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',  # Set the minimum log level to INFO. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
            'formatter': 'standard',  # Use the 'standard' formatter defined above
            'class': 'logging.StreamHandler',  # Output logs to the console (stdout)
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],  # Use the 'default' handler defined above
            'level': 'INFO',  # Set the minimum log level for the root logger
            'propagate': True  # Allow log messages to propagate to ancestor loggers
        },
        'sqlalchemy.engine': {
            'handlers': ['default'],  # Use the 'default' handler defined above
            'level': 'WARNING',  # Set the minimum log level for SQLAlchemy engine logs
            'propagate': False  # Prevent log messages from propagating to ancestor loggers
        },
    }
}


def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)


# Helper class to get logger instances
class LoggerHelper:
    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)
