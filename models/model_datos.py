import sqlite3
from typing import Dict, Any

from database.conexion import obtener_conexion


def leer_datos() -> Dict[str, Any] | str | None:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM datos 
                """
            )
            row = cursor.fetchone()
            if row:
                return dict(row)  # Retorna un diccionario si se encuentra una fila
            else:
                return None
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def actualizar_datos(nombre: str, direccion: str, telefono: str, horario: str) -> str | bool:
    try:
        with obtener_conexion() as conexion:
            conexion.execute(
                """
                UPDATE datos
                SET nombre = ?, direccion = ?, telefono = ?, horario = ?
                WHERE id = 1
                """,
                (nombre, direccion, telefono, horario)
            )
            conexion.commit()
            return True
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


# Ejemplo de uso
if __name__ == "__main__":
    pass
