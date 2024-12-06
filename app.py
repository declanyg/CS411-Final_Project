from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
import os
from typing import Dict

from weather_management.models import user_model
from weather_management.models import CurrentWeather_model
from weather_management.models import WeatherData_model
from weather_management.models.favourites_model import FavouritesModel
from weather_management.utils.sql_utils import check_database_connection, check_table_exists


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

favourites_models: Dict[str, FavouritesModel] = {}

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
    Route to check if the database connection and Users table are functional.

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
def create_account() -> Response:
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
        favourites_models[username] = FavouritesModel(username, os.getenv("API_KEY"))
        app.logger.info("Sucessfully created user: %s", username)
        return make_response(jsonify({'status': 'success', 'username': username}), 200)
    except Exception as e:
        app.logger.error("Failed to create user: %s", str(e))
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/update-password', methods=['POST'])
def update_password() -> Response:
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
    

##########################################################
#
# Favourite Weather Management
#
##########################################################

@app.route('/api/set_favourite_location', methods=['POST'])
def set_favourite_location() -> Response:
    """
    Route for a user to to set a location as a favourite.

    Expected JSON Input:
        - username (str): The user's username.
        - location (str): The location to add to favourites.

    Returns:
        JSON response indicating success of the addition or error message.
    """
    try:
        data = request.get_json()

        username = data.get('username')
        location = data.get('location')

        if not username or not location:
            return make_response(jsonify({'error': 'Invalid input. username, and location are required.'}), 400)

        # Get the cooresponding FavouritesModel
        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        # Add location to favourites
        favourite_model.set_favourite_location(location)

        app.logger.info(f"Location added to {username}'s favourites: {location}")
        return make_response(jsonify({'status': 'success', 'message': 'Location added to favourites'}), 201)

    except Exception as e:
        app.logger.error(f"Error adding location to favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/remove_favourite_location', methods=['POST'])
def remove_favourite_location() -> Response:
    """
    Route for a user to to remove a location from their favourites.

    Expected JSON Input:
        - username (str): The user's username.
        - location (str): The location to remove from favourites.

    Returns:
        JSON response indicating success of the removal or error message.
    """
    try:
        data = request.get_json()

        username = data.get('username')
        location = data.get('location')

        if not username or not location:
            return make_response(jsonify({'error': 'Invalid input. username, and location are required.'}), 400)

        # Get the cooresponding FavouritesModel
        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        # Remove location from favourites
        favourite_model.set_favourite_location(location)

        app.logger.info(f"Location removed from {username}'s favourites: {location}")
        return make_response(jsonify({'status': 'success', 'message': 'Location removed from favourites'}), 201)

    except Exception as e:
        app.logger.error(f"Error removing location from favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/clear-favourites', methods=['POST'])
def clear_favourites() -> Response:
    """
    Route to clear all favourited locations from a user's favourites.

    Expected JSON Input:
        - username (str): The user's username.

    Returns:
        JSON response indicating success of the operation or an error message.
    """
    try:
        data = request.get_json()

        username = data.get('username')

        if not username:
            return make_response(jsonify({'error': 'Invalid input. username required.'}), 400)
        
        app.logger.info('Clearing %s\'s favourite locations', username)

        # Get the cooresponding FavouritesModel
        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        # Clear the entire playlist
        favourite_model.clear_favourites()

        return make_response(jsonify({'status': 'success', 'message': 'Favourites cleared'}), 200)

    except Exception as e:
        app.logger.error(f"Error clearing favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

##########################################################
#
# Favourite Weather Retrieval
#
##########################################################

@app.route('/api/get-all-favourites/<string:username>', methods=['GET'])
def get_all_favourite_locations(username: str) -> Response:
    """
    Route to retrieve all favourited locations.

    Path parameter:
        - username (str): The user's username.

    Returns:
        JSON response with the list of locations or an error message.
    """
    try:
        app.logger.info("Retrieving all favourites locations from the playlist")

        # Get the cooresponding FavouritesModel
        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        # Get all locations from favourites
        favourites = favourite_model.get_all_favourites()

        return make_response(jsonify({'status': 'success', 'favourited_locations': favourites}), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving locations from favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get_weather_by_favourite_location/<string:username>/<int:location>', methods=['GET'])
def get_weather_by_favourite_location(username: str, location: str) -> Response:
    """
    Route to retrieve a user's favourite location's weather.

    Path Parameters:
        - username (str): The username
        - location (str): The favourite location

    Returns:
        JSON response with the location's current weather or error message.
    """
    try:
        app.logger.info(f"Retrieving current weather from favourites by favourite location: {location}")

        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        #Get current weather from favourited location
        weather = favourite_model.get_weather_by_favourite_location(location)

        return make_response(jsonify({'status': 'success', 'weather': weather}), 200)

    except ValueError as e:
        app.logger.error(f"Error retrieving weather by favourite location: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error retrieving weather from favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get_all_favourite_weathers/<string:username>', methods=['GET'])
def get_all_favourite_weathers(username: str) -> Response:
    """
    Route to retrieve the weather for all of a user's favourite locations.

    Path Parameter:
        - username (str): The username

    Returns:
        JSON response with all of the current weathers or error message.
    """
    try:
        app.logger.info(f"Retrieving current weather for {username}'s favourite locations")

        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        #Get current weather from favourited location
        weathers = favourite_model.get_all_favourite_weathers(location)

        return make_response(jsonify({'status': 'success', 'weathers': weathers}), 200)

    except ValueError as e:
        app.logger.error(f"Error retrieving weathers: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error retrieving weathers from favourites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get_historical_weather_by_favourite_location/<string:username>/<string:favourite_location>/<string:date>', methods=['GET'])
def get_historical_weather_by_favourite_location(username: str, favourite_location: str, date: str) -> Response:
    """
    Route to retrieve the weather for all of a user's favourite locations.

    Path Parameters:
        - username (str): The username
        - favourite_location (str): The name of the favourite location
        - date (str): The date to retrieve the weather of (in the format of YYYY-MM-dd)

    Returns:
        JSON response with the historical weather data for the given date or error message.
    """
    try:
        app.logger.info(f"Retrieving historical weather data from {date}")

        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        #Get historical weather from favourited location
        historicalWeatherData = favourite_model.get_historical_weather_by_favourite_location(favourite_location, date)

        return make_response(jsonify({'status': 'success', 'date': date, 'weather': historicalWeatherData}), 200)

    except ValueError as e:
        app.logger.error(f"Error retrieving historical weather data: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error retrieving historical weather data from favourited location: {e}")
        return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/get_forecast_by_favourite_location/<string:username>/<string:favourite_location>/<int:days>', methods=['GET'])
def get_forecast_by_favourite_location(username: str, favourite_location: str, days: int) -> Response:
    """
    Route to retrieve the forecast for the next upcoming days for a favourite location.

    Path Parameters:
        - username (str): The username
        - favourite_location (str): The name of the favourite location
        - days (int): The number of upcoming days to retrieve (up to 10)

    Returns:
        JSON response with the forecasted weather for the given amount of days or error message.
    """
    try:
        app.logger.info(f"Retrieving forecasted weather data for the next {days} days")

        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        #Get forecasted weather from favourited location
        forecastedWeatherData = favourite_model.get_forecast_by_favourite_location(favourite_location, days)

        return make_response(jsonify({'status': 'success', 'forecast': forecastedWeatherData}), 200)

    except ValueError as e:
        app.logger.error(f"Error retrieving forecasted weather data: {e}")
        return make_response(jsonify({'error': str(e)}), 404)
    except Exception as e:
        app.logger.error(f"Error retrieving forecasted weather data from favourited location: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get_favourites_length/<string:username>', methods=['GET'])
def get_favourites_length(username: str) -> Response:
    """
    Route to retrieve a the number of favourite locations a user has.

    Returns:
        JSON response with the favourites length or error message.
    """
    try:
        app.logger.info("Retrieving favourites length")

        if username not in favourites_models:
            return make_response(jsonify({'error': f'User {username} not found.'}), 404)
        favourite_model = favourites_models[username]

        # Get favourites length
        favourites_length = favourite_model.get_favourites_length()

        return make_response(jsonify({
            'status': 'success',
            'favourites_length': favourites_length,
        }), 200)

    except Exception as e:
        app.logger.error(f"Error retrieving favourites length: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
