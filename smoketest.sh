#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5001/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Password Storage
#
##########################################################

clear_users() {
  echo "Clearing users..."
  curl -s -X DELETE "$BASE_URL/clear-users" | grep -q '"status": "success"'
}

login() {
  username=$1
  password=$2

  echo "Logging into user $username with password $password..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  echo $response | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "User login successful."
  else
    echo "Failed to login user."
    echo "Response: $response"
    exit 1
  fi
}

create_account() {
  username=$1
  password=$2

  echo "Creating user ($username: $password)..."
  response=$(curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  echo $response | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    echo "Response: $response"
    exit 1
  fi
}

update_password() {
  username=$1
  password=$2

  echo "Updating user password ($username: $password)..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  echo $response | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "User password updated successfully."
  else
    echo "Failed to update user password."
    echo "Response: $response"
    exit 1
  fi
}

set_favourite_location() {
  username=$1
  location=$2

  echo "Adding location to favourites: $username - $location..."
  response=$(curl -s -X POST "$BASE_URL/set_favourite_location" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"location\":\"$location\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location added to favourites successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Favourites JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add location to favourites."
    echo "Response: $response"
    exit 1
  fi
}

remove_favourite_location() {
  username=$1
  location=$2

  echo "Removing location from favourites: $username - $location..."
  response=$(curl -s -X POST "$BASE_URL/remove_favourite_location" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"location\":\"$location\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location removed from favourites successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Favourites JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to remove location from favourites."
    echo "Response: $response" 
    exit 1
  fi
}

clear_favourites() {
  username=$1

  echo "Clearing favourites for $username..."
  response=$(curl -s -X POST "$BASE_URL/clear-favourites" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "favourites cleared successfully."
  else
    echo "Failed to clear favourites."
    echo "Response: $response" 
    exit 1
  fi
}

##########################################################
#
# Favourite Weather Retrieval
#
##########################################################

get_all_favourite_locations() {
  username=$1

  echo "Getting favourite locations for $username..."
  response=$(curl -s -X GET "$BASE_URL/get-all-favourites/$username")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Favourites retrieved successfully for $username."
    if [ "$ECHO_JSON" = true ]; then
      echo "Favourites JSON ($username):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get favourites for $username."
    exit 1
  fi
}

get_weather_by_favourite_location() {
  username=$1
  location=$2

  echo "Getting favourite location weather: $username - $location..."
  response=$(curl -s -X GET "$BASE_URL/get_weather_by_favourite_location/$username/$location")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather retrieved successfully for $location."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON ($location):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weather for $location."
    echo "Response: $response" 
    exit 1
  fi
}

get_all_favourite_weathers() {
  username=$1

  echo "Getting the weather for all favourite locations: $username..."
  response=$(curl -s -X GET "$BASE_URL/get_all_favourite_weathers/$username")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weathers retrieved successfully for $username."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weathers JSON ($username):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weathers for $username."
    echo "Response: $response" 
    exit 1
  fi
}

get_all_favourite_weathers() {
  username=$1

  echo "Getting the weather for all favourite locations: $username..."
  response=$(curl -s -X GET "$BASE_URL/get_all_favourite_weathers/$username")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weathers retrieved successfully for $username."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weathers JSON ($username):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get weathers for $username."
    echo "Response: $response" 
    exit 1
  fi
}

get_historical_weather_by_favourite_location() {
  username=$1
  favourite_location=$2
  date=$3

  echo "Getting the historical weather date for the favourite location: $location..."
  response=$(curl -s -X GET "$BASE_URL/get_historical_weather_by_favourite_location/$username/$favourite_location/$date")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Historical weather data retrieved successfully for $favourite_location."
    if [ "$ECHO_JSON" = true ]; then
      echo "Historical weather JSON ($favourite_location - $date):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get historical weather for $favourite_location on $date."
    echo "Response: $response" 
    exit 1
  fi
}

get_forecast_by_favourite_location() {
  username=$1
  favourite_location=$2
  days=$3

  echo "Getting the historical weather date for the favourite location: $location..."
  response=$(curl -s -X GET "$BASE_URL/get_forecast_by_favourite_location/$username/$favourite_location/$days")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Forecasted weather data for the next $days days retrieved successfully for $favourite_location."
    if [ "$ECHO_JSON" = true ]; then
      echo "Forecasted weather JSON ($favourite_location - $date):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get forecasted weather for the next $days days for $favourite_location."
    echo "Response: $response" 
    exit 1
  fi
}

get_favourites_length() {
  username =$1

  echo "Retrieving favourites length for $username..."
  response=$(curl -s -X GET "$BASE_URL/get_favourites_length/$username")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Favourites length retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Favourites Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve favourites length."
    exit 1
  fi
}

# Health checks
check_health
check_db

# Clear users
clear_users

#User tests
create_account "Bob" "1234"
login "Bob" "1234"

create_account "Jeffery" "1005mflmae"
login "Jeffery" "1005mflmae"
update_password "Jeffery" "Golbus411"
login "Jeffery" "Golbus411"

#Favourites Model tests
set_favourite_location "Bob" "Hong Kong"
set_favourite_location "Bob" "Boston"
set_favourite_location "Bob" "London"
remove_favourite_location "Bob" "Hong Kong"
set_favourite_location "Jeffery" "Boston"
set_favourite_location "Jeffery" "Honolulu"
clear_favourites "Bob"

#Favourite Weather Retreival tests
get_all_favourite_locations "Jeffery"

get_weather_by_favourite_location "Jeffery" "Honolulu"
get_all_favourite_weathers "Jeffery"
get_historical_weather_by_favourite_location "Jeffery" "Honolulu" "2024-12-01"
get_forecast_by_favourite_location "Jeffery" "Honolulu" 5
get_favourites_length "Jeffery"

clear_favourites "Jeffery"
get_favourites_length "Jeffery"

echo "All tests passed successfully!"
