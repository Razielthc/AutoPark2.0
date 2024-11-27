import flet as ft

from models.model_ingresos import ingresos_total_mes_actual
from models.model_ingresos import ingresos_total_turno_actual
from vistas.frames.bar_char_frame import Charxmes
from vistas.frames.line_char_frame import Charxdia


class DashboardPage(ft.Row):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.isolated = True
        self.expand = True
        self.line_chart = Charxdia()
        self.bar_chart = Charxmes()
        self.total_dia = ft.Text(value=f"${ingresos_total_turno_actual()}", size=30)
        self.total_mes = ft.Text(value=f"${ingresos_total_mes_actual()}", size=30)
        self.contenedor1 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="Ganancias del día", size=30),
                        ft.Divider(height=5, color="GREY_300", thickness=3),
                        ft.Row(
                            [ft.Icon(ft.icons.ATTACH_MONEY_ROUNDED, size=30),
                             self.total_dia]
                        )
                    ]
                ),
                expand=True,
                padding=10,
            ),
            expand=False
        )

        self.contenedor2 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="Ganancias totales del mes", size=30),
                        ft.Divider(height=5, color="GREY_300", thickness=3),
                        ft.Row(
                            [ft.Icon(ft.icons.ATTACH_MONEY_ROUNDED, size=30), self.total_mes]
                        )
                    ]
                ),
                expand=True,
                padding=5,
            ),
            expand=False,

        )

        self.contenedor3 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="Ganancias totales del mes por dia", size=30),
                        ft.Divider(height=5, color="GREY_300", thickness=3),
                        ft.Container(
                            content=self.line_chart,
                            expand=True,
                            padding=20
                        )
                    ]
                ),
                expand=True,
                padding=10,
            ),
            expand=True,

        )

        self.contenedor4 = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(value="Ganancias totales del año por mes", size=30),
                        ft.Divider(height=5, color="GREY_300", thickness=3),
                        ft.Container(
                            content=self.bar_chart,
                            expand=True
                        )
                    ],
                    expand=True
                ),

                padding=10,
                expand=True
            ),
            expand=True,

        )
        self.controls = [
            ft.Column(controls=[self.contenedor1, self.contenedor3], expand=True),
            ft.Column(controls=[self.contenedor2, self.contenedor4], expand=True)

        ]

    def did_mount(self):
        self.carga_charts()

    def carga_charts(self):
        if self.usuario[1] == "operador":
            self.contenedor2.visible = False
            self.contenedor3.visible = False
            self.contenedor4.visible = False
            self.update()


if __name__ == "__main__":
    pass
