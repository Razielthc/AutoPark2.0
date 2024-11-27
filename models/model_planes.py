import sqlite3
from datetime import datetime
from database.conexion import obtener_conexion


def crear_plan(cliente_id: int, tarifa_costo, tarifa_duracion, fecha_inicio: str,
               fecha_fin: str, usuario_id: int):
    """
    Crea un plan contratado en la base de datos y retorna su ID.
    :param cliente_id: ID del cliente.
    :param tarifa_costo: Costo de la tarifa.
    :param tarifa_duracion: Duración de la tarifa (semanal, mensual, etc.).
    :param fecha_inicio: Fecha de inicio del plan.
    :param fecha_fin: Fecha de fin del plan.
    :param usuario_id: ID del usuario que registra el plan.
    :return: ID del plan recién creado o None si falla.
    """
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO planes_contratados (cliente_id, tarifa_costo, tarifa_duracion, fecha_inicio, fecha_fin, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (cliente_id, tarifa_costo, tarifa_duracion, fecha_inicio, fecha_fin, usuario_id)
            )
            conexion.commit()
            return cursor.lastrowid  # Retorna el ID del último registro insertado

    except sqlite3.Error as e:
        raise e


def elimina_plan(plan_id: int) -> bool:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                    DELETE FROM planes_contratados WHERE id = ?;
                    """, (plan_id,)
            )
            conexion.commit()
            return True  # Retorna el ID del último registro insertado

    except sqlite3.Error as e:
        raise e


def desactivar_planes_vencidos() -> str | bool:
    """Busca planes cuya fecha_fin sea igual a la fecha actual y cambia su estado de activo a 0."""
    try:
        # Conexión a la base de datos
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()

            # Obtener la fecha actual en formato YYYY-MM-DD
            fecha_actual = datetime.now().strftime("%Y-%m-%d")

            # Query para actualizar los planes vencidos
            query_actualizar = """
                UPDATE planes_contratados
                SET activo = 0
                WHERE fecha_fin = ? AND activo = 1
            """
            cursor.execute(query_actualizar, (fecha_actual,))

            # Confirmar cambios
            conexion.commit()

            return True
    except sqlite3.Error as e:
        return f"Error al desactivar los planes {e} "


if __name__ == "__main__":
    pass
