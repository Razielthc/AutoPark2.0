import flet as ft

from vistas.frames.plan_nuevo_frame import PlanForm
from vistas.frames.tarjeta_nueva_frame import TarjetaForm


class RenuevaDlg(ft.AlertDialog):
    def __init__(self, tipo, on_complete):
        super().__init__()
        self.on_complete = on_complete
        self.tipo = tipo
        self.isolated = True
        self.modal = True
        self.plan_form = PlanForm()
        self.tarjeta_form = TarjetaForm()
        self.plan_seleccionado = None
        self.tarjeta_info = None
        self.form = ft.Column(spacing=50, height=600)
        self.content = self.form

    def did_mount(self):
        if self.tipo == "plan":
            self.title = ft.Text("Renovacion del Plan")
            self.form.controls = [
                self.plan_form,
                ft.Row(controls=[
                    ft.FilledButton(content=ft.Text(value="Confirmar", weight=ft.FontWeight.BOLD, size=20),
                                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                                    on_click=self.validar_paso_actual),
                    ft.FilledButton(content=ft.Text(value="Cancelar", weight=ft.FontWeight.BOLD, size=20),
                                    style=ft.ButtonStyle(bgcolor=ft.colors.GREY_600),
                                    on_click=self.cierra_modal)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ]

        elif self.tipo == "tarjeta":
            self.title = ft.Text("Renovacion Tarjeta")
            self.form.controls = [
                self.tarjeta_form,
                ft.Row(controls=[
                    ft.FilledButton(content=ft.Text(value="Confirmar", weight=ft.FontWeight.BOLD, size=20),
                                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                                    on_click=self.validar_paso_actual),
                    ft.FilledButton(content=ft.Text(value="Cancelar", weight=ft.FontWeight.BOLD, size=20),
                                    style=ft.ButtonStyle(bgcolor=ft.colors.GREY_600),
                                    on_click=self.cierra_modal)
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ]
        self.update()

    def validar_paso_actual(self, e):
        """Valida el paso actual del formulario."""

        if self.tipo == "plan":
            # Validar selección del plan
            resultado, plan_seleccionado = self.plan_form.valida_plan()
            if not resultado:
                return False
            self.plan_seleccionado = plan_seleccionado
            # Notificar al callback con el resultado
            if self.on_complete:
                self.on_complete(self.plan_seleccionado, True)
            self.cierra_modal()
        elif self.tipo == "tarjeta":
            # Validar selección del plan
            resultado, tarjeta_info = self.tarjeta_form.valida_tarjeta()
            if not resultado:
                return False
            self.tarjeta_info = tarjeta_info
            # Notificar al callback con el resultado
            if self.on_complete:
                self.on_complete(self.tarjeta_info, True)
            self.cierra_modal()

    def cierra_modal(self, e=None):
        self.page.close(self)
