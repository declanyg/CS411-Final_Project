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

######################################################
#
#    Favourite Location Management Functions Test Cases
#
######################################################

def test_set_favourite_location_success():
    """Test adding a location to a user's favourites."""
    favourites_model = FavouritesModel(username="Bob", api_key=os.getenv("API_KEY"))
    favourites_model.set_favourite_location("Boston")
    assert len(favourites_model.favourites) == 1
    assert favourites_model.favourites[0] == 'Boston'

