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


def generar_pdf(datos_cliente, datos_plan, datos_tarjeta, filename, cambio):
    """Genera un archivo PDF con los datos del plan, cliente, y tarjeta respetando el formato con saltos de línea."""
    estacionamiento = leer_datos()
    c = canvas.Canvas(filename)

    # Encabezado del PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 800, estacionamiento["nombre"])
    c.setFont("Helvetica", 12)

    # Datos del Cliente
    c.drawString(50, 750, "Datos Cliente")
    c.setFont("Helvetica", 11)
    c.drawString(50, 730, f"Nombre: {datos_cliente['nombre']}")
    c.drawString(50, 710, f"Documento: {datos_cliente['documento']} Folio: {datos_cliente['folio_documento']}")
    c.drawString(50, 690, f"Correo: {datos_cliente['email']}  Teléfono: {datos_cliente['telefono']}")
    c.drawString(50, 670, f"Dirección: {datos_cliente['direccion']}")
    c.drawString(50, 650, f"Modelo: {datos_cliente['modelo']} Placa: {datos_cliente['placa']}")

    # Datos del Plan
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 630, "Datos Plan")
    c.setFont("Helvetica", 11)
    c.drawString(50, 610, f"Tipo plan: {datos_plan['tarifa_duracion']}")
    c.drawString(50, 590, f"Total: {datos_plan['tarifa_costo']}")
    c.drawString(50, 570, f"Vigencia: Inicio {datos_plan['fecha_inicio']} Fin: {datos_plan['fecha_fin']}")

    # Datos de la Tarjeta
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 550, "Tarjeta Asignada")
    c.setFont("Helvetica", 11)
    c.drawString(50, 530, f"Número: {datos_tarjeta['numero_tarjeta']}")

    # Datos del Cambio
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 510, "Cambio")
    c.setFont("Helvetica", 11)
    c.drawString(50, 490, f"{cambio}")

    c.save()

    logger.info(f"PDF generado en {filename}")


def imprime_recibo(datos_cliente, datos_plan, datos_tarjeta, cambio):
    try:
        # Obtener la instancia de la impresora
        printer = obtener_impresora()

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
            printer.textln(f"Nuevo plan pension")
            printer.set(align="left")
            printer.textln(f"Datos Cliente")
            printer.set(align="left", bold=False, normal_textsize=True)
            printer.textln(f"Nombre: {datos_cliente['nombre']}")
            printer.textln(f"Documento: {datos_cliente['documento']} Folio: {datos_cliente['folio_documento']}")
            printer.textln(f"Correo: {datos_cliente['email']}  Telefono: {datos_cliente['telefono']}")
            printer.textln(f"Direccion: {datos_cliente['direccion']}")
            printer.textln(f"Modelo: {datos_cliente['nombre']} Placa: {datos_cliente['placa']}")
            printer.ln()
            printer.set(align="left", bold=True, double_height=True, double_width=True)
            printer.textln("Datos Plan")
            printer.set(align="left", bold=False, normal_textsize=True)
            printer.textln(f"Tipo plan: {datos_plan['tarifa_duracion']} Total: {datos_plan['tarifa_costo']}")
            printer.textln(f"Vigencia: Inicio {datos_cliente['fecha_inicio']} Fin: {datos_plan['fecha_fin']} ")
            printer.ln()
            printer.set(align="left", bold=True, double_height=True, double_width=True)
            printer.textln("Tarjeta asignada")
            printer.set(align="left", bold=False, normal_textsize=True)
            printer.textln(f"Numero: {datos_tarjeta['numero_tarjeta']}")

            printer.set(align="left", bold=True, double_height=True, double_width=True)
            printer.textln(f"Cambio: {cambio}")

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
