#!/usr/bin/env python3
"""
Protecting PII
"""

from typing import List
import logging
import os
import re

PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'ip')


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """ Returns the log message obfuscated """
    temp = message
    for field in fields:
        temp = re.sub(field + "=.*?" + separator,
                      field + "=" + redaction + separator, temp)
    return temp


def get_logger() -> logging.Logger:
    """ Returns a logger object """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    handler = logging.StreamHandler()
    formatter = RedactingFormatter(PII_FIELDS)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


def get_db() -> None:
    """ Connects to MySQL db using env vars """
    user = os.environ.get('PERSONAL_DATA_DB_USERNAME', None)
    password = os.environ.get('PERSONAL_DATA_DB_PASSWORD', None)
    db_host = os.environ.get('PERSONAL_DATA_DB_HOST', None)
    db_name = os.environ.get('PERSONAL_DATA_DB_NAME', None)

    return None


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """ Initializes the class instance """
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Filters values in incoming log records """
        return filter_datum(
            self.fields, self.REDACTION, super().format(record),
            self.SEPARATOR)
