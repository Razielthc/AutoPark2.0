import flet as ft
from utils.get_size_monitor import size_monitor


class Navleft(ft.NavigationRail):
    def __init__(self):
        super().__init__()
        width, height = size_monitor()
        self.routes = {
            0: "/",
            1: "/cobro",
            2: "/clientes",
            3: "/tarifas",
            # 3: "/report",
            4: "/users",
            5: "/settings"
        }
        self.isolated = True
        self.width_monitor = width
        self.height_monitor = height
        self.selected_index = 0
        self.label_type = ft.NavigationRailLabelType.ALL
        self.min_width = self.width_monitor * 0.03
        self.min_extended_width = self.width_monitor * 0.05
        self.group_alignment = -1.0
        self.indicator_shape = ft.BeveledRectangleBorder()
        self.destinations = [
            ft.NavigationRailDestination(
                icon=ft.icons.SPACE_DASHBOARD_OUTLINED,
                selected_icon=ft.icons.SPACE_DASHBOARD_ROUNDED,
                label_content=ft.Text("INICIO", weight=ft.FontWeight.BOLD),

            ),
            ft.NavigationRailDestination(
                icon=ft.icons.DEPARTURE_BOARD_OUTLINED,
                selected_icon=ft.icons.DEPARTURE_BOARD_ROUNDED,
                label_content=ft.Text("COBRO", weight=ft.FontWeight.BOLD),

            ),
            ft.NavigationRailDestination(
                icon=ft.icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.icons.CALENDAR_MONTH_ROUNDED,
                label_content=ft.Text("PLANES", weight=ft.FontWeight.BOLD),

            ),
            ft.NavigationRailDestination(
                icon=ft.icons.PRICE_CHANGE_OUTLINED,
                selected_icon=ft.icons.PRICE_CHANGE_ROUNDED,
                label_content=ft.Text("TARIFAS", weight=ft.FontWeight.BOLD),

            ),
            # ft.NavigationRailDestination(
            #     icon=ft.icons.HOME_OUTLINED,
            #     selected_icon=ft.icons.HOME_ROUNDED,
            #     label_content=ft.Text("REPORTES", weight=ft.FontWeight.BOLD),
            #
            # ),
            ft.NavigationRailDestination(
                icon=ft.icons.PEOPLE_ALT_OUTLINED,
                selected_icon=ft.icons.PEOPLE_ALT_ROUNDED,
                label_content=ft.Text("USUARIOS", weight=ft.FontWeight.BOLD),

            ),
            ft.NavigationRailDestination(
                icon=ft.icons.SETTINGS_OUTLINED,
                selected_icon=ft.icons.SETTINGS_ROUNDED,
                label_content=ft.Text("CONFIGURACION", weight=ft.FontWeight.BOLD),

            )

        ]
        self.on_change = self.select_destination

    def did_mount(self):
        self.verifica_usuario()

    def verifica_usuario(self):
        usuario = self.page.session.get('usuario')
        if usuario[1] == "operador":
            for destino in self.destinations[2:]:
                destino.disabled = True
        elif usuario[1] == "supervisor":
            self.destinations[5].disabled = True

        self.update()

    def select_destination(self, e):
        selected_index = e.control.selected_index
        if selected_index in self.routes:
            self.page.go(self.routes[selected_index])


if __name__ == "__main__":
    pass
