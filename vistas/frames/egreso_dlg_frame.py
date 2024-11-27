import flet as ft

from models.model_egresos import crear_egreso


class EgresoDlg(ft.AlertDialog):
    def __init__(self, usuario_id=None):
        super().__init__()
        self.usuario_id = usuario_id
        self.isolated = True
        self.modal = True
        self.content_padding = 30
        self.icon = ft.Icon(ft.icons.PAYMENTS_SHARP)
        self.title = ft.Text("Retiro de efectivo")
        self.category_dropdown = ft.Dropdown(
            label="Categoría de Egreso",
            options=[
                ft.dropdown.Option("Servicios Básicos"),
                ft.dropdown.Option("Mantenimiento"),
                ft.dropdown.Option("Suministros"),
                ft.dropdown.Option("Personal"),
                ft.dropdown.Option("Gastos Administrativos"),
                ft.dropdown.Option("Marketing y Promoción"),
                ft.dropdown.Option("Seguridad"),
                ft.dropdown.Option("Otros"),
            ]
        )
        self.description_input = ft.TextField(
            label="Descripción del Egreso",
            hint_text="Ejemplo: Pago de CFE, compra de papelería, etc.",
        )
        self.amount_input = ft.TextField(
            label="Monto del Egreso",
            hint_text="Ingresa el monto en pesos",
            input_filter=ft.NumbersOnlyInputFilter()
        )
        self.content = ft.Column(
            controls=[
                self.category_dropdown,
                self.description_input,
                self.amount_input,
                ft.Row(
                    controls=[
                        ft.FilledButton(
                            text="Confirmar",
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_ACCENT_400,
                                color="white"
                            ),
                            on_click=self.confirm_egreso
                        ),
                        ft.OutlinedButton(
                            text="Cancelar",
                            on_click=self.cancel_modal
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            height=400,
            width=500
        )

    def confirm_egreso(self, e):
        try:
            # Validar los campos
            if not self.category_dropdown.value:
                self.category_dropdown.error_text = "Selecciona una categoría"
                self.update()
                return

            if not self.description_input.value.strip():
                self.description_input.error_text = "La descripción es obligatoria"
                self.update()
                return

            if not self.amount_input.value.strip():
                self.amount_input.error_text = "El monto es obligatorio"
                self.update()
                return

            # Intentar crear el egreso
            crear_egreso(
                monto=float(self.amount_input.value),
                tipo=self.category_dropdown.value,
                descripcion=self.description_input.value.strip(),
                usuario_id=self.usuario_id
            )

            self.page.close(self)

        except Exception as error:
            # Elevar la excepción al contexto superior
            raise Exception(f"Error al crear el egreso: {error}")

    def cancel_modal(self, e):
        self.page.close(self)
