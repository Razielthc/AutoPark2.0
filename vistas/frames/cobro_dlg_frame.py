import flet as ft

from models.model_ingresos import crear_ingreso


class CobroDlg(ft.AlertDialog):
    def __init__(self, total=None, referencia_tipo=None, referencia_id=None, tipo=None, usuario_id=None,
                 on_complete=None):
        super().__init__()
        self.referencia_tipo = referencia_tipo
        self.id = referencia_id
        self.tipo = tipo
        self.usuario = usuario_id
        self.cambio = None
        self.total_a_cobrar = total
        self.on_complete = on_complete  # Callback para notificar el resultado

        self.input_cobro = ft.TextField(
            icon=ft.icons.ATTACH_MONEY,
            label="Ingresa el monto recibido",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.modal = True
        self.icon = ft.Icon(ft.icons.PAYMENTS_SHARP)
        self.title = ft.Text("Ventana de Cobro")
        self.content = ft.Column(
            controls=[
                ft.Text(f"Total a cobrar ${self.total_a_cobrar}", weight=ft.FontWeight.BOLD, size=30),
                self.input_cobro,
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            content=ft.Text(value="ACEPTAR", size=20),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_ACCENT_400,
                                color="WHITE"
                            ),
                            on_click=self.verifica_cobro
                        )
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            height=250
        )

    def verifica_cobro(self, e):

        if not self.input_cobro.value.strip():
            self.input_cobro.error_text = "Ingresa un Monto"

            self.update()
        else:
            monto_ingresado = float(self.input_cobro.value)
            if monto_ingresado < self.total_a_cobrar:

                self.input_cobro.error_text = "El monto ingresado es menor"
                self.update()
            else:

                try:
                    self.cambio = monto_ingresado - self.total_a_cobrar

                    crear_ingreso(monto=self.total_a_cobrar, tipo=self.tipo, referencia_id=self.id,
                                  referencia_tipo=self.referencia_tipo, usuario_id=self.usuario)

                    # Notificar al callback con el resultado
                    if self.on_complete:
                        self.on_complete(self.cambio, True)

                    # Cerrar el modal
                    self.cierra_modal_cobro(e)
                except Exception as error:
                    # Notificar al callback con el resultado
                    if self.on_complete:
                        self.on_complete(self.cambio, False, error)

    def cierra_modal_cobro(self, e):
        self.page.close(self)


if __name__ == "__main__":
    pass
