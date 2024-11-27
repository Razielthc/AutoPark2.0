from escpos.exceptions import DeviceNotFoundError, USBNotFoundError
from escpos.printer import Win32Raw
import logging
from decouple import AutoConfig
from utils.get_resorce_path import resource_path
from models.model_datos import leer_datos

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config = AutoConfig(resource_path('.env'))


def obtener_impresora():
    try:

        if config('PRINTER_SYSTEM_ENABLED', cast=bool):
            return Win32Raw(config('PRINTER_SYSTEM_NAME'), profile="TM-T20II")
        else:
            raise ValueError("Impresora no configurada")

    except KeyError as e:
        raise ValueError(f"Error en la configuración de impresora: {e}")

    except Exception as e:
        raise e


def imprime_recibo(ticket, cambio):
    try:
        # Cargar configuraciones
        estacionamiento = leer_datos()
        if estacionamiento['recibo_pago']:

            # Obtener la impresora
            p = obtener_impresora()

            # Configuración del ticket
            p.set(align='center', bold=True, double_height=True, double_width=True)
            p.textln(f"{estacionamiento['nombre']}")
            p.set(align='left', bold=False, normal_textsize=True)
            p.textln(f"Direccion: {estacionamiento['direccion']}")
            p.textln(f"Telefono: {estacionamiento['telefono']} Horario : {estacionamiento['horario']}")
            p.ln()
            if ticket['tarifa_name'] == "ticket perdido":
                p.set(bold=True)
                p.textln(f"Ticket perdido tarifa: {ticket['tarifa_value']} ")
            else:
                p.textln(f"Ticket: {ticket['id']}, tarifa: {ticket['tarifa_value']} X Hora")
                p.textln(f"Entrada : {ticket['hora_entrada']} Salida: {ticket['hora_salida']}")

            p.set(bold=True)
            p.textln(f"Total : {ticket['total']} Cambio {cambio}")
            p.textln(f"Este no es un comprobante fiscal, Agradecemos"
                     f"su preferencia si tiene alguna sugerencia o queja"
                     f"favor de comunicarse al numero {estacionamiento['telefono']}")
            p.cut()
            p.close()
        else:
            pass
    except (DeviceNotFoundError, USBNotFoundError) as e:
        raise DeviceNotFoundError(e)
    except ValueError as e:
        raise ValueError(e)
    except Exception as e:
        raise Exception(e)
