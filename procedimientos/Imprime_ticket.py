from escpos.exceptions import DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError, ConfigSyntaxError, \
    ConfigSectionMissingError
from escpos.capabilities import NotSupported
from escpos.printer import Network, Win32Raw
import logging
from decouple import AutoConfig
from models.model_datos import leer_datos
from models.model_tarifas import ticket_perdido_tarifa
from models.model_ticket import actualiza_impresion
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)
config = AutoConfig(resource_path('.env'))


def obtener_impresora(reimpresion):
    try:

        if reimpresion:
            if config('PRINTER_SYSTEM_ENABLED', cast=bool):
                return Win32Raw(config('PRINTER_SYSTEM_NAME'), profile="TM-T20II")
            else:
                raise (ConfigNotFoundError, NotSupported)
        else:
            if config('OPERATION_MODE') == "auto":
                logger.warning(
                    f"valor printer Entrada Enabled en auto {config('PRINTER_ENTRADA_ENABLED')} config('PRINTER_ENTRADA_PORT')")
                if config('PRINTER_ENTRADA_ENABLED', cast=bool):
                    printer = Network(config('PRINTER_ENTRADA_PORT'), profile="TM-T20II")
                    status = printer.query_status(b'\x10\x04\x04')

                    # Convertir la respuesta de bytes a un entero
                    status_int = int.from_bytes(status, 'big')

                    # Enmascarar y extraer los bits 5 y 6
                    # Desplazamos 5 lugares a la derecha para llevar los bits 5 y 6 a la posición 0 y 1
                    # Luego hacemos una operación AND (&) con 0b11 (que es 3 en decimal) para quedarnos con esos 2 bits
                    paper_status = (status_int >> 5) & 0b11

                    # Evaluar el estado del papel
                    if paper_status == 0:  # Ambos bits 5 y 6 son 0
                        return printer
                    else:
                        raise SystemError("No hay papel en la impresora del dispensador de tickets")

                else:
                    raise ValueError("Error al cargar la configuracion de la impresora del dispensador")
            else:

                if config('PRINTER_SYSTEM_ENABLED', cast=bool):
                    return Win32Raw(config('PRINTER_SYSTEM_NAME'))
                else:
                    raise (ConfigNotFoundError, NotSupported)
    except (KeyError, DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError, ConfigSyntaxError,
            ConfigSectionMissingError, NotSupported) as e:
        raise e


def imprime_ticket(ticket, reimpresion=False):
    try:
        # Cargar configuraciones
        estacionamiento = leer_datos()
        ticket_perdido = ticket_perdido_tarifa()

        # Obtener la impresora
        p = obtener_impresora(reimpresion)

        # Configuración del ticket
        p.set(align='center', bold=True, double_height=True, double_width=True)
        p.textln(f"{estacionamiento['nombre']}")
        p.ln()
        p.set(align='left', bold=False, normal_textsize=True)
        p.textln(f"Direccion: {estacionamiento['direccion']}")
        p.textln(f"Telefono: {estacionamiento['telefono']} Horario : {estacionamiento['horario']}")
        p.ln()
        p.qr(content=f"{ticket['id']}#{ticket['hora_entrada']}", center=True, size=10)
        p.ln()
        p.textln(f"Ticket: {ticket['id']} Entrada : {ticket['hora_entrada']} tarifa: {ticket['tarifa_value']} X Hora ")
        p.set(bold=True)
        p.ln()
        p.textln(f"**** Costo de boleto perdido $ {ticket_perdido['costo']} ****")
        p.textln(f"El estacionamiento se obliga a prestar el\n"
                 f"servicio en los términos del reglamento en\n"
                 f"materia haciéndonos responsables únicamente\n"
                 f"por robo total o incendio del vehículo.\n"
                 f"No respondemos por robos parciales, daños\n"
                 f"causados por terceros, ni objetos dejados en\n"
                 f"los vehículos, así como fallas mecánicas o\n"
                 f"eléctricas, si no es bajo previo inventario\n"
                 f"o aviso por escrito. En caso de robo total\n"
                 f"respondemos hasta per el monto máximo incluido\n"
                 f"en la póliza correspondiente al estacionamiento.\n"
                 f"La salida del vehículo será únicamente con\n"
                 f"la entrega del presente boleto y pago de la\n"
                 f"tarifa correspondiente. No procederá\n"
                 f"reclamación posterior, la tarifa incluye IVA")

        p.cut()
        p.ln(5)
        p.close()
        actualiza_impresion(ticket['id'])
        logger.debug(f"Se imprime nuevo ticket")
    except (DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError, ConfigSyntaxError,
            ConfigSectionMissingError, NotSupported) as e:
        logger.warning(f"No se pudo conectar a la impresora {e}")
        raise e
    except ValueError as e:
        logger.warning(f"Impresora no configurada {e}")
        raise e
    except SystemError as e:
        logger.warning(f"Impresora de entrada sin papel {e}")
        raise e
    except Exception as e:
        logger.warning(f"Error {e}")
        raise e


if __name__ == "__main__":
    p = obtener_impresora(reimpresion=True)
    p.cut()
    pass
