from datetime import datetime
import sqlite3

from database.conexion import obtener_conexion


def crear_tarjeta(cliente_id: int, numero_tarjeta, tarjeta_hex, usuario_id: int):
    """
    Crea un plan contratado en la base de datos y retorna su ID.
    :param cliente_id: ID del cliente.
    :param numero_tarjeta
    :param tarjeta_hex
    :param usuario_id: ID del usuario que registra el plan.
    :return: ID del plan recién creado o None si falla.
    """
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:

        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO tarjetas_cliente (cliente_id, numero_tarjeta, tarjeta_hex, fecha, usuario_id)
                VALUES (?, ?, ?, ?, ?)
                """, (cliente_id, numero_tarjeta, tarjeta_hex, fecha, usuario_id)
            )
            conexion.commit()
            return cursor.lastrowid  # Retorna el ID del último registro insertado

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: tarjetas_cliente.numero_tarjeta" in str(e):
            raise sqlite3.IntegrityError("Error: El número de tarjeta ya está registrado.") from e
        else:
            raise  # Reelevar otros errores de integridad

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Error de base de datos: {str(e)}") from e


def desactiva_tarjeta(tarjeta_id: int) -> bool:
    """
    Desactiva una tarjeta cambiando su estado `activo` a 0 (False) en la base de datos.

    Args:
        tarjeta_id (int): ID de la tarjeta a desactivar.

    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                UPDATE tarjetas_cliente 
                SET activo = 0
                WHERE id = ?
                """, (tarjeta_id,)
            )
            conexion.commit()
            return cursor.rowcount > 0  # True si se actualizó al menos una fila

    except sqlite3.Error as e:
        # Registrar o manejar el error si es necesario
        raise e


def elimina_tarjeta(tarjeta_id: int) -> bool:
    """
    Elimina permanentemente una tarjeta de la base de datos.

    Args:
        tarjeta_id (int): ID de la tarjeta a eliminar.

    Returns:
        bool: True si la operación fue exitosa (se eliminó una fila), False en caso contrario.
    """
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                DELETE FROM tarjetas_cliente 
                WHERE id = ?
                """, (tarjeta_id,)
            )
            conexion.commit()
            return cursor.rowcount > 0  # True si se eliminó al menos una fila

    except sqlite3.Error as e:
        # Registrar el error antes de lanzarlo (opcional)
        print(f"Error al eliminar tarjeta con ID {tarjeta_id}: {e}")
        raise e


if __name__ == "__main__":
    pass
