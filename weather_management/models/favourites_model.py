import logging
import requests
from datetime import datetime
from typing import List
from Final_Project.weather_management.models.user_model import User
from Final_Project.weather_management.models.WeatherData_model import WeatherData
from Final_Project.weather_management.models.CurrentWeather_model import CurrentWeather
from weather_management.utils.logger import configure_logger
# from weather_management.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)


class FavouritesModel:
    """
    A class to manage the favourite weather locations for a user.

    Attributes:
        username (str): The current user's username.
        favourites (List[str]): The list of locations.
        base_url (str): The base url used for requests to the API
        api_key (str): The api key for WeatherAPI.com
    """

    def __init__(self, username, api_key):
        """
        Initializes the FavouritesModel with the user set to a User object with the username set to the given username, and an empty favourite location list.
        """
        self.username: str = username
        self.favourites: List[str] = []
        self.base_url: str = "http://api.weatherapi.com/v1"
        self.api_key: str = api_key

    ##################################################
    # Favourite Location Management Functions
    ##################################################

    def set_favourite_location(self, location: str) -> None:
        """
        Adds a location to a user's favourite locations list.

        Args:
            locations (str): The location to add to favourite locations.

        Raises:
            ValueError: If the location is already added or the location name is invalid.
        """
        logger.info("Adding location to favourite location list: %s", location)
        if location in self.favourites:
            logger.error("Location with name %s already exists in favourites", location)
            raise ValueError(f"Location with name {location} already exists in favourites")
        success = self.validate_location_name(location)
        if success:
            self.favourites.append(location)
            logger.info("Location %d has been added", location)

    def remove_favourite_location(self, location: str) -> None:
        """
        Removes a location from the favourites by its name.

        Args:
            location (str): The name of the location to remove from favourites.

        Raises:
            ValueError: If favourites is empty or the location doesn't exist.
        """
        logger.info("Removing location %s from favourites", location)
        self.check_if_empty()
        try:
            self.favourites.remove(location)
            logger.info("Location with name %s has been removed", location)
        except ValueError:
            logger.error("Location with name %s doesn't exist in favourites", location)
            raise ValueError(f"Location '{location}' not found in favourites.")

    def clear_favourites(self) -> None:
        """
        Clears all favourite locations. If favourites is already empty, logs a warning.
        """
        logger.info("Clearing favourites")
        if self.get_favourites_length() == 0:
            logger.warning("Clearing an empty favourites list")
        self.favourites.clear()

    ##################################################
    # Favourites Retrieval Functions
    ##################################################

    def get_all_favourites(self) -> List[str]:
        """
        Returns a list of all locations in the favourites.
        """
        self.check_if_empty()
        logger.info("Getting all favourited locations")
        return self.favourites

    def get_weather_by_favourite_location(self, favourite_location: str) -> CurrentWeather:
        """
        Retrieves the weather for a favourite location by its name.

        Args:
            favourite_location (str): The name of the favourite location to retrieve.

        Raises:
            ValueError: If favourites is empty, the location is not found.
            requests.exceptions.RequestException: If the API call raises an erorr.
        """
        self.check_if_empty()
        #Checking if in favourites as all favourited locations should be valid (only added to list when valid)
        #This aims to minimize API calls.
        if favourite_location in self.favourites: 
            logger.info("Getting weather for location %s from favourites", favourite_location)

            params = {
            "key": self.api_key,
            "q": favourite_location
            }

            try:
                response = requests.get(self.base_url+'/current.json', params=params)
                if response.status_code == 200:
                    weather = CurrentWeather(
                        name=favourite_location, 
                        temperature=response["current"]["temp_c"], 
                        feels_like=response["current"]["feelslike_c"],
                        humidity=response["current"]["humidity"],
                        wind_speed=response["current"]["wind_kph"],
                        wind_direction=response["current"]["wind_dir"],
                        pressure_mb=response["current"]["pressure_mb"],
                        precipitation=response["current"]["precip_mm"],
                        cloud=response["current"]["cloud"],
                        condition=response["current"]["condition"]["text"],
                    )
                    logger.info("Location %s weather successfully fetched", favourite_location)
                    return weather
                else:
                    logger.error("Invalid location name %s", favourite_location)
                    raise ValueError(f"Invalid location name: {favourite_location}")
            except requests.exceptions.RequestException as e:
                logger.error("Request error while making API call: %s", str(e))
                raise e
        else:
            logger.error("Location with name %s doesn't exist in favourites", favourite_location)
            raise ValueError(f"Location '{favourite_location}' not found in favourites.")

    def get_all_favourite_weathers(self) -> List[CurrentWeather]:
        """
        Retrieves the weathers for each of the user's favourite locations.

        Raises:
            ValueError: If favourites is empty.
            requests.exceptions.RequestException: If the API call raises an erorr.
        """
        self.check_if_empty()
        weathers = []
        logger.info("Getting all weathers from favourites")
        for location in self.favourites:
            params = {
            "key": self.api_key,
            "q": location
            }

            try:
                response = requests.get(self.base_url+'/current.json', params=params)
                if response.status_code == 200:
                    weather = CurrentWeather(
                        name=location, 
                        temperature=response["current"]["temp_c"], 
                        feels_like=response["current"]["feelslike_c"],
                        humidity=response["current"]["humidity"],
                        wind_speed=response["current"]["wind_kph"],
                        wind_direction=response["current"]["wind_dir"],
                        pressure_mb=response["current"]["pressure_mb"],
                        precipitation=response["current"]["precip_mm"],
                        cloud=response["current"]["cloud"],
                        condition=response["current"]["condition"]["text"],
                    )
                    logger.info("Location %s weather successfully fetched", location)
                    weathers.append(weather)
                else:
                    logger.error("Invalid location name %s", location)
                    raise ValueError(f"Invalid location name: {location}")
            except requests.exceptions.RequestException as e:
                logger.error("Request error while making API call: %s", str(e))
                raise e
        return weathers
    
    def get_historical_weather_by_favourite_location(self, favourite_location: str, date: str) -> WeatherData:
        """
        Retrieves the historical weather data for the past couple days for a favourite location.

        Args:
            favourite_location (str): The name of the favourite location to retrieve.
            date (str): The date to retrieve the weather of (in the format of YYYY-MM-dd)
        Raises:
            ValueError: If favourites is empty, is not found or date is invalid.
            requests.exceptions.RequestException: If the API call raises an erorr.
        """
        self.check_if_empty()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Days must be in the format of YYYY-MM-dd, got {date}")
        
        #Checking if in favourites as all favourited locations should be valid (only added to list when valid)
        #This aims to minimize API calls.
        if favourite_location in self.favourites: 
            logger.info("Getting historical weather data for location %s from favourites", favourite_location)

            params = {
            "key": self.api_key,
            "q": favourite_location,
            "dt": date
            }
            
            try:
                response = requests.get(self.base_url+'/history.json', params=params)
                if response.status_code == 200:
                    day = response["forecast"]["forecastday"][0]
                    historical_data = WeatherData(
                        name=favourite_location,
                        date=day["date"],
                        min_temp=day["day"]["mintemp_c"],
                        max_temp=day["day"]["maxtemp_c"],
                        avg_temp=day["day"]["avgtemp_c"],
                        max_wind_speed=day["day"]["maxwind_kph"],
                        total_precipitation_mm=day["day"]["totalprecip_mm"],
                        total_snow_cm=day["day"]["totalsnow_cm"],
                        avg_visibility=day["day"]["avgvis_km"],
                        avg_humidity=day["day"]["avghumidity"],
                        chance_of_rain=day["day"]["daily_chance_of_rain"],
                        chance_of_snow=day["day"]["daily_chance_of_rain"],
                        condition=day["day"]["condition"]["text"]
                    )
                    logger.info("Location %s historical data on day %s successfully fetched", favourite_location, date)
                    return historical_data
                else:
                    logger.error("Invalid location name %s", favourite_location)
                    raise ValueError(f"Invalid location name: {favourite_location}")
            except requests.exceptions.RequestException as e:
                logger.error("Request error while making API call: %s", str(e))
                raise e
        else:
            logger.error("Location with name %s doesn't exist in favourites", favourite_location)
            raise ValueError(f"Location '{favourite_location}' not found in favourites.")

    def get_forecast_by_favourite_location(self, favourite_location: str, days: int) -> List[WeatherData]:
        """
        Retrieves the forecast for the next upcoming days for a favourite location.

        Args:
            favourite_location (str): The name of the favourite location to retrieve.
            days (int): The number of upcoming days to retrieve (up to 10)
        Raises:
            ValueError: If favourites is empty, the location is not found or days is invalid.
            requests.exceptions.RequestException: If the API call raises an erorr.
        """
        self.check_if_empty()
        if not (days > 0 and days <= 10):
            raise ValueError(f"Days must be greater than 0 and less than 10, got {days}")
        #Checking if in favourites as all favourited locations should be valid (only added to list when valid)
        #This aims to minimize API calls.
        if favourite_location in self.favourites: 
            logger.info("Getting forecast for location %s from favourites", favourite_location)

            params = {
            "key": self.api_key,
            "q": favourite_location,
            "days": str(days),
            "api": "no",
            "alerts": "no"
            }
            
            forecasts = []
            try:
                response = requests.get(self.base_url+'/forecast.json', params=params)
                if response.status_code == 200:
                    for day in response["forecast"]["forecastday"]:
                        forecasts.append(WeatherData(
                            name=favourite_location,
                            date=day["date"],
                            min_temp=day["day"]["mintemp_c"],
                            max_temp=day["day"]["maxtemp_c"],
                            avg_temp=day["day"]["avgtemp_c"],
                            max_wind_speed=day["day"]["maxwind_kph"],
                            total_precipitation_mm=day["day"]["totalprecip_mm"],
                            total_snow_cm=day["day"]["totalsnow_cm"],
                            avg_visibility=day["day"]["avgvis_km"],
                            avg_humidity=day["day"]["avghumidity"],
                            chance_of_rain=day["day"]["daily_chance_of_rain"],
                            chance_of_snow=day["day"]["daily_chance_of_rain"],
                            condition=day["day"]["condition"]["text"]
                        ))
                    logger.info("Location %s forecast for the next %s days successfully fetched", favourite_location, days)
                    return forecasts
                else:
                    logger.error("Invalid location name %s", favourite_location)
                    raise ValueError(f"Invalid location name: {favourite_location}")
            except requests.exceptions.RequestException as e:
                logger.error("Request error while making API call: %s", str(e))
                raise e
        else:
            logger.error("Location with name %s doesn't exist in favourites", favourite_location)
            raise ValueError(f"Location '{favourite_location}' not found in favourites.")

    def get_favourites_length(self) -> int:
        """
        Returns the number of favourite locations.
        """
        return len(self.favourites)

    ##################################################
    # Utility Functions
    ##################################################

    def validate_location_name(self, location_name: str) -> bool:
        """
        Validates the given location, ensuring it is a valid location supported by the API.

        Args:
            location_name (str): The location name to validate.

        Raises:
            ValueError: If a location name is not a valid location supported by the API.
            requests.exceptions.RequestException: If the API call raises an erorr.
        """
        
        params = {
            "key": self.api_key,
            "q": location_name
        }
        try:
            response = requests.get(self.base_url+'/timezone.json', params=params)
            if response.status_code == 200:
                return True
            else:
                logger.error("Invalid location name %s", location_name)
                raise ValueError(f"Invalid location name: {location_name}")
        except requests.exceptions.RequestException as e:
            logger.error("Request error while making API call: %s", str(e))
            raise e
    
    def check_if_empty(self) -> None:
        """
        Checks if the favourites list is empty, logs an error, and raises a ValueError if it is.

        Raises:
            ValueError: If the favourites location list is empty.
        """
        if not self.favourites:
            logger.error("Favourites is empty")
            raise ValueError("Favourites is empty")
