from escpos.exceptions import (
    DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError,
    ConfigSyntaxError, ConfigSectionMissingError
)
import logging
from decouple import AutoConfig
from utils.get_resorce_path import resource_path
from models.model_datos import leer_datos
from reportlab.pdfgen import canvas
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


def generar_pdf(corte, filename):
    """Genera un archivo PDF con los datos del corte respetando el formato con saltos de línea."""
    estacionamiento = leer_datos()
    c = canvas.Canvas(filename)

    # Encabezado del PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 800, estacionamiento["nombre"])
    c.setFont("Helvetica", 12)

    # Datos principales
    c.drawString(50, 750, f"Corte {corte['tipo']} No: {corte['id']}")
    c.drawString(50, 730, f"Fecha: {corte['fecha']} Usuario: {corte['nombre_usuario']}")

    # Texto con formato en varias líneas
    c.setFont("Helvetica", 11)
    text = c.beginText(50, 710)  # Posición inicial para el bloque de texto
    text.setLeading(14)  # Espaciado entre líneas

    # Añadir cada línea del texto formateado
    for linea in corte["c_salida"].split("\n"):
        text.textLine(linea)

    c.drawText(text)  # Dibujar el texto en el lienzo
    c.save()

    logger.info(f"PDF generado en {filename}")


def imprime_corte(corte):
    try:
        # Obtener la instancia de la impresora
        printer = obtener_impresora()

        if printer == "MICROSOFT_PRINT_TO_PDF":
            # Generar un archivo PDF y guardarlo en una ubicación específica
            output_path = os.path.join(os.getcwd(), "corte.pdf")
            generar_pdf(corte, output_path)

            # Enviar el archivo PDF a "Microsoft Print to PDF"
            logger.info(f"Enviando el archivo PDF a la impresora 'Microsoft Print to PDF'")
            subprocess.run(["start", "/MIN", output_path], shell=True, check=True)
            logger.info("Archivo enviado a la impresora PDF.")
        else:
            # Configuración y uso de la impresora RAW
            printer.set(align="center", bold=True, double_height=True, double_width=True)
            printer.textln(f"{leer_datos()['nombre']}")
            printer.ln()
            printer.set(align="left", bold=False, normal_textsize=True)
            printer.textln(f"Corte {corte['tipo']} No: {corte['id']} ")
            printer.textln(f"Fecha: {corte['fecha']} Usuario: {corte['nombre_usuario']}")
            printer.ln()
            printer.textln(corte["c_salida"])
            printer.cut()
            printer.close()
            logger.info("Corte impreso correctamente.")
    except (DeviceNotFoundError, USBNotFoundError, Error, ConfigNotFoundError, ConfigSyntaxError, ConfigSectionMissingError) as e:
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

