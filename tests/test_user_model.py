from contextlib import contextmanager
import re
import sqlite3
import bcrypt

import pytest

from weather_management.models.user_model import (
    User,
    login,
    create_user,
    update_password,
    clear_users
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("weather_management.models.user_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test

######################################################
#
#    Login
#
######################################################

def test_login_success(mock_cursor, mocker):
    """Test successful login."""

    #Test data
    username = "Bob"
    password = "1234"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    mock_cursor.fetchone.return_value = (salt, hashed_password)
    mocker.patch("weather_management.models.user_model.bcrypt.hashpw", return_value=hashed_password)

    # Call the function to login to a new user
    result = login(username=username, password=password)
    assert result is True

    mock_cursor.execute.assert_called_once_with("SELECT salt, hashed_password FROM Users WHERE username = ?", (username,))

def test_login_failure(mock_cursor, mocker):
    """Test unsuccessful login."""

    #Test data
    username = "Bob"
    password = "1234"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    mock_cursor.fetchone.return_value = (salt, hashed_password)
    mocker.patch("weather_management.models.user_model.bcrypt.hashpw", return_value=bcrypt.hashpw('4321'.encode('utf-8'), salt))

    # Call the function to login to a new user
    result = login(username=username, password='4321')
    assert result is False

    mock_cursor.execute.assert_called_once_with("SELECT salt, hashed_password FROM Users WHERE username = ?", (username,))

def test_login_user_not_found(mock_cursor):
    mock_cursor.fetchone.return_value = None
    username = "Bob"
    with pytest.raises(ValueError, match=f"User with username {username} not found"):
        login(username=username, password='1234')

######################################################
#
#    Create
#
######################################################

def test_create_user_success(mock_cursor, mocker):
    """Test creating a new user in the database."""

    mocked_salt = bcrypt.gensalt()
    mocked_username = "Bob"
    mocked_password = "1234"
    mocked_hashed_password = bcrypt.hashpw(mocked_password.encode('utf-8'), mocked_salt)
    mocker.patch("weather_management.models.user_model.bcrypt.gensalt", return_value=mocked_salt)

    # Call the function to create a new user
    create_user(username=mocked_username, password=mocked_password)

    expected_query = normalize_whitespace("""
        INSERT INTO Users (username, salt, hashed_password)
        VALUES (?, ?, ?)
    """)

    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]

    # Assert that the SQL query was executed with the correct arguments
    expected_arguments = (mocked_username, mocked_salt, mocked_hashed_password)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

def test_create_user_duplicate(mock_cursor):
    """Test creating a user with a duplicate username (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: User.username")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="User with username 'Bob' already exists."):
        create_user(username="Bob", password="1234")

######################################################
#
#    Update
#
######################################################

def test_update_password_success(mock_cursor):
    """Test password update for an existing user."""
    mocked_salt = bcrypt.gensalt()
    mocked_username = "Bob"
    mocked_password = "1234"
    mocked_hashed_password = bcrypt.hashpw(mocked_password.encode('utf-8'), mocked_salt)
    mock_cursor.fetchone.return_value = (mocked_salt,)

    update_password(mocked_username, mocked_password)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE Users SET hashed_password = ? WHERE username = ?
    """)

    # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (username)
    expected_arguments = (mocked_hashed_password, mocked_username)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."
    
    mock_cursor.execute.assert_any_call("SELECT salt FROM Users WHERE username = ?", (mocked_username,))

def test_update_password_user_not_found(mock_cursor):
    """Test password update for a user that doesn't exist."""
    # Test data
    username = "Bob"
    new_password = "1234"
    
    # Mock database to return None for user lookup
    mock_cursor.fetchone.return_value = None

    # Import and call the update_password function
    with pytest.raises(ValueError, match=f"User with username {username} not found"):
        update_password(username=username, password=new_password)

######################################################
#
#    Clear
#
######################################################

def test_clear_users(mock_cursor, mocker):
    """Test clearing all users (removes all users)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_tables.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_users()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_tables.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()