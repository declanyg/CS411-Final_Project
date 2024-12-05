from dataclasses import dataclass
import logging
import os
import sqlite3
import bcrypt

from weather_management.utils.logger import configure_logger
from weather_management.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class User:
    id: int
    username: str
    salt: str
    hashed_password: str

def login(username: str, password: int) -> bool:
    """
    Log into a user stored in the users table.

    Args:
        username (str): The user's username.
        hashed_password (str): The hashed_password for the user.

    Raises:
        ValueError: If username is invalid.
        ValueError: If username is invalid.
        sqlite3.Error: For any other database errors.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to login user with username %d", username)

            cursor.execute("SELECT (salt, hashed_password) FROM Users WHERE username = ?", (username,))
            row = cursor.fetchone()[0]
            if row:
                salt, hashed_password = row[0], row[1]
                # Check the password
                if hashed_password == bcrypt.hashpw(password.encode('utf-8'), salt):
                    logger.info("Logged into user with username %d", username)
                    return True
                else:
                    logger.info("Incorrect password for user with username %d", username)
                    return False
            else:
                logger.info("User with username %d not found", username)
                raise ValueError(f"User with username {username} not found")


    except sqlite3.Error as e:
        logger.error("Database error while updating password for user with username %s: %s", username, str(e))
        raise e

def create_user(username: str, password: int) -> None:
    """
    Creates a new user in the users table.

    Args:
        username (str): The user's username.
        hashed_password (str): The hashed_password for the user.

    Raises:
        ValueError: If username is invalid.
        sqlite3.IntegrityError: If a user with the same compound key (username, hashed_password) already exists.
        sqlite3.Error: For any other database errors.
    """
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Validate the required fields
    try:
        # Use the context manager to handle the database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Users (username, salt, hashed_password)
                VALUES (?, ?, ?)
            """, (username, salt, hashed_password))
            conn.commit()

            logger.info("User created successfully: %s (%s) - (%s)", username, salt, hashed_password)

    except sqlite3.IntegrityError as e:
        logger.error("User with username '%s', and hashed_password '%s' already exists.", username, hashed_password)
        raise ValueError(f"User with username '{username}', and hashed_password '{hashed_password}' already exists.") from e
    except sqlite3.Error as e:
        logger.error("Database error while creating user: %s", str(e))
        raise sqlite3.Error(f"Database error: {str(e)}")

def update_password(username: str, password: str) -> None:
    """
    Updates a user's password.

    Args:
        username (str): The username for the user to update.
        password (str): The password to update for a user.

    Raises:
        ValueError: If the user does not exist.
        sqlite3.Error: If there is a database error.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info("Attempting to update password for user with username %d", username)

            cursor.execute("SELECT salt FROM Users WHERE username = ?", (username,))
            salt = cursor.fetchone()[0]
            if salt:
                # Update the password
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
                cursor.execute("UPDATE Users SET hashed_password = ? WHERE user = ?", (hashed_password, username,))
                conn.commit()

                logger.info("Password changed for user with username: %s", username)
            else:
                logger.info("User with username %d not found", username)
                raise ValueError(f"User with username {username} not found")


    except sqlite3.Error as e:
        logger.error("Database error while updating password for user with username %s: %s", username, str(e))
        raise e
