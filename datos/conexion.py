import os

import psycopg

CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
    "dbname": os.getenv("PGDATABASE", "pelucan"),
    "connect_timeout": 3, 
}


def conectar():
    """Devuelve una conexión abierta a la base de datos."""
    return psycopg.connect(**CONFIG)
