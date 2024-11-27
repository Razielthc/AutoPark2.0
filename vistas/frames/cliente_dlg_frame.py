import flet as ft
import re
import logging
from models.model_clientes import actualizar_cliente

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


class ClienteDlg(ft.AlertDialog):
    def __init__(self, cliente=None, usuario_id=None, on_complete=None):
        super().__init__()
        self.cliente = cliente
        self.on_complete = on_complete
        self.modal = True
        self.isolated = True
        self.title = ft.Text("Editar Cliente")

        self.cliente_id = None

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
        self.usuario_id = usuario_id

        self.content = ft.Column(
            controls=[
                ft.Text("Datos del Cliente", size=24, weight=ft.FontWeight.BOLD),
                self.nombre_input,
                ft.Row(controls=[self.documento_input, self.folio_documento_input]),
                ft.Row(controls=[self.email_input, self.telefono_input]),
                self.direccion_input,
                ft.Row(controls=[self.modelo_input, self.placa_input]),
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            text="Guardar",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_ACCENT_400,
                                color="white"
                            ),
                            on_click=self.guardar_cliente
                        ),
                        ft.OutlinedButton(
                            text="Cancelar",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.RED_ACCENT_400,
                                color="white"
                            ),
                            on_click=self.cierra_modal
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            height=600,
            width=800
        )

    def did_mount(self):
        self.carga_datos_cliente()

    def carga_datos_cliente(self):
        if self.cliente is not None:
            self.cliente_id = self.cliente['id']
            self.nombre_input.value = self.cliente['nombre']
            self.documento_input.value = self.cliente['documento'].strip().upper()
            self.folio_documento_input.value = self.cliente['folio_documento']
            self.email_input.value = self.cliente['email']
            self.telefono_input.value = self.cliente['telefono']
            self.direccion_input.value = self.cliente['direccion']
            self.modelo_input.value = self.cliente['modelo']
            self.placa_input.value = self.cliente['placa']

        self.update()

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "cliente_nombre": r"^.+$",  # Dominio simple
            "cliente_documento": r"^(INE|LICENCIA|PASAPORTE)$",  # Solo números
            "cliente_folio_documento": r"^.+$",  # Formato de correo electrónico
            "cliente_email": r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$",  # Cualquier cadena no vacía
            "cliente_telefono": r"^\d{1,10}$",
            "cliente_direccion": r"^.+$",
            "modelo": r"^.+$",  # Dominio simple
            "placa": r"^.+$",  # Formato de correo electrónico
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    # Función para manejar el botón de guardar
    def guardar_cliente(self, e):

        if not self.validar_datos(self.nombre_input.value, "cliente_nombre"):
            self.nombre_input.error_text = "Nombre no valido"
            self.update()
            return

        documento = self.documento_input.value or ""  # Asignar cadena vacía si no hay selección
        if not self.validar_datos(documento, "cliente_documento"):
            self.documento_input.error_text = "Documento no válido"
            self.update()
            return

        if not self.validar_datos(self.folio_documento_input.value, "cliente_folio_documento"):
            self.folio_documento_input.error_text = "Folio no valido"
            self.update()
            return

        if not self.validar_datos(self.email_input.value, "cliente_email"):
            self.email_input.error_text = "Correo no valido"
            self.update()
            return

        if not self.validar_datos(self.telefono_input.value, "cliente_telefono"):
            self.telefono_input.error_text = "Telefono no valido"
            self.update()
            return

        if not self.validar_datos(self.direccion_input.value, "cliente_direccion"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return

        if not self.validar_datos(self.modelo_input.value, "modelo"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return

        if not self.validar_datos(self.placa_input.value, "placa"):
            self.direccion_input.error_text = "Direccion no valida"
            self.update()
            return

        try:
            if self.cliente is not None:  # Si existe un ID, se actualiza
                actualizar_cliente(
                    cliente_id=int(self.cliente_id),
                    usuario_id=int(self.usuario_id),
                    nombre=self.nombre_input.value,
                    documento=self.documento_input.value,
                    folio_documento=self.folio_documento_input.value,
                    email=self.email_input.value,
                    telefono=self.telefono_input.value,
                    direccion=self.direccion_input.value,
                    placa=self.placa_input.value,
                    modelo=self.modelo_input.value

                )

            # Notificar al callback con el resultado
            if self.on_complete:
                self.on_complete(True)

            # Cerrar el modal
            self.cierra_modal(e)

        except Exception as ex:
            # Notificar al callback del error
            if self.on_complete:
                self.on_complete(False, ex)

            # Cerrar el modal
            self.cierra_modal(e)

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()

    def cierra_modal(self, e):
        self.page.close(self)
