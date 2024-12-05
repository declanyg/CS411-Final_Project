from dataclasses import dataclass
import logging

from weather_management.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

#Data is in metric units
@dataclass
class WeatherData:
    name: str
    date: str
    min_temp: float
    max_temp: float
    avg_temp: float
    max_wind_speed: float  
    total_precipitation_mm: float
    total_snow_cm: float
    avg_visibility: float
    avg_humidity: int
    chance_of_rain: int
    chance_of_snow: int
    condition: str
