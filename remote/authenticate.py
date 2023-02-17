"""Used for authenticating the user"""


import sqlite3

import hash
import datetime


class AuthenticationError(Exception):
    pass


class BadArgument(AuthenticationError):
    pass


class InvalidPasswordError(AuthenticationError):
    pass


class UserNotExistError(AuthenticationError):
    pass


class SessionNotExistError(AuthenticationError):
    pass


def auth_session(session_ID, connection):
    """Authenticates that a session exists and returns the users UserID

    Arguments:
        session_ID: str
            -- The ID of the session
        connection: sqlite3.Connection
            -- The connection to the database

    Returns:
        user_ID: str
            -- The ID of the user who made this session

    Raises:
        SessionNotExistError:
            It raises this exception if no session has been found with that ID
    """

    query = """
    SELECT UserID
    FROM UserSessions
    WHERE SessionID = ?;
    """

    # Execute the query and get the first result (Session ID is unique so there
    # should not be more than one)
    cursor = connection.execute(query, (session_ID,))
    user_ID = cursor.fetchone()

    # result is None only if there is no case where the WHERE clause is valid,
    # so there must not be any session with that ID
    if user_ID is None:
        raise SessionNotExistError(f"No session with ID {session_ID}")

    return user_ID[0]


def auth_username_password(username, password, connection):
    """Authorises the user based on their username and password.

    Arguments:
        username: str
            -- The username
        password: str
            -- The password
        connection: sqlite3.Connection
            -- A connection to the database

    Raises:
        UserNotExistError:
            It raises this if no user has that username
        InvalidPasswordError:
            It raises this if the password does not match what is stored

    Returns:
        user_ID: str
            -- The UserID of the user

    """

    # Get the user ID
    user_ID = get_user_ID(username, connection)

    query = """
    SELECT PasswordHash, Salt
    FROM Users
    WHERE UserID = ?;
    """

    # Execute the query and get the value
    cursor = connection.execute(query, (user_ID,))

    # As user_ID is already known to be a user, there should be no error here
    password_hash, salt = cursor.fetchone()

    if password_hash == hash_password(password, salt):
        return user_ID
    else:
        raise InvalidPasswordError(f"Password is invalid as hashes " +
                                   f"{password_hash} and " +
                                   f"{hash_password(password, salt)} " +
                                   f"don't match")


def create_session(user_ID, connection):
    """Creates a new session for a given user.

    Arguments:
        user_ID: str
            -- The user's UserID
        connection: sqlite3.Connection
            -- The connection to the database

    Raises:
        UserNotExistError:
            It raises this when there is a sqlite3.IntegrityError as that must
            mean that the UserID is invalid and so fails the foreign key
            restraint

    Returns:
        session_ID: str
            -- The ID of the session
        expires: str
            -- The expiry date of the session in the format %Y-%m-%d %H:%M:%S

    """

    # Get the seed for the session ID
    seed = hash.gen_seed()
    session_ID = hash.get_random_hex(seed, 16)

    # Get the date and time when the session expires
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    expires = expires.strftime("%Y-%m-%d %H:%M:%S")

    query = """
    INSERT INTO UserSessions (UserID, SessionID, Expires)
    VALUES (?, ?, ?);
    """
    try:
        connection.execute(query, (user_ID, session_ID, expires))
    except sqlite3.IntegrityError:
        # This should only be reached if there is an integrity error due to the
        # user ID being invalid

        # It may also be reached if the session ID is not unique, but the
        # chance of that happening is so low that it can be ignored
        raise UserNotExistError(f"No user with ID {user_ID} found")

    return session_ID, expires


def create_user(username, password, connection):
    """Creates a new user with a given username and password.

    Arguments:
        username: str
            -- The user's username
        password: str
            -- The user's password
        connection: sqlite3.Connection
            -- A connection to the database

    Returns:
        user_ID: str
            -- The user's user ID
    """
    seed = hash.gen_seed()
    salt = hash.get_random_hex(seed, 16)
    password_hash = hash_password(password, salt)
    seed = hash.gen_seed()
    user_ID = hash.get_random_hex(seed, 16)
    query = """
    INSERT INTO Users (UserID, Username, PasswordHash, Salt)
    VALUES (?, ?, ?, ?);
    """

    connection.execute(query, (user_ID, username, password_hash, salt))

    return user_ID


def hash_password(password, salt):
    """Hashes the password

    Arguments:
        password: str
            -- The password to hash
        salt: str
            -- The salt

    Returns:
        password_hash: str
            -- The hashed password
    """
    result = salt + password
    return hash.hash_(result)


def get_user_ID(username, connection):
    """Get the User ID from the username

    Arguments:
        username: str
            -- The user's username
        connection: sqlite3.Connection
            -- The connection to the database

    Raises:
        UserNotExistError:
            -- It raises this when no user with the given username is found

    Returns:
        user_ID:
            -- The user's user ID

    """
    query = """
    SELECT UserID
    FROM Users
    WHERE Username = ?;
    """
    cursor = connection.execute(query, (username,))
    user_ID = cursor.fetchone()
    if user_ID is None:
        raise UserNotExistError(f"User {username} does not exist")
    return user_ID[0]