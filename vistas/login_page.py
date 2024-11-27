import logging
import asyncio
import flet as ft
from models.model_session import crea_session
from models.model_user import verificar_credenciales

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


class LoginPage(ft.Row):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.login_event = asyncio.Event()
        self.imagen = ft.Image(
            src=f"/imagenes/Autoparklogin_v2.png",  # URL de la imagen de ejemplo
            fit=ft.ImageFit.SCALE_DOWN,
            expand=True,

        )
        # Controles en la columna derecha
        self.username_input = ft.TextField(label="Nombre de usuario", icon=ft.icons.PERSON,
                                           on_change=self.limpia_inputs)
        self.password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True,
                                           icon=ft.icons.KEY,
                                           on_change=self.limpia_inputs)
        self.login_button = ft.FilledButton(content=ft.Container(content=ft.Text(value="Entrar", size=30), width=150,
                                                                 padding=10, alignment=ft.alignment.center),
                                            on_click=self.handle_login)
        # Columna derecha con controles
        self.controls_column = ft.Column(
            controls=[self.username_input, self.password_input, self.login_button],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Container para la imagen con ancho máximo del 50% del ancho de la ventana
        self.image_container = ft.Container(
            content=self.imagen,
            expand=False,
            border_radius=300,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,

        )

        # Container para los controles con ancho máximo del 50% del ancho de la ventana
        self.controls_container = ft.Container(
            content=self.controls_column,
            expand=True,
            padding=ft.padding.symmetric(horizontal=20)

        )
        self.controls = [self.image_container, self.controls_container]
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.spacing = 50
        self.expand = True

    def handle_login(self, e):

        if self.username_input.value and self.password_input.value:
            resultado = verificar_credenciales(username=self.username_input.value,
                                               plain_password=self.password_input.value)
            if isinstance(resultado, dict):
                self.page.session.set("usuario", [resultado['nombre'], resultado['rol_name'], resultado['id']])
                crea_session(resultado['id'])
                logger.info('Usuario autenticado correctamente')
                self.login_event.set()
            else:
                self.username_input.error_text = resultado
                self.password_input.error_text = resultado
        else:
            mensaje_error = "Ingrese un usuario y una contraseña"
            self.username_input.error_text = mensaje_error
            self.password_input.error_text = mensaje_error

        self.update()

    async def esperar_login(self):
        await self.login_event.wait()

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()


if __name__ == "__main__":
    pass
