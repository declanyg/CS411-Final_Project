from dataclasses import dataclass
import logging

from weather_management.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)

#Data is in metric units
@dataclass
class Weather:
    name: str
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    wind_direction: str
    pressure_mb: float
    precipitation: float
    cloud: int #as percentage
    condition: str