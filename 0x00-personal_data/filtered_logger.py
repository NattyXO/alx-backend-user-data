#!/usr/bin/env python3
"""
0x05. Personal data
How to implement a log filter that will obfuscate PII fields
How to encrypt a password and check the validity
How to authenticate to a database using environment variables
"""

import os
import re
import mysql.connector
from typing import List
import logging


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    """
    Filters sensitive fields in the log message
    Args:
        fields: List of strings representing sensitive fields
        redaction: String representing the redacted value
        message: String representing the log line
        separator: String representing the field separator character in the log line
    Returns:
        The filtered log message
    """
    for field in fields:
        message = re.sub(rf"{field}=(.*?)\{separator}",
                         f"{field}={redaction}{separator}", message)
    return message


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class"""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize the RedactingFormatter"""
        self.fields = fields
        super(RedactingFormatter, self).__init__(self.FORMAT)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record"""
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Returns a logging.Logger object named "user_data"
    with a StreamHandler using the RedactingFormatter
    and logging level set to INFO
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """Connects to a secure holberton database to read a users table."""
    DB_user = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    DB_password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    DB_host_name = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    DB_name = os.environ.get("PERSONAL_DATA_DB_NAME")
    connection = mysql.connector.connect(
        host=DB_host_name,
        database=DB_name,
        user=DB_user,
        password=DB_password,
    )
    return connection


def main():
    """Main function"""
    info_logger = get_logger()
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users;")
        rows = cursor.fetchall()
        for row in rows:
            record = "; ".join(f"{field}={value}" for field, value in zip(cursor.column_names, row))
            info_logger.info(record)


if __name__ == "__main__":
    main()
