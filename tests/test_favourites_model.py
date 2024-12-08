from contextlib import contextmanager
import re
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv

import pytest

from weather_management.models.favourites_model import FavouritesModel
from weather_management.models.user_model import User

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(dotenv_path=env_path)



@pytest.fixture()
def favourites_model():
    """Fixture to provide a new instance of FavouritesModel for each test."""
    return FavouritesModel(username="Bob", api_key=os.getenv("API_KEY"))

@pytest.fixture
def sample_place1():
    return ("Boston")

@pytest.fixture
def sample_place2():
    return ("New York")

######################################################
#
#    Favourite Location Management Functions Test Cases
#
######################################################

def test_set_favourite_location(favourites_model, sample_place1):
    """Test adding a location to a user's favourites."""
    favourites_model.set_favourite_location(sample_place1)
    assert len(favourites_model.favourites) == 1
    assert favourites_model.favourites[0] == sample_place1

def test_set_duplicate_favourite_location(favourites_model, sample_place1):
   """Test error when adding a duplicate favourite location"""
   favourites_model.set_favourite_location(sample_place1)
   assert len(favourites_model.favourites) == 1
   with pytest.raises(ValueError, match="Location with name Boston already exists in favourites"):
      favourites_model.set_favourite_location(sample_place1)

def test_remove_favourite_location(favourites_model, sample_place1, sample_place2):
    """Test removing a location from a user's favourites."""
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.set_favourite_location(sample_place2)
    assert len(favourites_model.favourites) == 2

    favourites_model.remove_favourite_location(sample_place2)
    assert len(favourites_model.favourites) == 1, f"Expected 1 location, but got {len(favourites_model.favourites)}"
    assert favourites_model.favourites[0] == sample_place1, "Expected Boston to remain"

def test_remove_favourite_location_not_in_list(favourites_model, sample_place1, sample_place2):
    """Test removing a location not in a user's favorites from a user's favorites"""
    favourites_model.set_favourite_location(sample_place1)
    assert len(favourites_model.favourites) == 1
    
    with pytest.raises(ValueError, match="Location 'New York' not found in favourites."):
      favourites_model.remove_favourite_location(sample_place2)


def test_clear_favourites(favourites_model, sample_place1):
    """Test clearing a user's favourites list"""
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.clear_favourites()
    assert len(favourites_model.favourites) == 0, "Expected empty favourites list"

def test_clear_playlist_empty_playlist(favourites_model, caplog):
    """Test clearing the entire favourites list when it's empty."""
    favourites_model.clear_favourites()
    assert len(favourites_model.favourites) == 0, "Favourites list should be empty after clearing"
    assert "Clearing an empty favourites list" in caplog.text, "Expected warning message when clearing an empty favourites list"



##################################################
#
#   Favourites Retrieval Functions Test Cases
#
##################################################

def test_get_all_favourites(favourites_model, sample_place1, sample_place2):
    """Test successfully retrieving all locations from the favourites list."""
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.set_favourite_location(sample_place2)
    all_locations = favourites_model.get_all_favourites()

    assert len(all_locations) == 2
    assert all_locations[0] == sample_place1
    assert all_locations[1] == sample_place2


def test_get_weather_by_favourite_locations(mocker, favourites_model, sample_place1):

    # Mock requests.get to return a fake response so we don't have to deal with HTTP
    mock_response = mocker.patch("requests.get")
    mock_response.return_value.status_code = 200
    mock_response.return_value.json.return_value = {
        "current": {
            "temp_c": 25.0,
            "feelslike_c": 27.0,
            "humidity": 60,
            "wind_kph": 15.0,
            "wind_dir": "NE",
            "pressure_mb": 1012,
            "precip_mm": 0.0,
            "cloud": 20,
            "condition": {"text": "Sunny"}
        }
    }

    favourites_model.set_favourite_location(sample_place1)
    result = favourites_model.get_weather_by_favourite_location(sample_place1)

    assert result.name == sample_place1
    assert result.temperature == 25.0
    assert result.condition == "Sunny"

def test_get_weather_by_favourite_location_not_in_favourites(favourites_model, mocker, sample_place1):
    """Test error when the location is not in the favourites list."""
    mock_response = mocker.patch("requests.get")
    mock_response.return_value.status_code = 200
    mock_response.return_value.json.return_value = {
        "current": {
            "temp_c": 25.0,
            "feelslike_c": 27.0,
            "humidity": 60,
            "wind_kph": 15.0,
            "wind_dir": "NE",
            "pressure_mb": 1012,
            "precip_mm": 0.0,
            "cloud": 20,
            "condition": {"text": "Sunny"}
        }
    }
    favourites_model.set_favourite_location(sample_place1)
    with pytest.raises(ValueError, match="Location 'Tokyo' not found in favourites."):
        favourites_model.get_weather_by_favourite_location("Tokyo")


def test_get_weather_by_favourite_invalid_location(favourites_model, mocker):
    """Test error when the location is invalid."""
    # Mock requests.get to return a fake response so we don't have to deal with HTTP
    mock_response = mocker.patch("requests.get")
    mock_response.return_value.status_code = 400
    mock_response.return_value.json.return_value = {
        "current": {
            "temp_c": 25.0,
            "feelslike_c": 27.0,
            "humidity": 60,
            "wind_kph": 15.0,
            "wind_dir": "NE",
            "pressure_mb": 1012,
            "precip_mm": 0.0,
            "cloud": 20,
            "condition": {"text": "Sunny"}
        }
    }

    
    with pytest.raises(ValueError, match="Invalid location name: as;ldfja;sldkjf;"):
        favourites_model.set_favourite_location("as;ldfja;sldkjf;")
        favourites_model.get_weather_by_favourite_location("as;ldfja;sldkjf;")


def test_get_weather_by_favourite_location_api_failure(mocker, favourites_model, sample_place1):
    """Test API failure when fetching weather data."""
    # Mock requests.get to raise a RequestException
    favourites_model.set_favourite_location(sample_place1)
    mocker.patch("requests.get", side_effect=Exception("Network Error"))
    with pytest.raises(Exception, match="Network Error"):
        favourites_model.get_weather_by_favourite_location(sample_place1)



def test_get_all_favourite_weathers(favourites_model, sample_place1, sample_place2, mocker):
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.set_favourite_location(sample_place2)

    mock_weather_data_1 = {
        "current": {
            "temp_c": 22.5,
            "feelslike_c": 21.0,
            "humidity": 60,
            "wind_kph": 15.0,
            "wind_dir": "N",
            "pressure_mb": 1012,
            "precip_mm": 0.0,
            "cloud": 20,
            "condition": {
                "text": "Clear"
            }
        }   
    }

    mock_weather_data_2 = {
        "current": {
            "temp_c": 18.0,
            "feelslike_c": 17.0,
            "humidity": 75,
            "wind_kph": 10.0,
            "wind_dir": "E",
            "pressure_mb": 1015,
            "precip_mm": 2.0,
            "cloud": 50,
            "condition": {
                "text": "Rainy"
            }
        }
    }

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = [mock_weather_data_1, mock_weather_data_2]  # Simulate multiple responses
    weathers = favourites_model.get_all_favourite_weathers()
            
    assert len(weathers) == 2
    assert weathers[0].name == sample_place1
    assert weathers[0].temperature == 22.5
    assert weathers[0].condition == "Clear"

    assert weathers[1].name == sample_place2
    assert weathers[1].temperature == 18.0
    assert weathers[1].condition == "Rainy"


def test_get_all_favourite_weathers_invalid_location(favourites_model, sample_place1, sample_place2, mocker):

    mock_weather_data_1 = {
        "current": {
            "temp_c": 22.5,
            "feelslike_c": 21.0,
            "humidity": 60,
            "wind_kph": 15.0,
            "wind_dir": "N",
            "pressure_mb": 1012,
            "precip_mm": 0.0,
            "cloud": 20,
            "condition": {
                "text": "Clear"
            }
        }   
    }

    mock_weather_data_2 = {
        "current": {
            "temp_c": 18.0,
            "feelslike_c": 17.0,
            "humidity": 75,
            "wind_kph": 10.0,
            "wind_dir": "E",
            "pressure_mb": 1015,
            "precip_mm": 2.0,
            "cloud": 50,
            "condition": {
                "text": "Rainy"
            }
        }
    }

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 400
    mock_get.return_value.json.side_effect = [mock_weather_data_1, mock_weather_data_2]  # Simulate multiple responses

    with pytest.raises(Exception, match="Invalid location name: aaaaaa"):
        favourites_model.set_favourite_location("aaaaaa")
        favourites_model.set_favourite_location("bbbbbb")
        favourites_model.get_all_favourite_weathers()  


def test_get_historical_weather_by_favourite_location(favourites_model, sample_place1, mocker):

    mock_historical_weather_data = {
    "forecast": {
        "forecastday": [
            {
                "date": "2022-05-01",
                "day": {
                    "mintemp_c": 10.0,
                    "maxtemp_c": 15.0,
                    "avgtemp_c": 12.5,
                    "maxwind_kph": 20.0,
                    "totalprecip_mm": 0.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 10.0,
                    "avghumidity": 60,
                    "daily_chance_of_rain": 10,
                    "daily_chance_of_snow": 1,
                    "condition": {
                        "text": "Partly Cloudy"
                    }
                }
            }
        ]
    }
    }
    date = "2022-05-01"

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_historical_weather_data  # Simulate the API JSON response

    favourites_model.set_favourite_location(sample_place1)
    historical_weather = favourites_model.get_historical_weather_by_favourite_location(sample_place1, date)

    assert historical_weather.name == sample_place1
    assert historical_weather.date == date
    assert historical_weather.min_temp == 10.0
    assert historical_weather.max_temp == 15.0
    assert historical_weather.avg_temp == 12.5
    assert historical_weather.max_wind_speed == 20.0
    assert historical_weather.total_precipitation_mm == 0.0
    assert historical_weather.total_snow_cm == 0.0
    assert historical_weather.avg_visibility == 10.0
    assert historical_weather.avg_humidity == 60
    assert historical_weather.chance_of_rain == 10
    assert historical_weather.chance_of_snow == 1
    assert historical_weather.condition == "Partly Cloudy"
        

def test_get_historical_weather_by_favourite_location_empty_favourites(favourites_model, sample_place1):
    with pytest.raises(ValueError, match="Favourites is empty"):
        favourites_model.get_historical_weather_by_favourite_location(sample_place1, "2022-05-02")

def test_get_historical_weather_by_favourite_location_invalid_date(favourites_model, sample_place1):
    favourites_model.set_favourite_location(sample_place1)
    with pytest.raises(ValueError, match="Date must be in the format of YYYY-MM-dd, got aaa"):
        favourites_model.get_historical_weather_by_favourite_location(sample_place1, "aaa")

def test_get_historical_weather_by_favourite_location_invalid_location(favourites_model, sample_place1, mocker):
    mock_historical_weather_data = {
    "forecast": {
        "forecastday": [
            {
                "date": "2022-05-01",
                "day": {
                    "mintemp_c": 10.0,
                    "maxtemp_c": 15.0,
                    "avgtemp_c": 12.5,
                    "maxwind_kph": 20.0,
                    "totalprecip_mm": 0.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 10.0,
                    "avghumidity": 60,
                    "daily_chance_of_rain": 10,
                    "daily_chance_of_snow": 1,
                    "condition": {
                        "text": "Partly Cloudy"
                    }
                }
            }
        ]
    }
    }
    date = "2022-05-01"

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 400
    mock_get.return_value.json.return_value = mock_historical_weather_data  # Simulate the API JSON response

    with pytest.raises(ValueError, match="Invalid location name: aaa"):
        favourites_model.set_favourite_location("aaa")
        favourites_model.get_historical_weather_by_favourite_location("aaa", date)

def test_get_forecast_by_favourite_location(favourites_model, sample_place2, mocker):
    mock_forecast_data = {
    "forecast": {
        "forecastday": [
            {
                "date": "2024-12-09",
                "day": {
                    "mintemp_c": 10.0,
                    "maxtemp_c": 15.0,
                    "avgtemp_c": 12.5,
                    "maxwind_kph": 20.0,
                    "totalprecip_mm": 0.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 10.0,
                    "avghumidity": 60,
                    "daily_chance_of_rain": 10,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Partly Cloudy"
                    }
                }
            },
            {
                "date": "2024-12-10",
                "day": {
                    "mintemp_c": 12.0,
                    "maxtemp_c": 18.0,
                    "avgtemp_c": 15.0,
                    "maxwind_kph": 25.0,
                    "totalprecip_mm": 5.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 8.0,
                    "avghumidity": 70,
                    "daily_chance_of_rain": 50,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Rainy"
                    }
                }
            }
        ]
    }
    }

    days = 2

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = mock_forecast_data  # Simulate the forecast JSON response
    
    favourites_model.set_favourite_location(sample_place2)
    forecast = favourites_model.get_forecast_by_favourite_location(sample_place2, days)
    
    assert len(forecast) == days

    assert forecast[0].name == sample_place2
    assert forecast[0].date == "2024-12-09"
    assert forecast[0].min_temp == 10.0
    assert forecast[0].max_temp == 15.0
    assert forecast[0].avg_temp == 12.5
    assert forecast[0].condition == "Partly Cloudy"
    
    assert forecast[1].name == sample_place2
    assert forecast[1].date == "2024-12-10"
    assert forecast[1].min_temp == 12.0
    assert forecast[1].max_temp == 18.0
    assert forecast[1].avg_temp == 15.0
    assert forecast[1].condition == "Rainy"

def test_get_forecast_by_favourite_location_empty_favourites(favourites_model, sample_place2, mocker):
    with pytest.raises(ValueError, match="Favourites is empty"):
        forecast = favourites_model.get_forecast_by_favourite_location(sample_place2, 2)

def test_get_forecast_by_favourite_location_invalid_location(favourites_model, mocker):
    mock_forecast_data = {
    "forecast": {
        "forecastday": [
            {
                "date": "2024-12-09",
                "day": {
                    "mintemp_c": 10.0,
                    "maxtemp_c": 15.0,
                    "avgtemp_c": 12.5,
                    "maxwind_kph": 20.0,
                    "totalprecip_mm": 0.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 10.0,
                    "avghumidity": 60,
                    "daily_chance_of_rain": 10,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Partly Cloudy"
                    }
                }
            },
            {
                "date": "2024-12-10",
                "day": {
                    "mintemp_c": 12.0,
                    "maxtemp_c": 18.0,
                    "avgtemp_c": 15.0,
                    "maxwind_kph": 25.0,
                    "totalprecip_mm": 5.0,
                    "totalsnow_cm": 0.0,
                    "avgvis_km": 8.0,
                    "avghumidity": 70,
                    "daily_chance_of_rain": 50,
                    "daily_chance_of_snow": 0,
                    "condition": {
                        "text": "Rainy"
                    }
                }
            }
        ]
    }
    }

    days = 2

    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 400
    mock_get.return_value.json.return_value = mock_forecast_data

    with pytest.raises(ValueError, match="Invalid location name: aaa"):
        favourites_model.set_favourite_location("aaa")
        favourites_model.get_forecast_by_favourite_location("aaa", 2)


def test_get_forecast_by_favourite_location_nonexistant_favourite(favourites_model, sample_place1, sample_place2, mocker):
    favourites_model.set_favourite_location(sample_place2)
    with pytest.raises(ValueError, match="Location 'Boston' not found in favourites"):
        forecast = favourites_model.get_forecast_by_favourite_location(sample_place1, 2)


def test_get_favourites_length(favourites_model, sample_place1, sample_place2):
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.set_favourite_location(sample_place2)
    value = favourites_model.get_favourites_length()
    assert value == 2

##################################################
#
#   Utility Functions Test Cases
#
##################################################

def test_validate_location_name(favourites_model, sample_place2, mocker):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"location": {"name": sample_place2}} 

    result = favourites_model.validate_location_name(sample_place2)
    assert result == True

def test_validate_location_name_invalid(favourites_model, mocker):
    """Test invalid location name raises ValueError."""
    location_name = "InvalidLocation"
    
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 400
    mock_get.return_value.json.return_value = {}  # Simulate empty response or invalid response
        
    with pytest.raises(ValueError, match=f"Invalid location name: {location_name}"):
        favourites_model.validate_location_name(location_name)
        

def test_check_if_empty_empty(favourites_model):
    with pytest.raises(ValueError, match="Favourites is empty"):
        favourites_model.check_if_empty()


def test_check_if_empty_NOT_empty(favourites_model, sample_place1, sample_place2):
    favourites_model.set_favourite_location(sample_place1)
    favourites_model.set_favourite_location(sample_place2)
    try:
        favourites_model.check_if_empty()
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError raised: {e}")
