import logging
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# Path to the logs directory
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')

# Ensure the logs directory exists
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Ensure the errors.log file exists
LOG_FILE_PATH = os.path.join(LOGS_DIR, 'errors.log')
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, 'w'):  # Create the file if it doesn't exist
        pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/errors.log',
            'backupCount': 10,  # Keep 10 old log files
            'maxBytes': 1024 * 1024 * 5,  # 5MB per log file
            'level': 'ERROR',  # Log only ERROR and higher level messages
            'formatter': 'standard',
        },
    },

    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },

    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'pymongo.topology._debug_log': {
            'handlers': [],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'pymongo': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'urllib3': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'urllib3.connectionpool': {
            'handlers': [],
            'level': 'WARNING',
            'propagate': False,
        },
        'asyncio': {
            'handlers': [],
            'level': 'WARNING',  # or 'CRITICAL' to completely silence
            'propagate': False,
        },
    },
}
