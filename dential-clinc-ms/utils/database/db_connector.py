import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from utils.logger import log_message 
import os
from dotenv import load_dotenv


def get_db_config():
        load_dotenv()
        config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "3306"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "dental_db")
        }

        return config


def get_db_connection(config):
    """Establishes and returns a MySQL connection."""
    config = get_db_config()
    print("Attempting connection with config:", config)  # Debug print

    try:
        # Correct way - unpack the dictionary with **
        connection = mysql.connector.connect(**config)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Connected to MySQL server version {db_info}")
            return connection
            
    except Error as e:
        if e.errno == 1045:  # Access denied
            print(f"❌ Access denied for user '{config['user']}'. Check credentials.")
        elif e.errno == 1049:  # Unknown database
            print(f"❌ Database '{config['database']}' doesn't exist.")
        else:
            print(f"❌ MySQL Error [{e.errno}]: {e.msg}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None