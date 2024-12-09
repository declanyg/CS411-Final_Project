# CS411-Final_Project: Weather Dashboard Application

This application is a weather dashboard application. It is based on the weather dashboard application example given. It is a web-based application that is designed to provide users with easy access to weather information. Users can set favourite locations, and easily view their current, forecasted (up to 10 days in the future), and historical weather data. Weather data is pulled from [Weather API] (https://www.weatherapi.com).

# Healthcheck Routes

## Route
`/health`

## Request Type
**GET**

## Purpose
Verify's the service is running.

## Request Parameters
None.

## Successful Response Format
- Code: 200
- Content: { "status": "healthy" }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/api/health"
```

### Example Repsonse
```json
{
  "status": "healthy"
}
```

## Route
`/db-check`

## Request Type
**GET**

## Purpose
Check if the database connection and Users table are functional

## Request Parameters
None.

## Successful Response Format
- Code: 200
- Content: { "database_status": "healthy" }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/api/db-check"
```

### Example Repsonse
```json
{
  "database_status": "healthy",
  "status": 200
}
```


# User Routes

## Route
`/login`

## Request Type
**POST**

## Purpose
Login to an existing user with a username and password.

## Request Body
- **username** (String): User's chosen username.
- **password** (String): User's chosen password.

## Successful Response Format
- Code: 200
- Content: { "status": "success", "username": username }

### Example Request
```json
{
  "username": "newuser123",
  "password": "securepassword"
}
```
### Example Response
```json
{
  "status": "success",
  "username": "newuser123"
}
```

## Route
`/create-account`

## Request Type
**POST**

## Purpose
Creates a new user account with a username and password.

## Request Body
- **username** (String): User's chosen username.
- **password** (String): User's chosen password.

## Successful Response Format
- Code: 200
- Content: { "status": "success", "username": username }

### Example Request
```json
{
  "username": "newuser123",
  "password": "securepassword"
}
```
### Example Response
```json
{
  "status": "success",
  "username": "newuser123"
}
```

## Route
`/update-password`

## Request Type
**POST**

## Purpose
Updates a user account's password given a username and password.

## Request Body
- **username** (String): User's chosen username.
- **password** (String): User's chosen password.

## Successful Response Format
- Code: 200
- Content: { "status": "success", "username": username }

### Example Request
```json
{
  "username": "newuser123",
  "password": "securepassword"
}
```
### Example Response
```json
{
  "status": "success",
  "username": "newuser123"
}
```

## Route
`/clear-users`

## Request Type
**DELETE**

## Purpose
Clears all the users in Users table (recreates the table)

## Request Body
None.

## Successful Response Format
- Code: 200
- Content: { "status": "success" }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/api/clear-users"
```

### Example Response
```json
{
  "status": "success"
}
```


# Favourite Weather Management Routes

## Route
`/set_favourite_location`

## Request Type
**POST**

## Purpose
Sets a location as a user's favourite.

## Request Body
- **username** (String): User's chosen username.
- **location** (String): The location to add to favourites.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'Location added to favourites', 'favourites': List[str] }

### Example Request
```json
{
  "username": "newuser123",
  "location": "Boston"
}
```
### Example Response
```json
{
  "status": "success",
  "message": "Location added to favourites",
  "favourites": ["Boston"]
}
```

## Route
`/remove_favourite_location`

## Request Type
**POST**

## Purpose
Removes a location from a user's favourites.

## Request Body
- **username** (String): User's chosen username.
- **location** (String): The location to remove from favourites.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'Location removed from favourites', "favourites": List[str] }

### Example Request
```json
{
  "username": "newuser123",
  "location": "Boston"
}
```
### Example Response
```json
{
  "status": "success",
  "message": "Location removed from favourites",
  "favourites": []
}
```

## Route
`/clear_favourites`

## Request Type
**POST**

## Purpose
Clears a user's favourites.

## Request Body
- **username** (String): User's chosen username.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'Favourites cleared' }

### Example Request
```json
{
  "username": "newuser123"
}
```
### Example Response
```json
{
  "status": "success",
  "message": "Favourites cleared",
}
```


# Favourite Weather Retrieval

## Route
`/get-all-favourites/<string:username>`

## Request Type
**GET**

## Purpose
Retrieve a user's list of favourited locations.

## Request Parameters
- **username** (String): User's chosen username.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'favourited_locations': List[str] }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get-all-favourites/newuser123"
```

### Example Response
```json
{
  "status": "success",
  "favourited_locations": ["Boston", "Hong Kong"],
}
```

## Route
`/get_weather_by_favourite_location/<string:username>/<string:location>`

## Request Type
**GET**

## Purpose
Retrieve a user's favourite location's weather.

## Request Parameters
- **username** (String): User's chosen username.
- **location** (String): The location to retrieve the weather of

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'weather retrieved successfully', 'weather': CurrentWeather }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get_weather_by_favourite_location/newuser123/Boston"
```

### Example Response
```json
{
  "status": "success",
  "message": "weather retrieved successfully",
  "weather": {
    "cloud": 100,
    "condition": "Overcast",
    "feels_like": 4.1,
    "humidity": 60,
    "name": "Boston",
    "precipitation": 0,
    "pressure_mb": 1012,
    "temperature": 7.2,
    "wind_direction": "W",
    "wind_speed": 17.6
  }
}
```

## Route
`/get_all_favourite_weathers/<string:username>`

## Request Type
**GET**

## Purpose
Retrieve the weather for all of a user's favourited locations.

## Request Parameters
- **username** (String): User's chosen username.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'weathers retrieved successfully', 'weathers': List[CurrentWeather] }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get_all_favourite_weathers/newuser123"
```

### Example Response
```json
{
  "status": "success",
  "message": "weathers retrieved successfully",
  "weathers": [
    {
      "cloud": 100,
      "condition": "Overcast",
      "feels_like": 4.1,
      "humidity": 60,
      "name": "Boston",
      "precipitation": 0,
      "pressure_mb": 1012,
      "temperature": 7.2,
      "wind_direction": "W",
      "wind_speed": 17.6
    },
    {
      "cloud": 50,
      "condition": "Partly cloudy",
      "feels_like": 6.5,
      "humidity": 47,
      "name": "New York",
      "precipitation": 0,
      "pressure_mb": 1014,
      "temperature": 8.9,
      "wind_direction": "WNW",
      "wind_speed": 15.5
    }
  ]
}
```

## Route
`/get_historical_weather_by_favourite_location/<string:username>/<string:favourite_location>/<string:date>`

## Request Type
**GET**

## Purpose
Retrieve the historical weather data for a user's favourite location on a particular date.

## Request Parameters
- **username** (String): User's chosen username.
- **favourite_location** (String): The name of the favourite location
- **date** (String): The date to retrieve the weather of (in the format of YYYY-MM-dd)

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': f'Historical weather data retrieved for date {date} successfully', 'date': String, 'historicalWeatherData': WeatherData }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get_historical_weather_by_favourite_location/newuser123/Boston/2024-12-07"
```

### Example Response
```json
{
  "status": "success",
  "message": "Historical weather data retrieved for date 2024-12-07 successfully",
  "date": "2024-12-07",
  "historicalWeatherData": {
    "avg_humidity": 68,
    "avg_temp": -0.1,
    "avg_visibility": 10,
    "chance_of_rain": 0,
    "chance_of_snow": 0,
    "condition": "Partly cloudy",
    "date": "2024-12-07",
    "max_temp": 4.1,
    "max_wind_speed": 16.2,
    "min_temp": -3.2,
    "name": "Boston",
    "total_precipitation_mm": 0,
    "total_snow_cm": 0
  },
}
```

## Route
`/get_forecast_by_favourite_location/<string:username>/<string:favourite_location>/<int:days>`

## Request Type
**GET**

## Purpose
Retrieve the forecast for the next upcoming days for a favourite location.

## Request Parameters
- **username** (String): User's chosen username.
- **favourite_location** (String): The name of the favourite location
- **date** (String): The number of upcoming days to retrieve (up to 10)

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': f'Weather for the upcoming {days} day(s) retrieved successfully', 'forecastedWeatherData': List[WeatherData] }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get_historical_weather_by_favourite_location/newuser123/Boston/3"
```

### Example Response
```json
{
  "status": "success",
  "message": "Weather for the upcoming 3 day(s) retrieved successfully",
  "forecastedWeatherData": [
    {
      "avg_humidity": 78,
      "avg_temp": 3.8,
      "avg_visibility": 8.7,
      "chance_of_rain": 0,
      "chance_of_snow": 0,
      "condition": "Overcast ",
      "date": "2024-12-08",
      "max_temp": 9.3,
      "max_wind_speed": 24.5,
      "min_temp": -0.6,
      "name": "Boston",
      "total_precipitation_mm": 0,
      "total_snow_cm": 0
    },
    {
      "avg_humidity": 87,
      "avg_temp": 3.3,
      "avg_visibility": 9.3,
      "chance_of_rain": 86,
      "chance_of_snow": 86,
      "condition": "Moderate rain",
      "date": "2024-12-09",
      "max_temp": 4.3,
      "max_wind_speed": 15.8,
      "min_temp": 1.3,
      "name": "Boston",
      "total_precipitation_mm": 17.82,
      "total_snow_cm": 0
    },
    {
      "avg_humidity": 98,
      "avg_temp": 5,
      "avg_visibility": 4.7,
      "chance_of_rain": 86,
      "chance_of_snow": 86,
      "condition": "Heavy rain",
      "date": "2024-12-10",
      "max_temp": 5.1,
      "max_wind_speed": 14.8,
      "min_temp": 3.7,
      "name": "Boston",
      "total_precipitation_mm": 21.23,
      "total_snow_cm": 0
    }
  ],
}
```

## Route
`/get_favourites_length/<string:username>`

## Request Type
**GET**

## Purpose
Retrieve the number of favourite locations a user has.

## Request Parameters
- **username** (String): User's chosen username.

## Successful Response Format
- Code: 200
- Content: { 'status': 'success', 'message': 'favourites length retrieved successfully', 'favourites_length': int }

### Example Request
```bash
curl -s -X GET "http://localhost:5001/get_favourites_length/newuser123"
```

### Example Response
```json
{
  "status": "success",
  "message": "favourites length retrieved successfully",
  "favourites_length": 3
}
```