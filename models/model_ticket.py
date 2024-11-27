import sqlite3

from database.conexion import obtener_conexion


class TicketNotFoundError(Exception):
    pass


def crear_ticket(hora_entrada, tarifa_name, tarifa_value, usuario_id, hora_salida=None, total=None, impreso: bool = False) -> dict | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                INSERT INTO tickets(hora_entrada,hora_salida,total, tarifa_name, tarifa_value, impreso, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (hora_entrada, hora_salida, total, tarifa_name, tarifa_value, impreso, usuario_id)
            )
            ticket_id = cursor.lastrowid  # Obtener el ID del último registro insertado

            # Confirmar los cambios
            conexion.commit()

            # Recuperar el registro recién insertado
            cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
            registro = cursor.fetchone()

            # Si usas row_factory, puedes convertir esto en un dict automáticamente
            return dict(registro) if registro else None

    except sqlite3.Error as e:
        return f"Error al consultar la base de datos: {str(e)}"


def tickets_no_impresos() -> list[dict] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT * 
                   FROM tickets
                   WHERE impreso IS FALSE;
                """
            )
            # Assuming you want to return a list of dictionaries
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return results
    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def busca_ticket(id_ticket: int) -> dict | str | None:
    try:
        with obtener_conexion() as conexion:
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()
            cursor.execute(
                """SELECT id, hora_entrada, tarifa_name, tarifa_value, total
                   FROM tickets
                   WHERE id = ?
                   AND total IS NULL
                   
                """, (id_ticket,))
            # Obtener el último registro como un diccionario
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                raise TicketNotFoundError(f"El ticket {id_ticket} ya fue cobrado")
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Error al consultar la base de datos: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")


def actualiza_ticket(id_ticket: int, hora_salida: str, total: float) -> dict:
    try:
        with obtener_conexion() as conexion:
            # Configurar el row_factory para que devuelva diccionarios
            conexion.row_factory = sqlite3.Row
            cursor = conexion.cursor()

            # Actualizar el ticket con hora de salida, total y poner corte a NULL
            cursor.execute(
                """UPDATE tickets
                   SET hora_salida = ?, total = ?, corte = NULL
                   WHERE id = ?
                """, (hora_salida, total, id_ticket))

            # Verificar si se actualizó algún registro
            if cursor.rowcount == 0:
                raise TicketNotFoundError(f"No se encontró el ticket con id {id_ticket}")

            # Confirmar la transacción
            conexion.commit()

            # Obtener el ticket actualizado
            cursor.execute(
                """SELECT * 
                   FROM tickets
                   WHERE id = ?
                """, (id_ticket,))

            # Obtener el resultado como un diccionario
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                raise TicketNotFoundError(f"No se pudo recuperar el ticket actualizado con id {id_ticket}")

    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def actualiza_impresion(ticket_id):
    try:
        with obtener_conexion() as conexion:
            # Configurar el row_factory para que devuelva diccionarios
            cursor = conexion.cursor()

            # Actualizar el ticket
            cursor.execute(
                """UPDATE tickets
                   SET impreso = 1
                   WHERE id = ?
                """, (ticket_id,))

            # Confirmar la transacción
            conexion.commit()

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Error al consultar la base de datos: {str(e)}")

    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")


def marcar_ticket_corte():
    try:
        with obtener_conexion() as conexion:

            cursor = conexion.cursor()

            # Actualizar el ticket
            cursor.execute(
                """UPDATE tickets
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
