"""Creates the tables for the database"""

import sqlite3

# The name of the database
DATABASE_NAME = "./database/storage.db"

# Make sure that foreign keys are enabled
PRAGMA = "PRAGMA foreign_keys = ON;"

# The query to create the tables.
CREATE_TABLES_QUERY = """
DROP TABLE IF EXISTS Files;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS UserSessions;

CREATE TABLE Users (
   UserID CHAR(16) PRIMARY KEY CHECK (UserID NOT GLOB '*[^0-9a-f]*'),
   Username VARCHAR(32) UNIQUE,
   PasswordHash CHAR(64) NOT NULL CHECK (PasswordHash NOT GLOB '*[^0-9a-f]*'),
   Salt CHAR(32) NOT NULL CHECK (Salt NOT GLOB '*[^0-9a-f]*')
);

CREATE TABLE UserSessions(
   SessionID CHAR(16) PRIMARY KEY CHECK (SessionID NOT GLOB '*[^0-9a-f]*'),
   UserID CHAR(16) NOT NULL CHECK (UserID NOT GLOB '*[^0-9a-f]*'),
   Expires CHAR(19) NOT NULL CHECK (Expires GLOB '20[2-9][0-9]-[01][0-9]-[0-3][0-9] [01][0-9]:[0-5][0-9]:[0-5][0-9]' AND Expires > DATETIME()),
   FOREIGN KEY (UserID) REFERENCES Users (UserID) ON DELETE CASCADE
);

CREATE TABLE Files (
   FilePath CHAR(16) PRIMARY KEY CHECK (FilePath NOT GLOB '*[^0-9a-f]*'),
   UserID CHAR(16) NOT NULL CHECK (UserID NOT GLOB '*[^0-9a-f]*'),
   FileName VARCHAR(64) NOT NULL,
   Description VARCHAR(256) NOT NULL,
   FOREIGN KEY (UserID) REFERENCES Users (UserID) ON DELETE RESTRICT
);
"""

if __name__ == '__main__':
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()
    cursor.execute(PRAGMA)
    cursor.executescript(CREATE_TABLES_QUERY)