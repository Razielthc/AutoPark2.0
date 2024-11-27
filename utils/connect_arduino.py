import logging
import threading
import time
import serial
from procedimientos.crea_entrada_auto import nueva_entrada_auto
from decouple import AutoConfig
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config = AutoConfig(resource_path('.env'))


class ArduinoCommunication:
    def __init__(self, q, control):
        self.q = q
        self.control = control
        self.arduino = None
        self.lock = threading.Lock()
        self.connected = False

    def conectar(self):
        logger.debug('Inicia Funcion Conectar')
        retries = 0
        max_retries = 5

        while retries < max_retries and not self.control["done"]:
            try:

                if not config('ARDUINO_ENABLED', cast=bool):
                    self.q.put("No se pudo cargar la configuracion del PLC")
                    self.control["done"] = True
                    logger.warning('No se pudo conectar no hay configuracion')
                    return
                self.q.put("Conectando con Arduino...")
                self.arduino = serial.Serial(config('ARDUINO_PORT'), 9600, timeout=1)
                time.sleep(2)  # Espera a que Arduino se reinicie
                self.connected = True
                self.q.put("Conexión con Arduino exitosa")
                logger.debug('Conexion Exitosa')
                return
            except serial.SerialException as e:
                logger.warning(f"Error de comunicación: {str(e)}")
                self.q.put(f"Error de comunicación: {str(e)}")
                retries += 1
                time.sleep(30)  # Espera 30 segundos antes de intentar reconectar
            except Exception as e:
                logger.warning(f"Error : {str(e)}")
                self.q.put(f"Error: {str(e)}")
                return

    def recibir_mensajes(self):
        logger.debug('Inicia Funcion recibir mensajes')
        while not self.control["done"]:
            if not self.connected:
                self.conectar()
            if self.connected:
                with self.lock:
                    try:
                        if self.arduino.in_waiting > 0:
                            respuesta_arduino = self.arduino.readline().decode().strip()
                            if respuesta_arduino == "nueva entrada":
                                nueva_entrada_auto()
                                self.q.put("nueva entrada")

                    except serial.SerialException as e:

                        self.q.put(f"Error de recepción: {str(e)}")

                        self.connected = False

                    except SystemError as e:
                        self.q.put("error papel")

                    except Exception as e:
                        if not isinstance(e, SystemError):
                            self.q.put(f"Error: {str(e)}")

            time.sleep(1)

    def enviar_mensaje(self, mensaje):
        with self.lock:
            try:
                if self.connected:
                    self.arduino.write(mensaje.encode())
                else:
                    raise ConnectionError("Arduino no esta conectado")
            except serial.SerialException as e:
                self.q.put(f"Error al enviar mensaje: {str(e)}")
                self.connected = False
            except Exception as e:
                self.connected = False
                raise e

    def cerrar(self):
        with self.lock:
            if self.arduino:
                self.arduino.close()
                self.q.put("Conexión con Arduino cerrada")
                self.arduino = None

    def verificar_puerto(self, mensaje="hola arduino", respuesta_esperada="hola python", port=None):
        with self.lock:
            try:
                if self.arduino is None:
                    self.arduino = serial.Serial(port, 9600, timeout=1)

                if self.arduino.port != port:
                    self.arduino.port = port

                time.sleep(2)

                self.arduino.write((mensaje + '\n').encode())
                time.sleep(2)
                respuesta_arduino = None
                while self.arduino.in_waiting > 0:
                    try:
                        respuesta_arduino = self.arduino.readline().decode().strip()
                    except UnicodeDecodeError:
                        continue

                if respuesta_esperada in respuesta_arduino:
                    return True
                else:
                    return f"Respuesta incorrecta: {respuesta_arduino}"
            except serial.SerialTimeoutException:
                return "Tiempo de espera agotado"
            except serial.SerialException as e:
                return f"Error de comunicación: {e}"
            except Exception as e:
                return f"Error inesperado: {e}"


if __name__ == "__main__":
    pass
