import flet as ft
import re
import logging

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


class ClienteForm(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.width = 600
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.datos_cliente = {}

        self.nombre_input = ft.TextField(label="Nombre", on_change=self.limpia_inputs)
        self.documento_input = ft.Dropdown(
            label="Documento ID",
            hint_text="Selecciona un documento",
            options=[
                ft.dropdown.Option("INE"),
                ft.dropdown.Option("LICENCIA"),
                ft.dropdown.Option("PASAPORTE"),
            ],
            autofocus=True,
            on_change=self.limpia_inputs
        )
        self.folio_documento_input = ft.TextField(label="Folio documento", on_change=self.limpia_inputs)
        self.email_input = ft.TextField(label="Email", on_change=self.limpia_inputs)
        self.telefono_input = ft.TextField(label="Teléfono", on_change=self.limpia_inputs)
        self.direccion_input = ft.TextField(label="Dirección", on_change=self.limpia_inputs)
        self.modelo_input = ft.TextField(label="Modelo y año", on_change=self.limpia_inputs)
        self.placa_input = ft.TextField(label="Placa del Vehiculo", on_change=self.limpia_inputs)

        self.controls = [
            ft.Text("Datos del Cliente", size=24, weight=ft.FontWeight.BOLD),
            self.nombre_input,
            ft.Row(controls=[self.documento_input, self.folio_documento_input]),
            ft.Row(controls=[self.email_input, self.telefono_input]),
            self.direccion_input,
            ft.Row(controls=[self.modelo_input, self.placa_input])
        ]

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "cliente_nombre": r"^.+$",
            "cliente_documento": r"^(INE|LICENCIA|PASAPORTE)$",
            "cliente_folio_documento": r"^.+$",
            "cliente_email": r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$",
            "cliente_telefono": r"^\d{1,10}$",
            "cliente_direccion": r"^.+$",
            "modelo": r"^.+$",
            "placa": r"^.+$",
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    # Función para manejar el botón de guardar
    def valida_cliente(self):

        if not self.validar_datos(self.nombre_input.value, "cliente_nombre"):
            self.nombre_input.error_text = "Nombre no valido"
            self.update()
            return False, None

        documento = self.documento_input.value or ""  # Asignar cadena vacía si no hay selección
        if not self.validar_datos(documento, "cliente_documento"):
            self.documento_input.error_text = "Documento no válido"
            self.update()
            return False, None

        if not self.validar_datos(self.folio_documento_input.value, "cliente_folio_documento"):
            self.folio_documento_input.error_text = "Folio no valido"
            self.update()
            return False, None

        if not self.validar_datos(self.email_input.value, "cliente_email"):
            self.email_input.error_text = "Correo no valido"
            self.update()
            return False, None

        if not self.validar_datos(self.telefono_input.value, "cliente_telefono"):
            self.telefono_input.error_text = "Telefono no valido"
            self.update()
            return False, None

        if not self.validar_datos(self.direccion_input.value, "cliente_direccion"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return False, None

        if not self.validar_datos(self.modelo_input.value, "modelo"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return False, None

        if not self.validar_datos(self.placa_input.value, "placa"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return False, None

        self.datos_cliente['nombre'] = self.nombre_input.value
        self.datos_cliente['documento'] = self.documento_input.value
        self.datos_cliente['folio_documento'] = self.folio_documento_input.value
        self.datos_cliente['email'] = self.email_input.value
        self.datos_cliente['telefono'] = self.telefono_input.value
        self.datos_cliente['direccion'] = self.direccion_input.value
        self.datos_cliente['modelo'] = self.modelo_input.value
        self.datos_cliente['placa'] = self.placa_input.value

        return True, self.datos_cliente

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()


if __name__ == "__main__":
    pass
