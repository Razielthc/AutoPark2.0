import sqlite3
from datetime import datetime

from database.conexion import obtener_conexion


def crear_ingreso(monto: float, tipo: str, referencia_id: int, referencia_tipo: str, usuario_id: int,
                  corte: str = None) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO ingresos (monto, tipo, referencia_id, referencia_tipo, usuario_id, fecha, corte)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (monto, tipo, referencia_id, referencia_tipo, usuario_id, fecha, corte)
            )
            conexion.commit()
            return f"Ingreso creado con ID: {cursor.lastrowid}"
    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def ingresos_total_turno_actual():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ 
                    SELECT
                    COALESCE(SUM(monto), 0) AS total_por_turno
                    FROM ingresos
                    WHERE corte IS NULL
                """
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def ingresos_total_mes_actual():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT
                    COALESCE(SUM(monto), 0) AS total_por_mes
                    FROM ingresos
                    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
                """
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def ingresos_total_x_dia_mes():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT
                    strftime('%Y-%m-%d', fecha) AS dia,
                    SUM(COALESCE(monto, 0)) AS total_por_dia
                    FROM ingresos
                    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
                    GROUP BY dia;
                """
            )
            resultado = cursor.fetchall()
            return resultado  # Retorna los resultados de la consulta como una lista de tuplas [(día, total_por_dia), ...]

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def ingresos_total_x_mes_ano():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT 
                    strftime('%Y-%m', fecha) AS mes,
                    SUM(COALESCE(monto, 0)) AS total_por_mes
                    FROM ingresos
                    WHERE strftime('%Y', fecha) = strftime('%Y', 'now')
                    GROUP BY mes
                """
            )
            resultados = cursor.fetchall()
            return resultados  # Retorna los resultados de la consulta como una lista de tuplas [(mes, total_por_mes), ...]

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def marcar_ingresos_corte():
    try:
        with obtener_conexion() as conexion:

            cursor = conexion.cursor()

            # Actualizar el ticket
            cursor.execute(
                """UPDATE ingresos
                   SET corte = 'cc'
                   WHERE corte is NULL
                """)

            # Confirmar la transacción
            conexion.commit()

    except sqlite3.Error as e:
        raise e

    except Exception as e:
        raise e


def elimina_ingreso(total, referencia_tipo, referencia_id):
    """
    Elimina un registro de la tabla 'ingresos' basado en los parámetros dados.
    :param total: Total del ingreso.
    :param referencia_tipo: Tipo de referencia.
    :param referencia_id: ID de la referencia.
    :raises: sqlite3. Error o Exception en caso de error.
    """
    try:
        with obtener_conexion() as conexion:

            cursor = conexion.cursor()

            # Eliminar el registro basado en las condiciones
            cursor.execute(
                """
                DELETE FROM ingresos
                WHERE monto = ? AND referencia_tipo = ? AND referencia_id = ?
                """,
                (total, referencia_tipo, referencia_id)
            )

            # Confirmar la transacción
            conexion.commit()

    except sqlite3.Error as e:
        # Reeleva el error de SQLite con contexto adicional
        raise sqlite3.Error(f"Error al eliminar ingreso: {e}") from e

    except Exception as e:
        # Reeleva cualquier otro error
        raise Exception(f"Error inesperado: {e}") from e


if __name__ == "__main__":
    pass
