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
    Returns the log message with obfuscated PII fields.

    Args:
        fields: A list of strings representing all fields.
        redaction: A string representing the obfuscation string.
        message: A string representing the log line.
        separator: A string representing the field separator in the log line.

    Returns:
        The obfuscated log message.
    """
    for field in fields:
        message = re.sub(rf"{field}=(.*?){separator}",
                         f"{field}={redaction}{separator}", message)
    return message


class RedactingFormatter(logging.Formatter):
    """Redacting Formatter class."""

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """Initialize the formatter."""
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        message = super().format(record)
        return filter_datum(self.fields, self.REDACTION,
                            message, self.SEPARATOR)


def get_logger() -> logging.Logger:
    """
    Return a Logger object with the required settings.
    """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = RedactingFormatter(PII_FIELDS)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """
    Connect to the secure Holberton database to read the users table.
    """
    db_user = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    db_password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    db_host = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.environ.get("PERSONAL_DATA_DB_NAME")

    connection = mysql.connector.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    return connection


def main():
    """
    Main function to execute the program.
    """
    fields = "name,email,phone,ssn,password,ip,last_login,user_agent"
    columns = fields.split(",")
    query = "SELECT {} FROM users;".format(fields)
    info_logger = get_logger()
    connection = get_db()

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

        for row in rows:
            record = ("{}={}".format(col, val) for col, val in zip(columns, row))
            msg = "{};".format("; ".join(record))

            log_record = logging.LogRecord(
                name="user_data",
                level=logging.INFO,
                pathname=None,
                lineno=None,
                msg=msg,
                args=None,
                exc_info=None
            )

            info_logger.handle(log_record)


if __name__ == "__main__":
    main()
