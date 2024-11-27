import logging
import sqlite3
from sqlite3 import Connection
from decouple import AutoConfig
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config_path = resource_path('.env')
config = AutoConfig(config_path)
logging.warning(f"ruta mail_setting {config_path}")


def obtener_conexion() -> Connection | str:
    logger.debug("se llama a la conexion de base de datos")

    try:
        # Establece y devuelve una conexión a la base de datos SQLite.
        db_name = resource_path(f'./database/{config("DATABASE")}')
        conexion = sqlite3.connect(db_name)
        conexion.row_factory = sqlite3.Row

        # Habilitar las claves foráneas en la conexión
        conexion.execute("PRAGMA foreign_keys = ON;")
        logger.debug("Claves foráneas habilitadas y conexión realizada")

        return conexion

    except (sqlite3.Error, ValueError) as e:
        logger.warning(f"Error al conectar con base de datos {e}")
        return f"Error {e}"


def carga_schema():
    return resource_path('database/schema.sql')


if __name__ == "__main__":
    pass
