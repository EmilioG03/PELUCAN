import os
import psycopg2
from dotenv import load_dotenv


load_dotenv()


def obtener_conexion():
    return psycopg2.connect(
        host=os.getenv("PELUCAN_DB_HOST", "localhost"),
        database=os.getenv("PELUCAN_DB_NAME", "pelucan"),
        user=os.getenv("PELUCAN_DB_USER", "postgres"),
        password=os.getenv("PELUCAN_DB_PASSWORD"),
        port=os.getenv("PELUCAN_DB_PORT", "5432")
    )
