from escpos.exceptions import (
    DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError,
    ConfigSyntaxError, ConfigSectionMissingError
)
import logging
from decouple import AutoConfig

from models.model_clientes import busca_cliente
from utils.get_resorce_path import resource_path
from models.model_datos import leer_datos
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from escpos.printer import Win32Raw
import os
import subprocess

# Configuración del logger
logger = logging.getLogger(__name__)
config = AutoConfig(resource_path('.env'))


def obtener_impresora():
    try:
        # Verificar si el sistema de impresión está habilitado
        if config("PRINTER_SYSTEM_ENABLED", cast=bool):
            printer_name = config("PRINTER_SYSTEM_NAME")

            if printer_name.upper() == "MICROSOFT PRINT TO PDF":
                logger.info("Usando 'Microsoft Print to PDF' para generar un archivo PDF.")
                return "MICROSOFT_PRINT_TO_PDF"

            logger.info(f"Usando impresora configurada: {printer_name}")
            return Win32Raw(printer_name, profile="TM-T20II")  # Devuelve la impresora configurada

        else:
            raise ValueError("Impresora no configurada o sistema de impresión deshabilitado.")

    except KeyError as e:
        raise ValueError(f"Error en la configuración de impresora: {e}")
    except Exception as e:
        raise e


def generar_pdf(datos_cliente, datos_plan=None, datos_tarjeta=None, filename=None, cambio=None):
    """Genera un archivo PDF con los datos proporcionados, ajustándose dinámicamente al contenido."""
    estacionamiento = leer_datos()
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Márgenes y posición inicial
    margen_superior = 800
    margen_inferior = 50
    x_inicial = 50
    y_actual = margen_superior

    def agregar_texto(texto, font="Helvetica", size=11, bold=False, salto=20):
        """Función auxiliar para agregar texto y actualizar la posición."""
        nonlocal y_actual
        if y_actual <= margen_inferior:  # Verificar si hay espacio suficiente
            c.showPage()
            y_actual = margen_superior
        if bold:
            c.setFont(f"{font}-Bold", size)
        else:
            c.setFont(font, size)
        c.drawString(x_inicial, y_actual, texto)
        y_actual -= salto

    # Encabezado del PDF
    agregar_texto(estacionamiento["nombre"], font="Helvetica", size=16, bold=True, salto=30)
    # Encabezado del PDF
    tipo_recibo = "Renovacion Plan" if datos_plan else "Renovacion Tarjeta"
    agregar_texto(tipo_recibo, font="Helvetica", size=20, bold=True, salto=30)

    # Datos del Cliente
    agregar_texto("Datos del Cliente", bold=True, salto=20)
    agregar_texto(f"Nombre: {datos_cliente['nombre']}")
    agregar_texto(f"Correo: {datos_cliente['email']}  Teléfono: {datos_cliente['telefono']}")

    # Datos del Plan (si existen)
    if datos_plan:
        agregar_texto("Datos del Plan", bold=True, salto=30)
        agregar_texto(f"Tipo plan: {datos_plan['tarifa_duracion']}")
        agregar_texto(f"Total: {datos_plan['tarifa_costo']}")
        agregar_texto(f"Vigencia: Inicio {datos_plan['fecha_inicio']} Fin: {datos_plan['fecha_fin']}")

    # Datos de la Tarjeta (si existen)
    if datos_tarjeta:
        agregar_texto("Tarjeta Asignada", bold=True, salto=30)
        agregar_texto(f"Número: {datos_tarjeta['numero_tarjeta']}")

    # Datos del Cambio
    if cambio is not None:
        agregar_texto("Cambio", bold=True, salto=30)
        agregar_texto(f"${cambio or "0"}")

    # Guardar el PDF
    c.save()
    logger.info(f"PDF generado en {filename}")


def imprime_recibo_renovacion(cliente_id, cambio, datos_plan=None, datos_tarjeta=None):
    try:
        # Obtener la instancia de la impresora
        printer = obtener_impresora()
        datos_cliente = busca_cliente(cliente_id=cliente_id)

        if printer == "MICROSOFT_PRINT_TO_PDF":
            # Generar un archivo PDF y guardarlo en una ubicación específica
            output_path = os.path.join(os.getcwd(), "nuevo_plan.pdf")
            generar_pdf(datos_cliente, datos_plan, datos_tarjeta, output_path, cambio)

            # Enviar el archivo PDF a "Microsoft Print to PDF"
            logger.info(f"Enviando el archivo PDF a la impresora 'Microsoft Print to PDF'")
            subprocess.run(["start", "/MIN", output_path], shell=True, check=True)
            logger.info("Archivo enviado a la impresora PDF.")
        else:
            # Configuración y uso de la impresora RAW
            printer.set(align="center", bold=True, double_height=True, double_width=True)
            printer.textln(f"{leer_datos()['nombre']}")
            printer.ln()
            tipo_recibo = "Renovacion Plan" if datos_plan else "Renovacion Tarjeta"
            printer.textln(f"{tipo_recibo}")
            printer.set(align="left")
            printer.textln(f"Datos Cliente")
            printer.set(align="left", bold=False, normal_textsize=True)
            printer.textln(f"Nombre: {datos_cliente['nombre']}")
            printer.textln(f"Correo: {datos_cliente['email']}  Telefono: {datos_cliente['telefono']}")
            printer.ln()
            if datos_plan:
                printer.set(align="left", bold=True, double_height=True, double_width=True)
                printer.textln("Datos Plan")
                printer.set(align="left", bold=False, normal_textsize=True)
                printer.textln(f"Tipo plan: {datos_plan['tarifa_duracion']} Total: {datos_plan['tarifa_costo']}")
                printer.textln(f"Vigencia: Inicio {datos_cliente['fecha_inicio']} Fin: {datos_plan['fecha_fin']} ")
                printer.ln()

            if datos_tarjeta:
                printer.set(align="left", bold=True, double_height=True, double_width=True)
                printer.textln("Tarjeta asignada")
                printer.set(align="left", bold=False, normal_textsize=True)
                printer.textln(f"Numero: {datos_tarjeta['numero_tarjeta']}")

            printer.set(align="left", bold=True, double_height=True, double_width=True)
            printer.textln(f"Cambio: ${cambio or "0"}")

            printer.cut()
            printer.close()
            logger.info("Recibo plan impreso correctamente.")
    except (DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError, ConfigSyntaxError,
            ConfigSectionMissingError) as e:
        logger.warning(f"No se encontró la impresora o no se pudo conectar: {e}")
        raise DeviceNotFoundError(e)
    except ValueError as e:
        logger.warning("No se encontró la impresora o no se pudo conectar.")
        raise ValueError(e)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error al enviar el archivo PDF a la impresora: {e}")
        raise e
    except Exception as e:
        logger.warning(f"Error inesperado: {e}")
        raise Exception(e)
