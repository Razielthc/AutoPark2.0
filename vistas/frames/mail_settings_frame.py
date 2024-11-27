import re
import logging
from dotenv import set_key
import flet as ft
from decouple import AutoConfig
from procedimientos.enviar_correo import test_correo
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

# Ejemplo de uso:
config_path = resource_path('.env')
config = AutoConfig(config_path)
logging.warning(f"ruta mail_setting {config_path}")


class SettingMail(ft.Row):
    def __init__(self):
        super().__init__()
        self.dlg = ft.AlertDialog()
        self.expand = True
        self.isolated = True
        self.check_mail_enabled = ft.Checkbox(label="Habilitar correo para envio de reporte",
                                              value=config('SMTP_ENABLED', default='False', cast=bool),
                                              on_change=self.checkbox_changed)
        self.smtp_server_input = ft.TextField(
            label="Servidor SMTP",
            value=config('SMTP_SERVER'),
            on_change=self.limpia_inputs
        )
        self.smtp_port_input = ft.TextField(
            label="Puerto SMTP",
            value=str(config('SMTP_PORT')),
            on_change=self.limpia_inputs
        )

        self.smtp_user_input = ft.TextField(
            label="Usuario SMTP",
            value=config('SMTP_USERNAME'),
            on_change=self.limpia_inputs
        )

        self.smtp_password_input = ft.TextField(
            label="Contraseña SMTP",
            password=True,
            value=config('SMTP_PASSWORD'),
            on_change=self.limpia_inputs
        )

        self.smtp_mail_to_input = ft.TextField(
            label="Correo que va a recibir los reportes",
            value=config('SMTP_MAIL_TO'),
            on_change=self.limpia_inputs
        )

        self.btn_guardar = ft.FilledButton(text="Guardar", style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                                           on_click=self.guardar)
        self.btn_test_mail = ft.FilledButton(text="Enviar correo de prueba",
                                             style=ft.ButtonStyle(bgcolor=ft.colors.BLUE_ACCENT),
                                             on_click=self.test_mail)

        self.alignment = ft.MainAxisAlignment.CENTER
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER

        self.controls = [ft.Column(
            controls=[
                ft.Row([self.check_mail_enabled], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(
                    [ft.Text(value="Servidor de correo", size=20, weight=ft.FontWeight.W_400), self.smtp_server_input],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="Puerto", size=20, weight=ft.FontWeight.W_400), self.smtp_port_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="Usuario", size=20, weight=ft.FontWeight.W_400), self.smtp_user_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text(value="Contraseña", size=20, weight=ft.FontWeight.W_400), self.smtp_password_input],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row(
                    [ft.Text(value="Correo de destino", size=20, weight=ft.FontWeight.W_400), self.smtp_mail_to_input],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([self.btn_guardar, self.btn_test_mail], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ],
            width=500,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30

        )]

    def did_mount(self):
        try:
            habilitado = config('SMTP_ENABLED', default='False', cast=bool)
            logger.warning("valor de SMTP_ENABLED")
            self.smtp_server_input.disabled = not habilitado
            self.smtp_port_input.disabled = not habilitado
            self.smtp_user_input.disabled = not habilitado
            self.smtp_password_input.disabled = not habilitado
            self.smtp_mail_to_input.disabled = not habilitado
            self.btn_test_mail.disabled = not habilitado
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

        if not self.validar_datos(self.smtp_server_input.value, "smtp_server"):
            self.smtp_server_input.error_text = "Servidor SMTP no válido"
            self.update()
            return

            # Validar puerto SMTP
        if not self.validar_datos(self.smtp_port_input.value, "smtp_port"):
            self.smtp_port_input.error_text = "Puerto SMTP no válido"
            self.update()
            return

            # Validar usuario SMTP
        if not self.validar_datos(self.smtp_user_input.value, "smtp_username"):
            self.smtp_user_input.error_text = "Usuario SMTP no válido"
            self.update()
            return

            # Validar contraseña SMTP
        if not self.validar_datos(self.smtp_password_input.value, "smtp_password"):
            self.smtp_password_input.error_text = "Contraseña SMTP no válida"
            self.update()
            return

        if not self.validar_datos(self.smtp_mail_to_input.value, "smtp_username"):
            self.smtp_mail_to_input.error_text = "Contraseña SMTP no válida"
            self.update()
            return

        try:
            set_key(config_path, "SMTP_ENABLED", str(self.check_mail_enabled.value))
            set_key(config_path, "SMTP_SERVER", self.smtp_server_input.value)
            set_key(config_path, "SMTP_PORT", self.smtp_port_input.value)
            set_key(config_path, "SMTP_USERNAME", self.smtp_user_input.value)
            set_key(config_path, "SMTP_PASSWORD", self.smtp_password_input.value)
            set_key(config_path, "SMTP_MAIL_TO", self.smtp_mail_to_input.value)

            self.muestra_mensaje(mensaje="Datos guardados con Exito es necesario reiniciar", tipo="reinicio")

        except FileNotFoundError as e:
            self.muestra_mensaje(mensaje=f"Error al probar el correo {e}", tipo="error")

        except Exception as e:
            self.muestra_mensaje(mensaje=f"Error al probar el correo {e}", tipo="error")

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "smtp_server": r"^([a-zA-Z0-9]+\.)+[a-zA-Z]{2,}$",  # Dominio simple
            "smtp_port": r"^[0-9]+$",  # Solo números
            "smtp_username": r"^[^@]+@[^@]+\.[a-zA-Z]{2,}$",  # Formato de correo electrónico
            "smtp_password": r".+"  # Cualquier cadena no vacía
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    def test_mail(self, e):
        try:
            test_correo(server_smtp=self.smtp_server_input.value, port=int(self.smtp_port_input.value),
                        user_name=self.smtp_user_input.value,
                        password_mail=self.smtp_password_input.value, to_mail=self.smtp_mail_to_input.value)
            self.muestra_mensaje(mensaje="El correo se envio con exito", tipo="exito")
        except Exception as e:
            print(e)
            self.muestra_mensaje(mensaje=f"Error al probar el correo {e}", tipo="error")

    def checkbox_changed(self, e):
        self.smtp_server_input.disabled = not e.control.value
        self.smtp_port_input.disabled = not e.control.value
        self.smtp_user_input.disabled = not e.control.value
        self.smtp_password_input.disabled = not e.control.value
        self.smtp_mail_to_input.disabled = not e.control.value
        self.btn_test_mail.disabled = not e.control.value
        self.update()

    def acepta_reinicio(self, e):
        self.page.window_destroy()
