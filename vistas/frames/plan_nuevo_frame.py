import re
import flet as ft
from datetime import datetime, timedelta
from NetSDK.SDK_Struct import NET_TIME
from models.model_tarifas import tarifas_planes
import json


class PlanForm(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.width = 600
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.plan_seleccionado = {}
        self.fecha_inicio = datetime.now()
        self.fecha_final = None
        self.total_plan = None
        self.duracion = None

        self.input_select_tarifas = ft.Dropdown(
            width=300,
            label="Planes",
            hint_text="Selecciona aun plan",
            autofocus=True,
            on_change=self.asigna_plan
        )

        self.fechas = ft.Text(size=18, weight=ft.FontWeight.W_800, style=ft.TextStyle(color=ft.colors.LIGHT_BLUE_800))

        self.controls = [
            ft.Text("Selecciona un plan", size=24, weight=ft.FontWeight.BOLD),
            self.input_select_tarifas,
            ft.Row(controls=[
                ft.Text("Periodo del plan", size=25, weight=ft.FontWeight.W_900,
                        style=ft.TextStyle(color=ft.colors.BLUE)),
                ft.Icon(name=ft.icons.CALENDAR_MONTH, color=ft.colors.BLUE, size=25),

            ], alignment=ft.MainAxisAlignment.CENTER),
            self.fechas
        ]

    def did_mount(self):
        tarifas = tarifas_planes()
        opciones = []
        if tarifas:
            for tarifa in tarifas:
                opciones.append(
                    ft.dropdown.Option(
                        text=f"Plan {tarifa['nombre']} Precio ${tarifa['costo']}",
                        key=json.dumps(tarifa)  # Convertimos el diccionario en un JSON string
                    ))
        self.input_select_tarifas.options = opciones
        self.update()

    def asigna_plan(self, e):
        if self.input_select_tarifas.value:
            # Convertimos el valor seleccionado de JSON string a diccionario
            tarifa = json.loads(self.input_select_tarifas.value)
            self.duracion = tarifa.get('duracion')  # Puede ser "mensual", "anual", etc.
            self.fecha_final = self.calcular_periodo(self.fecha_inicio, self.duracion)
            self.fechas.value = f"Inicio: {self.fecha_inicio.strftime("%Y-%m-%d")} - Fin: {self.fecha_final.strftime("%Y-%m-%d")}"
            self.total_plan = tarifa.get('costo')
            self.update()

    def valida_plan(self):

        if not self.validar_datos(self.duracion or "", "duracion"):
            self.input_select_tarifas.error_text = "Plan no válido"
            self.update()
            return False, None

        # Crear las fechas como NET_TIME
        valid_begin_time = NET_TIME(
            dwYear=self.fecha_inicio.year,
            dwMonth=self.fecha_inicio.month,
            dwDay=self.fecha_inicio.day,
            dwHour=0,  # Inicio del día
            dwMinute=0,
            dwSecond=0
        )
        valid_end_time = NET_TIME(
            dwYear=self.fecha_final.year,
            dwMonth=self.fecha_final.month,
            dwDay=self.fecha_final.day,
            dwHour=23,  # Fin del día
            dwMinute=59,
            dwSecond=59
        )

        self.plan_seleccionado['tarifa_costo'] = self.total_plan
        self.plan_seleccionado['tarifa_duracion'] = self.duracion
        self.plan_seleccionado['fecha_inicio'] = self.fecha_inicio.strftime("%Y-%m-%d")
        self.plan_seleccionado['fecha_fin'] = self.fecha_final.strftime("%Y-%m-%d")
        self.plan_seleccionado['valid_begin_time'] = valid_begin_time
        self.plan_seleccionado['valid_end_time'] = valid_end_time

        return True, self.plan_seleccionado

    @staticmethod
    def calcular_periodo(fecha_inicio, duracion):
        """
        Calcula la fecha final basada en la duración seleccionada y la fecha inicial.
        :param fecha_inicio: Objeto datetime de la fecha inicial.
        :param duracion: Duración del plan ('semanal', 'mensual', 'anual').
        :return: Fecha final en formato YYYY-MM-DD.
        """
        if duracion == 'semanal':
            # Añadir 7 días para un período semanal
            fecha_final_dt = fecha_inicio + timedelta(weeks=1)
        elif duracion == 'mensual':
            # Añadir un mes, manejando el cambio de año
            mes = fecha_inicio.month + 1
            year = fecha_inicio.year
            if mes > 12:  # Si excede diciembre, ajustamos el año y mes
                mes = 1
                year += 1
            # Calculamos el día válido para el nuevo mes
            ultimo_dia_mes = (datetime(year, mes + 1 if mes < 12 else 1, 1) - timedelta(days=1)).day
            dia = min(fecha_inicio.day, ultimo_dia_mes)
            fecha_final_dt = datetime(year, mes, dia)
        elif duracion == 'anual':
            # Añadir un año
            fecha_final_dt = fecha_inicio.replace(year=fecha_inicio.year + 1)
        else:
            # Si la duración no es reconocida, no cambiamos la fecha
            fecha_final_dt = fecha_inicio

        return fecha_final_dt

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "duracion": r"^(semanal|mensual|anual)$",  # Solo números
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False


if __name__ == "__main__":
    pass
