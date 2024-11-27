import flet as ft

from models.model_user import leer_usuarios, eliminar_usuario
from vistas.frames.add_user_frame import Adduser


class UserPage(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True
        self.spacing = 100
        self.frame = None
        self.content_error_modal = ft.Column(width=300,
                                             height=300,
                                             alignment=ft.MainAxisAlignment.CENTER,
                                             horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar datos de usuario"),
        )
        self.error_modal = ft.AlertDialog(
            title=ft.Text("Error al guardar o actualizar"),
            on_dismiss=lambda e: self.update(),
        )

        self.bar = ft.Row(controls=[
            ft.Text(value="Usuarios", size=40),
            ft.ElevatedButton(content=ft.Container(content=ft.Text(value="Nuevo usuario", size=20, expand=True,
                                                                   color="white"),
                                                   padding=10),
                              bgcolor="#3795BD",
                              on_click=self.add_user)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=25)),
                ft.DataColumn(ft.Text("Usuario", size=25)),
                ft.DataColumn(ft.Text("Rol", size=25)),
                ft.DataColumn(ft.Text("Acciones", size=25))
            ],
            expand=True
        )
        self.controls = [
            self.bar,
            self.table
        ]

    def did_mount(self):
        self.actualiza_tabla_usuarios()

    def actualiza_tabla_usuarios(self):
        usuarios = leer_usuarios()
        filas = []
        if isinstance(usuarios, list):
            for usuario in usuarios:

                # Crear una nueva lista de acciones para cada usuario
                acciones = [ft.IconButton(icon=ft.icons.EDIT,
                                          icon_color="YELLOW",
                                          on_click=lambda _, user=usuario: self.update_user(user))]

                # Agregar el botón de eliminar solo si hay más de un usuario
                if usuario["rol_name"] != "admin":
                    acciones.append(ft.IconButton(icon=ft.icons.DELETE,
                                                  icon_color="red",
                                                  on_click=lambda _, user_id=usuario.get('id'): self.delete_user(
                                                      user_id)
                                                  ))

                filas.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(value=usuario['name'])),
                        ft.DataCell(ft.Text(value=usuario['username'])),
                        ft.DataCell(ft.Text(value=usuario['rol_name'])),
                        ft.DataCell(ft.Row(acciones))
                    ]
                ))
            self.table.rows = filas
            self.update()

    def add_user(self, e):
        self.frame = Adduser(user_page=self)
        self.dlg_modal.content = self.frame
        self.page.open(self.dlg_modal)

    def update_user(self, id_user):
        self.frame = Adduser(user_page=self, user=id_user)
        self.dlg_modal.content = self.frame
        self.page.open(self.dlg_modal)

    def handle_close(self, e, mensaje=None):
        self.page.close(self.dlg_modal)
        self.frame.clean()
        if e.control.key == "Guardar":
            if mensaje:
                self.content_error_modal.controls = [
                    ft.Icon(ft.icons.DANGEROUS_OUTLINED, size=150, color="red"),
                    ft.Text(value=mensaje, size=30)
                ]
                self.error_modal.content = self.content_error_modal
                self.page.open(self.error_modal)
            else:
                self.actualiza_tabla_usuarios()

    def delete_user(self, id_user):
        eliminar_usuario(user_id=id_user)
        self.actualiza_tabla_usuarios()


if __name__ == "__main__":
    pass
