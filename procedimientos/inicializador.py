import logging
import sqlite3
from sqlite3 import Connection
from decouple import AutoConfig

from database.conexion import obtener_conexion, carga_schema
from models.model_planes import desactivar_planes_vencidos
from models.model_user import crear_usuario
from utils.get_resorce_path import resource_path
from utils.test_printer import verificar_impresora

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

# Ejemplo de uso:
config_path = resource_path('.env')
logger.warning(f"ruta{config_path}")
config = AutoConfig(config_path)

errors = []


def verificar_o_crear_db() -> bool:
    logger.debug('Inicia Funcion para Verificar base de datos')

    # Verifica si la base de datos está conectada y ejecuta el script SQL si es necesario.
    conexion = obtener_conexion()
    logger.debug('Se crea la conexion')

    if isinstance(conexion, Connection):
        logger.warning("Se carga instancia de conexion")
        try:
            sql_file = carga_schema()
            logger.warning(f"se carga la ruta del schema {sql_file}")
            cursor = conexion.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            logger.warning("se realiza la busqueda en la bd de las tablas")
            tablas = cursor.fetchall()
            # Leer el archivo .sql
            if tablas:
                logger.warning("las tablas se encuentran")
                return True
            else:

                logger.warning("tablas no encontradas")

                with open(sql_file, 'r') as file:
                    sql_script = file.read()

                logger.warning("se lee el archivo schema")
                # Ejecutar el script SQL

                with conexion:
                    conexion.executescript(sql_script)

                logger.warning("se ejecuta el schema para crear las tablas y el usuario admin")
                usuario = crear_usuario(nombre="Administrador", username="admin", plain_password="admin", role_id=1)

                if usuario is True:
                    logger.warning("Usuario y bd Creado")
                    return True

        except sqlite3.Error as e:
            errors.append(f"Error al crear las tablas {e}")
            logger.warning(f'No se pudo crear la base de datos{e}')
            return False

        finally:
            # Asegurarse de cerrar la conexión
            conexion.close()
    else:
        logger.debug('No se pudo crear la conexion')
        errors.append(conexion)


async def verificar_conexion_perifericos(device, operation_mode):
    logger.debug('Comienza funcion para verificar los perifericos')
    # Verificación de impresoras

    if config('PRINTER_SYSTEM_ENABLED', cast=bool):
        logger.warning(F"VALOR EN EL INICIALIZARDOR printer system {config('PRINTER_SYSTEM_NAME')}")
        result = await verificar_impresora(name=config('PRINTER_SYSTEM_NAME'),
                                           printer_type="printer_system")
        if result is not True:
            logger.warning(f"error al probar la impresora del sistema {result}")
            errors.append(f"Error en la impresora del sistema : {result}")

    if config('PRINTER_ENTRADA_ENABLED', cast=bool):
        logger.warning(F"VALOR EN EL INICIALIZARDOR printer entrada {config('PRINTER_ENTRADA_PORT')}")
        result = await verificar_impresora(port=config('PRINTER_ENTRADA_PORT'),
                                           printer_type="printer_entrada")
        if result is not True:
            logger.warning(f"error al probar la impresora de la entrada {result}")
            errors.append(f"Error en la impresora de la entrada : {result}")

    if config('CONTROLADOR_ENABLED', cast=bool):
        resultado = device.login()
        print("Inicio de sesión exitoso." if resultado else "Inicio de sesión fallido.")
        if resultado is not True:
            logger.warning(f"error al iniciar sesion en el controlador {resultado}")
            errors.append(f" error al iniciar sesion en el controlador : {resultado}")
        else:
            if operation_mode == "auto":
                resultado = device.attach_alarm()
                if resultado is not True:
                    logger.warning(f"error al suscribirse a los eventos  {resultado}")
                    errors.append(f" error al suscribirse a los eventos : {resultado}")

    return True if not errors else errors


def verifica_planes_vencidos():
    resultado = desactivar_planes_vencidos()
    if resultado is not True:
        logger.warning(f"error al probar la impresora del sistema {resultado}")
        errors.append(f"{resultado}")


async def inicializar_sistema(device):
    try:

        operation_mode = config('OPERATION_MODE')

        db_status = verificar_o_crear_db()

        if db_status is not True:
            logger.warning('Error al consultar o crear la base de datos')
            return f"archivo de base de datos", None

        perifericos_status = await verificar_conexion_perifericos(device, operation_mode)

        if perifericos_status is not True:
            logger.debug('Error al consultar perifericos')
            return perifericos_status, operation_mode

        verifica_planes_vencidos()

        return True, operation_mode
    except Exception as e:
        return f"error_fatal{e} ", None


# Ejemplo de uso
if __name__ == "__main__":
    pass
