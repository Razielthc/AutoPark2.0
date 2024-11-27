import flet as ft


class BarPagina(ft.AppBar):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.container_notificaciones = ft.PopupMenuButton(
            icon=ft.icons.NOTIFICATIONS_OUTLINED
        )
        self.mensajes_del_sistema = ft.Container()
        self.leading_width = 50
        self.title = ft.Text("AutoparkMX", size=30, color=ft.colors.BLACK)
        self.center_title = True
        self.bgcolor = ft.colors.SURFACE_VARIANT
        self.actions = [
            self.mensajes_del_sistema,
            self.container_notificaciones
        ]

    def did_mount(self):
        # usuario = self.page.session.get("usuario")
        self.asigna_usuario()

    def remove_item_clicked(self, e):
        # Remover el ítem que fue clicado de la lista de ítems
        self.container_notificaciones.items.remove(e.control)
        # Actualizar la página para reflejar el cambio
        self.container_notificaciones.icon = ft.icons.NOTIFICATIONS_OUTLINED
        self.container_notificaciones.icon_color = ft.colors.PRIMARY
        self.update()

    def agrega_notificacion(self, texto):
        if "error" in texto.lower():
            self.mensajes_del_sistema.visible = True
            self.mensajes_del_sistema.content = ft.Text(texto, color=ft.colors.RED_800)
            self.container_notificaciones.items.append(ft.PopupMenuItem(text=texto, on_click=self.remove_item_clicked))
            self.container_notificaciones.icon = ft.icons.NOTIFICATIONS_ACTIVE
            self.container_notificaciones.icon_color = "red"
        else:
            self.mensajes_del_sistema.visible = False
            self.container_notificaciones.items.append(ft.PopupMenuItem(text=texto, on_click=self.remove_item_clicked))
            self.container_notificaciones.icon = ft.icons.NOTIFICATIONS_ACTIVE
            self.container_notificaciones.icon_color = "green"

        self.update()

    def asigna_usuario(self):
        usuario = self.page.session.get("usuario")
        self.leading = ft.Row(controls=[
            ft.Icon(ft.icons.PERSON, size=30),
            ft.Text(value=usuario[0], size=30)
        ], expand=True)
        self.update()


if __name__ == "__main__":
    pass
