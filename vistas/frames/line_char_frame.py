import flet as ft

from models.model_ingresos import ingresos_total_x_dia_mes


class Charxdia(ft.LineChart):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.expand = True
        self.datachart = ft.LineChartData(
            # data_points=data_points,
            color=ft.colors.BLUE,
            curved=False,
            stroke_width=2,
            point=ft.ChartCirclePoint(),
            selected_point=ft.ChartCirclePoint()
        )
        self.bottom_axis = ft.ChartAxis(title=ft.Text("Días del Mes"))
        self.left_axis = ft.ChartAxis(title=ft.Text("Ingresos ($)", size=12, weight=ft.FontWeight.BOLD),
                                      labels_size=40,
                                      title_size=40,
                                      labels_interval=1)
        self.baseline_x = 0
        self.baseline_y = 0
        self.bgcolor = ft.colors.WHITE
        self.border = ft.border.all(width=2, color=ft.colors.BLACK)
        self.horizontal_grid_lines = ft.ChartGridLines(color=ft.colors.GREY, dash_pattern=[2, 2])
        self.vertical_grid_lines = ft.ChartGridLines(color=ft.colors.GREY, dash_pattern=[2, 2])
        self.interactive = True
        self.tooltip_bgcolor = ft.colors.YELLOW
        self.min_y = 0

    def did_mount(self):
        self.carga_datos()

    def carga_datos(self):
        datos = self.obtener_datos()
        if datos:
            monto_maximo = max(datos, key=lambda x: x[1])[1]
            cleaned_datos = [(dia, monto) for dia, monto in datos if monto is not None]  # Filter out None values
            self.datachart.data_points = [ft.LineChartDataPoint(x=int(dia.split('-')[2]), y=float(monto)) for dia, monto
                                          in
                                          cleaned_datos]
            self.data_series = [self.datachart]
            # Obtener montos únicos
            montos_unicos = sorted(set(monto for _, monto in cleaned_datos))
            self.bottom_axis.labels = [
                ft.ChartAxisLabel(value=int(dia.split('-')[2]), label=ft.Text(str(dia.split('-')[2]), size=14))
                for dia, _ in cleaned_datos]
            self.left_axis.labels = [ft.ChartAxisLabel(value=monto, label=ft.Text(str(monto), size=14)) for monto in
                                     montos_unicos]
            self.max_y = monto_maximo
            self.update()

    @staticmethod
    def obtener_datos():
        return ingresos_total_x_dia_mes()
