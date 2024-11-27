import sqlite3
from typing import List, Dict, Any

from database.conexion import obtener_conexion


def leer_roles() -> List[Dict[str, Any]] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM roles
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


if __name__ == "__main__":
    pass
