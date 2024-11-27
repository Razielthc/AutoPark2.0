import flet as ft

from models.model_rol import leer_roles
from models.model_user import crear_usuario, actualizar_usuario, hash_password


class Adduser(ft.Column):
    def __init__(self, user_page, user=None):
        super().__init__()
        self.user = user
        self.expand = False
        self.isolated = True
        self.all_filled = True
        self.width = 450
        self.height = 400
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.spacing = 15
        self.user_page = user_page  # Guardar la referencia a UserPage
        self.name_input = ft.TextField(label="Nombre completo", icon=ft.icons.PERSON,
                                       on_change=self.limpia_inputs)
        self.username_input = ft.TextField(label="usuario", icon=ft.icons.PERSON,
                                           on_change=self.limpia_inputs)
        self.password_input = ft.TextField(label="Contraseña", password=True, can_reveal_password=True,
                                           icon=ft.icons.KEY,
                                           on_change=self.limpia_inputs)

        self.list_role = ft.Dropdown(
            hint_text="Selecciona un rol para el usuario",
            on_change=self.limpia_inputs,
            icon=ft.icons.PERM_DATA_SETTING,
            key="list_role"
        )
        # Boton Guardar
        self.save_button = ft.FilledButton(
            content=ft.Container(content=ft.Text(value="Guardar", size=15),
                                 width=150,
                                 padding=10,
                                 alignment=ft.alignment.center,
                                 ),
            on_click=self.save_user,
            style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
            key="Guardar")
        # Boton Cancelar
        self.cancel_button = ft.FilledButton(
            content=ft.Container(content=ft.Text(value="Cancelar", size=15),
                                 width=150,
                                 padding=10,
                                 alignment=ft.alignment.center,
                                 ),
            on_click=self.cancelar,
            style=ft.ButtonStyle(bgcolor=ft.colors.RED_ACCENT_400),
            key="Cerrar")

        self.controls = [
            ft.Column([self.name_input, self.username_input, self.password_input, self.list_role]),
            ft.Row([self.save_button, self.cancel_button],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ]

    def did_mount(self):
        roles = leer_roles()
        if isinstance(roles, list):
            for rol in roles:
                if rol["name"] != "admin":
                    self.list_role.options.append(ft.dropdown.Option(key=str(rol['id']),
                                                                     text=rol['name']))
        if self.user is not None:
            if self.user.get('rol_name') == "admin":
                self.list_role.disabled = True
                self.username_input.disabled = True
            self.list_role.value = self.user.get('role_id')
            self.name_input.value = self.user.get('name')
            self.username_input.value = self.user.get('username')
            self.password_input.label = "Nueva Contraseña"
            self.list_role.value = self.user.get('role_id')
            self.save_button.on_click = self.update_user

        self.update()

    def cancelar(self, e):
        self.user_page.handle_close(e)

    def validacion_input(self):
        inputs = [self.name_input, self.username_input, self.password_input, self.list_role]

        for input_field in inputs:
            if input_field == self.list_role:
                # Validación específica para self.list_role
                if input_field.value is None:
                    input_field.error_text = "Debes seleccionar un rol"
                    self.all_filled = False
            else:
                # Validación para otros inputs
                if not input_field.value or len(input_field.value) <= 5:
                    input_field.error_text = "El campo no puede estar vacío o tener menos de 6 caracteres"
                    self.all_filled = False
                else:
                    input_field.error_text = None  # Limpiar el mensaje de error si el campo tiene valor
                    self.all_filled = True

        self.update()  # Actualizar la UI después de establecer mensajes de error

    def save_user(self, e):
        self.validacion_input()
        if self.all_filled:
            try:
                # Si todos los campos tienen valor, proceder a crear el usuario
                resultado = crear_usuario(nombre=self.name_input.value,
                                          username=self.username_input.value,
                                          plain_password=self.password_input.value,
                                          role_id=int(self.list_role.value))
                if resultado is True:
                    self.user_page.handle_close(e)
            except Exception as error:
                self.user_page.handle_close(e, mensaje=error)

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()

    def update_user(self, e):
        campos_a_actualizar = {}
        if self.name_input.value != self.user.get('name'):
            campos_a_actualizar['nombre'] = self.name_input.value

        if self.username_input.value != self.user.get('username'):
            campos_a_actualizar['username'] = self.username_input.value

        if self.password_input.value:  # Solo actualiza la contraseña si se ha proporcionado una nueva
            hashed_password = hash_password(self.password_input.value)
            if isinstance(hashed_password, str) and "Error" in hashed_password:
                return hashed_password
            campos_a_actualizar['password'] = hashed_password

        if self.list_role.value != self.user.get('role_id'):
            campos_a_actualizar['role_id'] = int(self.username_input.value)

        if not campos_a_actualizar:
            self.user_page.handle_close(e)

        # Llamar a la función `actualizar_usuario` solo con los campos que hayan cambiado
        resultado = actualizar_usuario(
            user_id=self.user.get('id'),
            nombre=campos_a_actualizar.get('nombre'),
            username=campos_a_actualizar.get('username'),
            plain_password=campos_a_actualizar.get('password')
        )
        if isinstance(resultado, str):
            self.user_page.handle_close(e, mensaje=resultado)

        else:
            self.user_page.handle_close(e)


if __name__ == "__main__":
    pass
