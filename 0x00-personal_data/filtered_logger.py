#!/usr/bin/env python3
"""
Protecting PII
"""

import logging
import os
import re
from typing import List

PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'ip')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """Returns the log message with obfuscated PII"""
    for field in fields:
        pattern = re.compile(rf"{field}=.*?{separator}")
        message = pattern.sub(f"{field}={redaction}{separator}", message)
    return message


def get_logger() -> logging.Logger:
    """Returns a logger object configured with required settings"""
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = RedactingFormatter(
        fmt="[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s",
        redaction="***",
        separator=";"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


class RedactingFormatter(logging.Formatter):
    """Custom log formatter to obfuscate PII"""

    def __init__(self, fmt: str, redaction: str, separator: str):
        super().__init__(fmt)
        self.redaction = redaction
        self.separator = separator

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record by obfuscating PII fields"""
        message = super().format(record)
        return filter_datum(PII_FIELDS, self.redaction, message, self.separator)


def get_db() -> None:
    """Connects to MySQL db using environment variables"""
    user = os.getenv('PERSONAL_DATA_DB_USERNAME')
    password = os.getenv('PERSONAL_DATA_DB_PASSWORD')
    db_host = os.getenv('PERSONAL_DATA_DB_HOST')
    db_name = os.getenv('PERSONAL_DATA_DB_NAME')

    if not all([user, password, db_host, db_name]):
        raise ValueError("Incomplete or missing environment variables for database connection.")

    return create_db_connection(user, password, db_host, db_name)


def create_db_connection(user: str, password: str, host: str, database: str):
    """Creates a database connection"""
    # Replace this code with your actual implementation.
    print(f"Creating database connection for user={user}, "
          f"host={host}, database={database}")
    return None
