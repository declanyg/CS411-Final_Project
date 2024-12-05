-- Users table
DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    salt TEXT NOT NULL,
    hashed_password TEXT NOT NULL,
    UNIQUE(username, hashed_password)
);

-- -- Locations table
-- DROP TABLE IF EXISTS Locations;
-- CREATE TABLE Locations (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     location_name TEXT NOT NULL,
--     UNIQUE(location_name)
-- );

-- -- UserLocations table
-- DROP TABLE IF EXISTS UserFavouriteLocations;
-- CREATE TABLE UserFavouriteLocations (
--     user_id INTEGER,
--     location_id INTEGER,
--     PRIMARY KEY (user_id, location_id),
--     FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
--     FOREIGN KEY (location_id) REFERENCES Locations(id) ON DELETE CASCADE
-- );