import hash
import os
import authenticate

def get_all_files(user_id, conn):
    query = """
    SELECT FilePath, FileName, Description
    FROM Files
    WHERE UserID = ?
    ORDER BY FileName ASC;
    """
    cursor = conn.execute(query, (user_id,))
    return cursor.fetchall()


def get_particular_file(filepath, user_ID, conn):
    query = """
    SELECT FileName, Description
    FROM Files
    WHERE FilePath = ? AND UserID = ?;
    """
    cursor = conn.execute(query, (filepath, user_ID))
    return cursor.fetchone()


def create_file(user_ID, filename, description, conn):
    seed = hash.gen_seed()
    filepath = hash.get_random_hex(seed, 8)
    query = """
    INSERT INTO Files (FilePath, UserID, FileName, Description)
    VALUES (?, ?, ?, ?);
    """
    conn.execute(query, (filepath, user_ID, filename, description))

    return filepath


def read_file(filepath, user_ID, conn):
    content = ""
    query = """
    SELECT 1
    FROM Files
    WHERE Filepath = ? AND UserID = ?
    """

    cursor = conn.execute(query, (filepath, user_ID))
    if cursor.fetchone() is None:
        return None

    with open(os.path.join('./data', filepath), "r") as f:
        content = f.read()

    return content


def update_file(filepath, user_ID, filename, description, content, conn):
    query = """
    UPDATE Files 
    SET FileName = ?, Description = ?
    WHERE FilePath = ? AND UserID = ?
    """
    conn.execute(query, (filename, description, filepath, user_ID))
    with open(os.path.join('./data', filepath), "w") as f:
        f.write(content)
