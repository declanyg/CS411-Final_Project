from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request

from weather_management.models import user_model
from weather_management.models.playlist_model import PlaylistModel
from weather_management.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

playlist_model = PlaylistModel()


####################################################
#
# Healthchecks
#
####################################################

@app.route('/api/health', methods=['GET'])
def healthcheck() -> Response:
    """
    Health check route to verify the service is running.

    Returns:
        JSON response indicating the health status of the service.
    """
    app.logger.info('Health check')
    return make_response(jsonify({'status': 'healthy'}), 200)


@app.route('/api/db-check', methods=['GET'])
def db_check() -> Response:
    """
    Route to check if the database connection and songs table are functional.

    Returns:
        JSON response indicating the database health status.
    Raises:
        404 error if there is an issue with the database.
    """
    try:
        app.logger.info("Checking database connection...")
        check_database_connection()
        app.logger.info("Database connection is OK.")
        app.logger.info("Checking if Users table exists...")
        check_table_exists("Users")
        app.logger.info("Users table exists.")
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)


##########################################################
#
# Password Storage
#
##########################################################

@app.route('/api/login', methods=['POST'])
def login() -> Response:
    """
    Route to login to a user.

    Expected JSON Input:
        - username (str): The user's username.
        - password (str): The password.

    Returns:
        JSON response indicating the success of the login.
    Raises:
        400 error if input validation fails.
        401 error if the password is incorrect.
        500 error if there is an issue with the login.

    """
    app.logger.info('Logging into a user')
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Log into the user
        app.logger.info('Logging into user: %s', username)
        if user_model.login(username=username, password=password):
            app.logger.info("Sucessfully logged into user: %s", username)
            return make_response(jsonify({'status': 'success', 'username': username}), 200)
        else:
            app.logger.info("Incorrect password for user: %s", username)
            return make_response(jsonify({'status': 'error', 'message': 'Invalid password'}), 401)
    except Exception as e:
        app.logger.error("Failed to login: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/create-account', methods=['POST'])
def login() -> Response:
    """
    Route to create a new user

    Expected JSON Input:
        - username (str): The user's username.
        - password (str): The user's password.

    Returns:
        JSON response indicating the success of the user creation.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue creating the user.
    """
    app.logger.info('Logging into a user')
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Create user
        app.logger.info('Creating user: %s', username)
        user_model.create_user(username=username, password=password)
        app.logger.info("Sucessfully created user: %s", username)
        return make_response(jsonify({'status': 'success', 'username': username}), 200)
    except Exception as e:
        app.logger.error("Failed to create user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/update-password', methods=['POST'])
def login() -> Response:
    """
    Route to create a new user

    Expected JSON Input:
        - username (str): The user's username.
        - password (str): The user's password.

    Returns:
        JSON response indicating the success of the password change.
    Raises:
        400 error if input validation fails.
        500 error if there is an issue updating the password.
    """
    app.logger.info('Logging into a user')
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        if username is None or password is None:
            return make_response(jsonify({'error': 'Invalid input, all fields are required with valid values'}), 400)

        # Create user
        app.logger.info('Changing password for user: %s', username)
        user_model.update_password(username=username, password=password)
        app.logger.info("Sucessfully updated password for user: %s", username)
        return make_response(jsonify({'status': 'success', 'username': username}), 200)
    except Exception as e:
        app.logger.error("Failed to update password: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
