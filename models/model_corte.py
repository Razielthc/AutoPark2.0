import sqlite3
from typing import List, Dict, Any

from database.conexion import obtener_conexion


def crear_corte(tipo: str, monto: float, fecha: str, c_salida: str, usuario_id: int) -> None | str | dict:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute("""
            INSERT INTO cortes (tipo, monto_total, fecha, c_salida, usuario_id)
            VALUES (?, ?, ?, ?, ?)
            """, (tipo, monto, fecha, c_salida, usuario_id))

            corte_id = cursor.lastrowid  # Obtener el ID del último registro insertado

            # Confirmar los cambios
            conexion.commit()
            # Recuperar el registro recién insertado
            cursor.execute("""
                            SELECT cortes.*, usuarios.name AS nombre_usuario
                            FROM cortes
                            JOIN usuarios ON cortes.usuario_id = usuarios.id
                            WHERE cortes.id = ?
                            """, (corte_id,))
            registro = cursor.fetchone()

            # Si usas row_factory, puedes convertir esto en un dict automáticamente
            return dict(registro) if registro else None
    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def leer_cortes() -> List[Dict[str, Any]] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT *
                FROM cortes
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def generar_corte():
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Consulta total ingresos, egresos y tickets
            cursor.execute(
                """
                SELECT
                (SELECT COALESCE(SUM(monto), 0) FROM ingresos WHERE corte IS NULL) AS total_ingresos,
                (SELECT COALESCE(SUM(monto), 0) FROM egresos WHERE corte IS NULL) AS total_egresos,
                (SELECT COUNT(*) FROM tickets WHERE total IS NOT NULL AND corte IS NULL) AS tickets_cobrados,
                (SELECT COUNT(*) FROM tickets WHERE total IS NULL AND corte IS NULL) AS tickets_sin_cobrar,
                (SELECT COUNT(*) FROM tickets WHERE corte IS NULL) AS total_tickets
                """
            )

            resultados_totales = cursor.fetchone()

            # Consulta resumen de ingresos por tipo
            cursor.execute(
                """
                SELECT tipo, SUM(monto) AS total_por_tipo
                FROM ingresos
                WHERE corte IS NULL
                GROUP BY tipo
                """
            )
            ingresos_por_tipo = cursor.fetchall()

            # Consulta resumen de egresos por tipo y descripción
            cursor.execute(
                """
                SELECT tipo, descripcion, SUM(monto) AS total_por_tipo
                FROM egresos
                WHERE corte IS NULL
                GROUP BY tipo, descripcion
                """
            )

            egresos_por_tipo = cursor.fetchall()

            return resultados_totales, ingresos_por_tipo, egresos_por_tipo

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {str(e)}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")


if __name__ == "__main__":
    pass
