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

echo "All tests passed successfully!"
