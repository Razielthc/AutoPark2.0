import time
import logging
import serial

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


async def verificar_puerto_arduino(port):
    try:
        logger.info('Comienza funcion para probar arduino')
        arduino = serial.Serial(port, 9600, timeout=1)
        time.sleep(2)  # Espera a que Arduino se reinicie

        arduino.write(("hola arduino" + '\n').encode())  # Envía el mensaje
        logger.debug('Se envia el mensaje a arduino')
        time.sleep(1)

        respuesta_arduino = None
        while arduino.in_waiting > 0:
            try:
                respuesta_arduino = arduino.readline().decode().strip()
            except UnicodeDecodeError:
                continue

        arduino.close()

        if "hola python" in respuesta_arduino:
            logger.debug('Communication con arduino exitosa')
            return True
        else:
            return f"Respuesta incorrecta: {respuesta_arduino}"
    except serial.SerialTimeoutException as e:
        logger.debug(f'Error en la conexion {e}')
        return "Tiempo de espera agotado"
    except serial.SerialException as e:
        logger.debug(f'Error en la conexion {e}')
        return f"Error al abrir el puerto serie: {e}"
    except Exception as e:
        logger.debug(f'Error en la conexion {e}')
        return f"Error inesperado: {e}"


if __name__ == "__main__":
    pass
