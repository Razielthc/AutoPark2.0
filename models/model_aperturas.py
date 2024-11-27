import sqlite3
from datetime import datetime

from database.conexion import obtener_conexion


def crear_apertura(door_name: str, metodo_entrada: str,
                   card_number: str = "", card_status: str = "", error_code: str = "",
                   fecha: str = "", usuario_id: int = ""):
    try:
        with obtener_conexion() as conexion:
            conexion.execute("""
            INSERT INTO aperturas (door_name, metodo_entrada, 
                                   card_number, card_status, error_code, fecha, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (door_name, metodo_entrada,
                  card_number, card_status, error_code, fecha, usuario_id))
            conexion.commit()
    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def autos_dentro() -> int | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
              SELECT
              (COALESCE(COUNT(*) FILTER (WHERE door_name = 'Entrada'), 0) - 
               COALESCE(COUNT(*) FILTER (WHERE door_name = 'Salida'), 0)) AS autos
              FROM
              aperturas;
                """
            )
            resultado = cursor.fetchone()
            return resultado[0]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"
    finally:
        conexion.close()


def aperturas_del_turno() -> list[dict]:
    conexion = None  # Inicializar la variable para evitar problemas si falla antes de asignar la conexión
    try:
        conexion = obtener_conexion()
        cursor = conexion.execute(
            """
            SELECT door_name, metodo_entrada, COUNT(*) AS total
            FROM aperturas
            WHERE corte IS NULL
            GROUP BY door_name, metodo_entrada;
            """
        )

        # Obtener los nombres de las columnas
        columns = [column[0] for column in cursor.description]

        # Convertir cada fila en un diccionario
        resultado = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return resultado  # Devuelve una lista de diccionarios

    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e
    finally:
        if conexion:
            conexion.close()


def marcar_aperturas_corte():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Actualizar el ticket
            cursor.execute(
                """UPDATE aperturas
                   SET corte = 'cc'
                   WHERE corte is NULL
                """)

            # Confirmar la transacción
            conexion.commit()

    except sqlite3.Error as e:
        raise e

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
