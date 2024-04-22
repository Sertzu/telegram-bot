import sqlite3
import pickle

def create_connection(db_file):
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLite connection is open")
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn):
    """Create a table to store user contexts."""
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_context (
                user_id TEXT PRIMARY KEY,
                context BLOB
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def save_context(conn, user_id, context):
    """Save the context array for a specific user."""
    try:
        c = conn.cursor()
        # Pickle the context to convert it into a binary format
        blob_data = pickle.dumps(context)
        c.execute('''
            INSERT INTO user_context (user_id, context) VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET context = excluded.context;
        ''', (user_id, sqlite3.Binary(blob_data)))
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def get_context(conn, user_id):
    """Retrieve the context array for a specific user, deserializing it with pickle."""
    try:
        c = conn.cursor()
        c.execute('SELECT context FROM user_context WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        if result:
            # Unpickle the blob back to a Python object (list of ints)
            return pickle.loads(result[0])
        return None
    except sqlite3.Error as e:
        print(e)
        return None

def delete_context(conn, user_id):
    """Delete the context for a specific user from the database."""
    try:
        c = conn.cursor()
        c.execute('DELETE FROM user_context WHERE user_id = ?', (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(e)