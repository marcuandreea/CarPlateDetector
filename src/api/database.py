import os
from contextlib import contextmanager

import psycopg2

# Citeste setarile de conexiune la baza de date
DB_CONFIG = {
    "database": os.getenv("PARKING_DB_NAME", "parkingDB"),
    "host": os.getenv("PARKING_DB_HOST", "localhost"),
    "user": os.getenv("PARKING_DB_USER", "postgres"),
    "password": os.getenv("PARKING_DB_PASSWORD", "1234"),
    "port": os.getenv("PARKING_DB_PORT", "1234"),
}


def get_connection():
    #Returneaza o conexiune PostgreSQL folosind aceleasi setari ca aplicatia Python
    return psycopg2.connect(**DB_CONFIG)


# Context manager pentru a gestiona conexiunile la baza de date
@contextmanager
def connection_scope():
    connection = None
    try:
        connection = get_connection()
        yield connection
    finally:
        if connection is not None:
            connection.close()
