import sqlite3
from typing import List, Dict, Any

from database.conexion import obtener_conexion


def leer_tarifas() -> List[Dict[str, Any]] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM tarifas
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def tarifas_planes() -> List[Dict[str, Any]] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM tarifas
                WHERE tipo = 'pension';
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def ticket_perdido_tarifa() -> dict | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM tarifas
                WHERE nombre = 'ticket perdido'
                """
            )
            resultado = cursor.fetchone()
            return resultado
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def renovacion_tarjeta_tarifa() -> dict | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT nombre, tipo, costo
                FROM tarifas
                WHERE tipo = 'renovacion'
                """
            )
            resultado = cursor.fetchone()
            return resultado
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def eliminar_tarifa(tarifa_id: int) -> str | bool:
    try:
        with obtener_conexion() as conexion:
            conexion.execute("UPDATE usuarios SET activo = FALSE  WHERE id = ?", (tarifa_id,))
        return True  # Indica que la operación fue exitosa
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def crear_tarifa(nombre: str, tipo: str, costo: float) -> bool | str:
    try:
        with obtener_conexion() as conexion:
            conexion.execute(
                """
                INSERT INTO tarifas (nombre, tipo, costo)
                VALUES (? , ? , ?)
                """, (nombre, tipo, costo)
            )
            conexion.commit()
            return True

    except sqlite3.Error as e:
        return f"Error al guardar el registro = {e}"


def actualizar_tarifa(tarifa_id: int, nombre: str = None, costo: float = None) -> str | bool:
    try:
        campos_a_actualizar = []
        costos = []

        if nombre:
            campos_a_actualizar.append("nombre = ?")
            costos.append(nombre)

        if costo:
            campos_a_actualizar.append("costo = ?")
            costos.append(costo)

        if not campos_a_actualizar:
            return "No se proporcionó ningún dato para actualizar."

        costos.append(tarifa_id)
        query = f"UPDATE tarifas SET {', '.join(campos_a_actualizar)} WHERE id = ?"

        with obtener_conexion() as conexion:
            conexion.execute(query, costos)
            conexion.commit()
            return True
    except sqlite3.Error as e:
        return f"Error al guardar el registro = {e}"


def tarifa_default() -> dict | str:
    try:
        with obtener_conexion() as conexion:
            conexion.row_factory = sqlite3.Row
            cursor = conexion.execute(
                """SELECT *
                   FROM tarifas
                WHERE nombre = 'auto' """
            )
            # Obtener el último registro como un diccionario
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return {}
    except sqlite3.Error as e:
        raise e


if __name__ == "__main__":
    tarifas = tarifas_planes()
    for tarifa in tarifas:
        print(tarifa)
    pass
