import sqlite3
from datetime import datetime
from database.conexion import obtener_conexion


def crear_egreso(monto: float, tipo: str, descripcion: str, usuario_id: int) -> str:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO egresos (monto, tipo, descripcion, usuario_id, fecha)
                VALUES (?, ?, ?, ?, ?)
                """,
                (monto, tipo, descripcion, usuario_id, fecha)
            )
            conexion.commit()
            return f"Ingreso creado con ID: {cursor.lastrowid}"
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def egresos_total_turno_actual():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT
                    SUM(COALESCE(monto, 0)) AS total_por_turno
                    FROM egresos
                    WHERE corte IS NULL
                """
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def egresos_total_mes_actual():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ 
                    SELECT
                    COALESCE(SUM(monto), 0) AS total_por_mes
                    FROM egresos
                    WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
                """
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0

    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def egresos_total_x_dia_mes():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT
                    strftime('%Y-%m-%d', fecha) AS dia,
                    SUM(COALESCE(monto, 0)) AS total_por_dia
                    FROM egresos
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


def egresos_total_x_mes_ano():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """ SELECT 
                    strftime('%Y-%m', fecha) AS mes,
                    SUM(COALESCE(monto, 0)) AS total_por_mes
                    FROM egresos
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


def marcar_egresos_corte():
    try:
        with obtener_conexion() as conexion:

            cursor = conexion.cursor()

            # Actualizar el ticket
            cursor.execute(
                """UPDATE egresos
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
