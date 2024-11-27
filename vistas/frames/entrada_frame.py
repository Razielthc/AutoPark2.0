import flet as ft

from models.model_tarifas import leer_tarifas
from procedimientos.crea_entrada import nueva_entrada


class EntradaFrame(ft.Column):
    def __init__(self, cobro_page):
        super().__init__()
        self.cobro_page = cobro_page
        self.device = None
        self.alignment = ft.MainAxisAlignment.SPACE_EVENLY
        self.isolated = True
        self.usuario = self.cobro_page.usuario
        self.modo_operacion = self.cobro_page.modo_operacion
        self.expand = True
        self.row_botones = ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                                  vertical_alignment=ft.CrossAxisAlignment.CENTER
                                  )

        self.card_botones = ft.Card(
            content=ft.Container(
                content=ft.Column(controls=[self.row_botones], expand=True),
                expand=True,
            ), expand=True
        )

        self.controls = [self.card_botones]

    def did_mount(self):
        if self.modo_operacion != "auto":
            self.crea_botones()

        if self.modo_operacion != "manual":
            self.device = self.cobro_page.device

    def crea_botones(self):
        tarifas = leer_tarifas()
        botones = []
        if isinstance(tarifas, list):
            for tarifa in tarifas:
                if tarifa['name'] != "ticket perdido":
                    botones.append(
                        ft.ElevatedButton(content=ft.Text(value=tarifa['name'], size=30, color=ft.colors.WHITE,
                                                          text_align=ft.TextAlign.CENTER),
                                          data=tarifa,
                                          on_click=self.entrada,
                                          style=ft.ButtonStyle(bgcolor="#0099cc",
                                                               shape=ft.RoundedRectangleBorder(radius=10)))
                    )

        self.row_botones.controls = botones

        self.update()

    def entrada(self, e):
        try:
            nueva_entrada(tarifa_name=e.control.data['name'], tarifa_valor=e.control.data['valor'],
                          user_id=self.usuario[2])
            self.device.abrir_pluma(0, "sistema")
            self.cobro_page.muestra_mensaje(title="Nueva entrada", mensaje="Nueva entrada registrada", tipo="exito")
        except Exception as e:
            self.cobro_page.muestra_mensaje(title="Error", mensaje=str(e), tipo="error")


if __name__ == "__main__":
    pass
