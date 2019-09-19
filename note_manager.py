"""Interfaces with the sqlite database
"""

import sqlite3
import datetime


def init_db():
    """Creates database file and schema if necessary"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    with conn:

        c.execute(
            "SELECT COUNT(*) FROM sqlite_master "
            "WHERE type='table' AND name='note_objs';")

        exists = c.fetchall()[0][0]
        current_time = datetime.datetime.now()

        if not exists:

            c.execute("""CREATE TABLE note_objs (
               id INTEGER PRIMARY KEY,
               name VARCHAR(100) NOT NULL,
               last_modified VARCHAR(100),
               data BLOB,
               parent_id INT, 
               FOREIGN KEY(parent_id) REFERENCES note_objs(id) 
               ON DELETE CASCADE
            );""")

            c.execute(f"""INSERT INTO note_objs(
            name, 
            last_modified, 
            data, 
            parent_id) 
            VALUES (
            'My Notes', 
            '{current_time}', 
            'Notebook', 
            NULL);""")


def new_obj(name, data, parent_nb, modified=str(datetime.datetime.now())):
    """Create a new note object inside the provided notebook"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    if "sqlite_" in name.lower():
        raise ValueError("sqlite_ is reserved for internal use.")

    with conn:
        c.execute(f"""INSERT INTO note_objs(
        name, 
        last_modified, 
        data, 
        parent_id) 
        VALUES (
        '{name}', 
        '{modified}', 
        '{data}', 
        '{parent_nb}');""")

    conn.commit()
    conn.close()


def update_obj(obj_id, **kwargs):
    """Updates a row with provided information"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    modified = str(datetime.datetime.now())

    # Formats the kwargs to set values in query -------------------------------

    sql_string = ''

    for column, value in kwargs.items():
        sql_string += f"{column} = '{value}', "

    # Update query ------------------------------------------------------------
    with conn:
        c.execute("UPDATE note_objs "
                  "SET " + sql_string +
                  "last_modified = '" + modified + "' "
                  "WHERE id = '" + str(obj_id) + "'")

    conn.commit()
    conn.close()


def get_row(obj_id):
    """Returns the row with the given id."""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    with conn:
        c.execute(f"SELECT * FROM note_objs WHERE id = {obj_id}")
        return c.fetchone()


def get_children(obj_id):
    """Gets the children rows of the provided row, via row ID"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    with conn:
        c.execute(f"SELECT * FROM note_objs WHERE parent_id = {obj_id}")
        children = c.fetchall()
        return children


def load():
    """Returns the entire table as list of tuples(rows)"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    with conn:
        c.execute("SELECT * FROM note_objs")

    return c.fetchall()


def delete(obj_id):
    """Delete note object"""

    # Connects to database file, if db file doesn't exist it creates one
    conn = sqlite3.connect("notes.db")
    # Cursor to execute sql commands
    c = conn.cursor()

    with conn:

        c.execute(f"DELETE FROM note_objs "
                  f"WHERE id = {obj_id}")

        # Cascade delete doesn't seem to be triggering, manually doing it:
        c.execute(f"DELETE FROM note_objs "
                  f"WHERE parent_id = {obj_id}")


init_db()  # Initialize database
