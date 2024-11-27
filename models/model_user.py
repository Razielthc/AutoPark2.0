import sqlite3
from typing import List, Dict, Any

import bcrypt

from database.conexion import obtener_conexion


def hash_password(plain_password: str) -> str:
    """Hash una contraseña en texto plano."""
    try:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    except Exception as e:
        return f"Error al generar el hash de la contraseña: {str(e)}"


def check_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano con su hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (Exception, ValueError):
        return False


def crear_usuario(nombre: str, username: str, plain_password: str, role_id: int) -> None | str:
    try:
        hashed_password = hash_password(plain_password)
        if isinstance(hashed_password, str) and "Error" in hashed_password:
            return hashed_password

        with obtener_conexion() as conexion:
            conexion.execute("""
            INSERT INTO usuarios (name, username, password, role_id)
            VALUES (?, ?, ?, ?)
            """, (nombre, username, hashed_password, role_id))
            conexion.commit()
            return True
    except sqlite3.Error as e:
        raise e
    except Exception as e:
        raise e


def leer_usuarios() -> List[Dict[str, Any]] | str:
    try:
        with obtener_conexion() as conexion:
            cursor = conexion.execute(
                """
                SELECT u.*, r.name as rol_name
                FROM usuarios u
                JOIN roles r ON u.role_id = r.id
                WHERE u.activo IS TRUE
                
                """
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def actualizar_usuario(user_id: int, nombre: str = None, username: str = None,
                       plain_password: str = None, role_id: int = None) -> str | None:
    try:
        campos_a_actualizar = []
        valores = []

        if nombre:
            campos_a_actualizar.append("name = ?")
            valores.append(nombre)

        if username:
            campos_a_actualizar.append("username = ?")
            valores.append(username)

        if plain_password:
            hashed_password = hash_password(plain_password)
            if isinstance(hashed_password, str) and "Error" in hashed_password:
                return hashed_password
            campos_a_actualizar.append("password = ?")
            valores.append(hashed_password)
        if role_id:
            campos_a_actualizar.append("role_id = ?")
            valores.append(role_id)

        if not campos_a_actualizar:
            return "No se proporcionó ningún dato para actualizar."

        valores.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(campos_a_actualizar)} WHERE id = ?"

        with obtener_conexion() as conexion:
            conexion.execute(query, valores)
        return None  # Indica que la operación fue exitosa
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def eliminar_usuario(user_id: int) -> str | None:
    try:
        with obtener_conexion() as conexion:
            conexion.execute("UPDATE usuarios SET activo = FALSE  WHERE id = ?", (user_id,))
        return None  # Indica que la operación fue exitosa
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


def verificar_credenciales(username: str, plain_password: str) -> dict | str | None:
    try:
        with obtener_conexion() as conn:
            cursor = conn.execute("""
                SELECT u.id, u.name, u.username, u.password, r.name as rol_name
                FROM usuarios u
                JOIN roles r ON u.role_id = r.id
                WHERE u.username = ?
            """, (username,))
            user = cursor.fetchone()

            if user and check_password(plain_password, user["password"]):
                # Si las credenciales son correctas, retornar los datos del usuario y el nombre del rol
                return {
                    "nombre": user["name"],
                    "rol_name": user["rol_name"],
                    "id": user["id"],
                }
            return "Usuario o contraseña incorrecta"
    except sqlite3.Error as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


if __name__ == "__main__":
    pass
