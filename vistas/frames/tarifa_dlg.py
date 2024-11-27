import re

import flet as ft

from models.model_tarifas import crear_tarifa, actualizar_tarifa


class TarifaDlg(ft.AlertDialog):
    def __init__(self, tarifa=None, on_complete=None):
        super().__init__()
        self.tarifa = tarifa
        self.on_complete = on_complete
        self.modal = True
        self.isolated = True
        self.name_input = ft.TextField(label="Nombre Tarifa", icon=ft.icons.PRICE_CHANGE,
                                       on_change=self.limpia_inputs, read_only=True)
        self.costo_input = ft.TextField(label="Valor", icon=ft.icons.ATTACH_MONEY_SHARP,
                                        input_filter=ft.NumbersOnlyInputFilter(),
                                        on_change=self.limpia_inputs)
        self.tipo_input = ft.Dropdown(
            label="Tipo Tarifa",
            hint_text="Selecciona un tipo?",
            options=[
                ft.dropdown.Option("hora"),
                ft.dropdown.Option("servicio"),
            ],
            autofocus=True,
        )

        # Boton Guardar
        self.save_button = ft.FilledButton(
            content=ft.Container(content=ft.Text(value="Guardar", size=15),
                                 width=150,
                                 padding=10,
                                 alignment=ft.alignment.center,
                                 ),
            on_click=self.save_tarifa,
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

        self.content = ft.Column(controls=[
            self.name_input,
            self.costo_input,
            self.tipo_input,
            ft.Row(controls=[
                self.save_button,
                self.cancel_button
            ])
        ])

    def did_mount(self):
        if self.tarifa is not None:
            self.name_input.value = self.tarifa.get('nombre')
            if self.tarifa['tipo'] in ['hora', 'servicio'] and self.tarifa['nombre'] != 'auto':
                self.name_input.read_only = False

            self.tipo_input.visible = False
            costo_str = str(self.tarifa.get('costo')).rstrip('0').rstrip('.')
            self.costo_input.value = costo_str
            self.save_button.on_click = self.update_tarifa
        else:
            self.name_input.read_only = False

        self.update()

    def cancelar(self, e=None):
        self.page.close(self)

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "tarifa_tipo": r"^(hora|servicio)$",
            "tarifa_nombre": r"^.+$",  # Solo números
            "tarifa_costo": r"^.+$",
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    def save_tarifa(self, e=None):

        if not self.validar_datos(self.name_input.value, "tarifa_nombre"):
            self.name_input.error_text = "Nombre no valido"
            self.update()
            return
        if not self.validar_datos(self.tipo_input.value, "tarifa_tipo"):
            self.tipo_input.value.error_text = "Tipo no valido"
            self.update()
            return
        if not self.validar_datos(self.costo_input.value, "tarifa_costo"):
            self.costo_input.error_text = "Costo no valido"
            self.update()
            return

        resultado = crear_tarifa(nombre=self.name_input.value, tipo=self.tipo_input.value,
                                 costo=float(self.costo_input.value))
        if resultado is True:
            if self.on_complete:
                self.on_complete(True)
        else:
            if self.on_complete:
                self.on_complete(True, resultado)

        self.cancelar()

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()

    def update_tarifa(self, e):

        if not self.validar_datos(self.name_input.value, "tarifa_nombre"):
            self.name_input.error_text = "Nombre no valido"
            self.update()
            return

        if not self.validar_datos(self.costo_input.value, "tarifa_costo"):
            self.costo_input.error_text = "Costo no valido"
            self.update()
            return

        resultado = actualizar_tarifa(tarifa_id=self.tarifa.get('id'), nombre=self.name_input.value,
                                      costo=float(self.costo_input.value))
        if resultado is True:
            if self.on_complete:
                self.on_complete(True)
        else:
            if self.on_complete:
                self.on_complete(True, resultado)

        self.cancelar()


if __name__ == "__main__":
    pass
