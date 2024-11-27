import calendar

import flet as ft

from models.model_ingresos import ingresos_total_x_mes_ano


class Charxmes(ft.BarChart):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.border = ft.border.all(1, ft.colors.GREY_400)
        self.left_axis = ft.ChartAxis(
            labels_size=40, title=ft.Text("Ingresos X mes"), title_size=40
        )
        self.horizontal_grid_lines = ft.ChartGridLines(
            color=ft.colors.GREY_300, width=1, dash_pattern=[3, 3]
        )
        self.tooltip_bgcolor = ft.colors.with_opacity(0.5, ft.colors.GREY_300)
        self.interactive = True
        self.expand = True

        # Eje inferior se establece en __init__ para mantener la consistencia
        self.bottom_axis = ft.ChartAxis(labels_size=40)

    def did_mount(self):
        self.carga_datos()

    def carga_datos(self):
        # Obtener datos y determinar el monto máximo
        resultado = self.obtener_datos()
        if resultado:
            # Filter out any None values
            resultado_limpio = [item for item in resultado if item[1] is not None]
            monto_maximo = max(resultado_limpio, key=lambda x: x[1])[1] if resultado_limpio else 0

            # Crear las barras y etiquetas del eje inferior
            self.bar_groups = [
                ft.BarChartGroup(
                    x=index,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=float(total) if total is not None else 0,
                            width=40,
                            color=ft.colors.random_color(),
                            tooltip=f"{calendar.month_name[int(mes.split('-')[1])]}: {total if total is not None else 0}",
                            border_radius=0,
                            border_side=ft.BorderSide(width=1, color="black")
                        )
                    ],
                )
                for index, (mes, total) in enumerate(resultado_limpio)
            ]

            # Crear etiquetas del eje inferior
            self.bottom_axis.labels = [
                ft.ChartAxisLabel(
                    value=index,
                    label=ft.Container(ft.Text(calendar.month_name[int(mes.split('-')[1])]), padding=10)
                )
                for index, (mes, _) in enumerate(resultado_limpio)
            ]

            # Configurar el eje máximo Y
            self.max_y = monto_maximo

            # Actualizar el gráfico
            self.update()

    @staticmethod
    def obtener_datos():
        return ingresos_total_x_mes_ano()

