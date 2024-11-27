import sqlite3
from datetime import datetime

from database.conexion import obtener_conexion


def crea_session(usuario_id: int):
    try:
        hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO sesiones(usuario_id, hora)
                VALUES (?, ?)
                """, (usuario_id, hora)
            )
            # Confirmar los cambios
            conexion.commit()
    except sqlite3.Error as e:
        raise


def session_activa() -> dict:
    try:
        with obtener_conexion() as conexion:
            # Configurar el row_factory para que devuelva diccionarios
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()

            cursor.execute(
                """SELECT * 
                   FROM sesiones
                   ORDER BY hora DESC
                   LIMIT 1;
                """
            )

            # Obtener el último registro como un diccionario
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return {}
    except sqlite3.Error as e:
        return {"error": f"Error al consultar la base de datos: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}


if __name__ == "__main__":
    crea_session(1)
    resultado1 = session_activa()
    print(resultado1)
