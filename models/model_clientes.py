from contextlib import closing
from datetime import datetime
import sqlite3

from database.conexion import obtener_conexion
from utils.get_resorce_path import resource_path


def crear_cliente(nombre: str, documento: str, folio_documento: str, email: str, telefono: str, direccion: str,
                  placa: str, modelo: str, usuario_id: int):
    try:
        fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with obtener_conexion() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre, documento, folio_documento, email, telefono, direccion, placa, modelo,
                                      fecha_registro, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, documento, folio_documento, email, telefono, direccion, placa, modelo, fecha_registro,
                  usuario_id))
            conexion.commit()

            # Obtener el ID del último registro insertado
            cliente_id = cursor.lastrowid

            # # Consultar el registro completo
            # cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
            # cliente_creado = cursor.fetchone()

            return cliente_id

    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def leer_clientes(pagina: int, registros_por_pagina: int, filtro: str = None):
    try:
        with obtener_conexion() as conexion:
            offset = (pagina - 1) * registros_por_pagina

            if filtro:
                query = """
                    SELECT 
                        c.id AS cliente_id,
                        c.nombre AS nombre_cliente,
                        c.folio_documento,
                        c.email,
                        c.telefono,
                        pc.tarifa_duracion,
                        pc.fecha_inicio,
                        pc.fecha_fin,
                        pc.activo AS plan_activo,
                        tc.id AS tarjeta_id,
                        tc.numero_tarjeta,
                        (SELECT COUNT(*) 
                         FROM clientes c 
                         WHERE c.activo = 1 AND (c.nombre LIKE ? OR c.email LIKE ? OR c.folio_documento LIKE ?)) AS total
                    FROM 
                        clientes c
                    LEFT JOIN 
                        planes_contratados pc ON c.id = pc.cliente_id AND pc.activo = 1
                    LEFT JOIN 
                        tarjetas_cliente tc ON c.id = tc.cliente_id AND tc.activo = 1
                    WHERE 
                        c.activo = 1 AND (c.nombre LIKE ? OR c.email LIKE ? OR c.folio_documento LIKE ?)
                    ORDER BY 
                        c.nombre
                    LIMIT ? OFFSET ?
                """
                valores = (
                    f"%{filtro}%", f"%{filtro}%", f"%{filtro}%",  # Para el conteo total
                    f"%{filtro}%", f"%{filtro}%", f"%{filtro}%",  # Para el filtro de clientes
                    registros_por_pagina, offset
                )
            else:
                query = """
                    SELECT 
                        c.id AS cliente_id,
                        c.nombre AS nombre_cliente,
                        c.folio_documento,
                        c.email,
                        c.telefono,
                        pc.tarifa_duracion,
                        pc.fecha_inicio,
                        pc.fecha_fin,
                        pc.activo AS plan_activo,
                        tc.id AS tarjeta_id,
                        tc.numero_tarjeta,
                        tc.tarjeta_hex,
                        (SELECT COUNT(*) 
                         FROM clientes c 
                         WHERE c.activo = 1) AS total
                    FROM 
                        clientes c
                    LEFT JOIN 
                        planes_contratados pc ON c.id = pc.cliente_id AND pc.activo = 1
                    LEFT JOIN 
                        tarjetas_cliente tc ON c.id = tc.cliente_id AND tc.activo = 1
                    WHERE 
                        c.activo = 1
                    ORDER BY 
                        c.nombre
                    LIMIT ? OFFSET ?
                """
                valores = (registros_por_pagina, offset)

            cursor = conexion.execute(query, valores)
            resultados = cursor.fetchall()

            # Convertir resultados en una lista de diccionarios
            clientes = [dict(zip([col[0] for col in cursor.description], row)) for row in resultados]

            # Extraer el total desde la primera fila
            total = resultados[0]["total"] if resultados else 0

            return clientes, total

    except sqlite3.Error as e:
        print(f"Error al leer clientes: {e}")
        return [], 0


def busca_cliente(cliente_id: int):
    try:
        with obtener_conexion() as conexion:
            query = """
                SELECT id, nombre, email, telefono
                FROM clientes 
                WHERE activo = 1 AND id = ?
            """
            with closing(conexion.execute(query, (cliente_id,))) as cursor:
                cliente = cursor.fetchone()  # Obtener solo el primer resultado
                if cliente:
                    # Convertir el resultado a un diccionario
                    return dict(zip([col[0] for col in cursor.description], cliente))
            return None
    except sqlite3.Error as e:
        print(f"Error al buscar clientes: {e}")
        return None


def actualizar_cliente(cliente_id: int, usuario_id: int, nombre: str = None, documento: str = None,
                       folio_documento: str = None, email: str = None, telefono: str = None, direccion: str = None,
                       placa: str = None, modelo: str = None):
    try:
        fecha_actualizacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        campos_a_actualizar = []
        valores = []

        # Campos opcionales
        if nombre:
            campos_a_actualizar.append("nombre = ?")
            valores.append(nombre)

        if documento:
            campos_a_actualizar.append("documento = ?")
            valores.append(documento)

        if folio_documento:
            campos_a_actualizar.append("folio_documento = ?")
            valores.append(folio_documento)

        if email:
            campos_a_actualizar.append("email = ?")
            valores.append(email)

        if telefono:
            campos_a_actualizar.append("telefono = ?")
            valores.append(telefono)

        if direccion:
            campos_a_actualizar.append("direccion = ?")
            valores.append(direccion)

        if placa:
            campos_a_actualizar.append("placa = ?")
            valores.append(placa)

        if modelo:
            campos_a_actualizar.append("modelo = ?")
            valores.append(modelo)

        if not campos_a_actualizar:
            raise ValueError("No se proporcionó ningún dato para actualizar")

        campos_a_actualizar.append("fecha_actualizacion = ?")
        valores.append(fecha_actualizacion)
        campos_a_actualizar.append("usuario_id = ?")
        valores.append(usuario_id)

        valores.append(cliente_id)
        query = f"UPDATE clientes SET {', '.join(campos_a_actualizar)} WHERE id = ?"

        with obtener_conexion() as conexion:
            conexion.execute(query, valores)

    except sqlite3.Error as e:
        raise f"Error en la base de datos: {str(e)}"
    except Exception as e:
        raise f"Error inesperado: {str(e)}"


def soft_elimina_cliente(cliente_id: int):
    try:
        with obtener_conexion() as conexion:
            # Desactivar cliente
            conexion.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (cliente_id,))

            # Desactivar planes asociados
            conexion.execute("UPDATE planes_contratados SET activo = 0 WHERE cliente_id = ?", (cliente_id,))

            # Desactivar tarjetas asociadas
            conexion.execute("UPDATE tarjetas_cliente SET activo = 0 WHERE cliente_id = ?", (cliente_id,))

    except sqlite3.Error as e:
        raise Exception(f"Error en la base de datos: {str(e)}")
    except Exception as e:
        raise Exception(f"Error inesperado: {str(e)}")


def elimina_cliente(cliente_id: int) -> bool:
    try:
        with obtener_conexion() as conexion:
            conexion.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
            return True
    except sqlite3.Error as e:
        raise f"Error en la base de datos: {str(e)}"
    except Exception as e:
        raise f"Error inesperado: {str(e)}"


def crear_clientes_falsos():
    try:
        sql_file = resource_path('database/factory_faker.sql')

        with open(sql_file, 'r') as file:
            sql_script = file.read()

        with obtener_conexion() as conexion:
            conexion.executescript(sql_script)

    except sqlite3.Error as e:
        raise f"Error en la base de datos: {str(e)}"
    except Exception as e:
        raise f"Error inesperado: {str(e)}"


if __name__ == "__main__":
    pass
