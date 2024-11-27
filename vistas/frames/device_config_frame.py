import re
import logging
from dotenv import set_key
import flet as ft
from decouple import AutoConfig
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

# Ejemplo de uso:
config_path = resource_path('.env')
config = AutoConfig(config_path)
logging.warning(f"ruta mail_setting {config_path}")


class DeviceConfig(ft.Row):
    def __init__(self, device=None):
        super().__init__()
        self.device = device
        self.dlg = ft.AlertDialog()
        self.expand = True
        self.isolated = True
        self.check_device_enabled = ft.Checkbox(label="Habilitar Controlador de barreras",
                                                value=config('CONTROLADOR_ENABLED', default='False', cast=bool),
                                                on_change=self.checkbox_changed)
        self.device_user_input = ft.TextField(
            label="usuario",
            value=config('CONTROLADOR_USER'),
            on_change=self.limpia_inputs
        )
        self.device_password_input = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            value=config('CONTROLADOR_PASS'),
            on_change=self.limpia_inputs
        )

        self.device_ip_input = ft.TextField(
            label="IP",
            value=config('CONTROLADOR_IP'),
            on_change=self.limpia_inputs
        )

        self.device_port_input = ft.TextField(
            label="puerto",
            value=config('CONTROLADOR_PORT'),
            on_change=self.limpia_inputs
        )

        self.btn_guardar = ft.FilledButton(text="Guardar", style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                                           on_click=self.guardar)
        self.btn_test_device = ft.FilledButton(text="Probar controlador",
                                               style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_ACCENT),
                                               on_click=self.test_device)

        self.alignment = ft.MainAxisAlignment.CENTER
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER

        self.controls = [ft.Column(
            controls=[
                ft.Row([self.check_device_enabled], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(
                    [ft.Text(value="Usuario", size=20, weight=ft.FontWeight.W_400), self.device_user_input],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="Contraseña", size=20, weight=ft.FontWeight.W_400), self.device_password_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="IP", size=20, weight=ft.FontWeight.W_400), self.device_ip_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="Puerto", size=20, weight=ft.FontWeight.W_400), self.device_port_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Row([self.btn_guardar, self.btn_test_device], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ],
            width=500,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30

        )]

    def did_mount(self):
        try:
            habilitado = config('CONTROLADOR_ENABLED', default='False', cast=bool)
            logger.warning("valor de CONTROLADOR_ENABLED")
            self.device_user_input.disabled = not habilitado
            self.device_password_input.disabled = not habilitado
            self.device_ip_input.disabled = not habilitado
            self.device_port_input.disabled = not habilitado
            self.btn_test_device.disabled = not habilitado
            self.update()
        except (KeyError, Exception) as e:
            self.muestra_mensaje(mensaje="Error al cargar el archivo de configuracion", tipo="error")

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()

    def muestra_mensaje(self, mensaje, tipo):
        if tipo == "error":
            icono = ft.Icon(ft.icons.ERROR_ROUNDED, color=ft.colors.RED_ACCENT_400, size=150)
        elif tipo == "reinicio":
            icono = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=ft.colors.GREEN_ACCENT_400, size=150)
            self.dlg.modal = True
            self.dlg.actions = [ft.TextButton("Aceptar", on_click=self.acepta_reinicio)]
        else:
            icono = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=ft.colors.GREEN_ACCENT_400, size=150)
        contenido = ft.Column(
            controls=[icono, ft.Text(value=mensaje)],
            height=200,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.dlg.content = contenido
        self.page.open(self.dlg)

    def guardar(self, e):

        if not self.validar_datos(self.device_user_input.value, "device_user"):
            self.device_user_input.error_text = "usuario no valido"
            self.update()
            return

            # Validar puerto SMTP
        if not self.validar_datos(self.device_password_input.value, "device_password"):
            self.device_password_input.error_text = "Contraseña no valida"
            self.update()
            return

            # Validar usuario SMTP
        if not self.validar_datos(self.device_ip_input.value, "device_ip"):
            self.device_ip_input.error_text = "ip no valido"
            self.update()
            return

            # Validar contraseña SMTP
        if not self.validar_datos(self.device_port_input.value, "device_port"):
            self.device_port_input.error_text = "puerto no valido"
            self.update()
            return

        try:
            set_key(config_path, "CONTROLADOR_ENABLED", str(self.check_device_enabled.value))
            set_key(config_path, "CONTROLADOR_USER", self.device_user_input.value)
            set_key(config_path, "CONTROLADOR_PASS", self.device_password_input.value)
            set_key(config_path, "CONTROLADOR_IP", self.device_ip_input.value)
            set_key(config_path, "CONTROLADOR_PORT", self.device_port_input.value)

            self.muestra_mensaje(mensaje="Datos guardados con Exito es necesario reiniciar", tipo="reinicio")

        except FileNotFoundError as e:
            self.muestra_mensaje(mensaje=f"Error al probar el correo {e}", tipo="error")

        except Exception as e:
            self.muestra_mensaje(mensaje=f"Error al probar el correo {e}", tipo="error")

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "device_ip": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",  # ip simple
            "device_port": r"^[0-9]+$",  # Solo números
            "device_user": r".+",  # Formato de correo electrónico
            "device_password": r".+"  # Cualquier cadena no vacía
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    def test_device(self, e):
        try:
            resultado_login = self.device.login()
            if resultado_login is True:
                self.device.abrir_pluma(0, metodo_entrada="prueba sistema")
                self.device.abrir_pluma(1, metodo_entrada="prueba sistema")
            self.muestra_mensaje(mensaje="El controlador se a probado con exito", tipo="exito")
        except Exception as e:
            print(e)
            self.muestra_mensaje(mensaje=f"Error al probar el controlador {e}", tipo="error")

    def checkbox_changed(self, e):
        self.device_user_input.disabled = not e.control.value
        self.device_password_input.disabled = not e.control.value
        self.device_ip_input.disabled = not e.control.value
        self.device_port_input.disabled = not e.control.value
        self.btn_test_device.disabled = not e.control.value
        self.update()

    def acepta_reinicio(self, e):
        self.page.window_destroy()
