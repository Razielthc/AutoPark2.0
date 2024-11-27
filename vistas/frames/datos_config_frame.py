import flet as ft

from models.model_datos import leer_datos, actualizar_datos


class DatosEstacionamiento(ft.Row):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.width = 500
        self.control_calling = None
        self.dlg = ft.AlertDialog()
        self.input_nombre = ft.TextField(label="Nombre de Estacionamiento", on_change=self.limpia_inputs, expand=True)
        self.input_direccion = ft.TextField(label="Direccion", on_change=self.limpia_inputs)
        self.input_telefono = ft.TextField(label="Telefono", on_change=self.limpia_inputs)
        self.input_apertura = ft.TextField(label="Hora de apertura", on_focus=self.open_data_picker)
        self.input_cierre = ft.TextField(label="Hora de cierre", on_focus=self.open_data_picker)
        self.time_picker = ft.TimePicker(
            confirm_text="Aceptar",
            cancel_text="Cancelar",
            error_invalid_text="Tiempo fuera de rango",
            help_text="Elige el horario",
            on_change=self.handle_change,
            on_dismiss=self.handle_close,
            time_picker_entry_mode=ft.TimePickerEntryMode.INPUT_ONLY
        )
        self.btn_guardar = ft.FilledButton(text="Guardar", style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                                           on_click=self.guardar)
        self.controls = [ft.Column(
            controls=[
                ft.Row([self.input_nombre]),
                ft.Row([self.input_direccion,
                        self.input_telefono]),
                ft.Row([self.input_apertura,
                        self.input_cierre]),
                self.btn_guardar
            ],
            expand=True
        )]

    def did_mount(self):
        self.carga_datos()

    def handle_change(self, e):
        self.control_calling.value = e.control.value
        self.handle_close(e)

    def handle_close(self, e):
        # Check if TimePicker was closed using the "X" button
        if not e.control.open:
            self.btn_guardar.focus()
            self.control_calling.disabled = False
            self.update()

    def open_data_picker(self, e):
        self.control_calling = e.control
        e.control.disabled = True
        self.update()
        self.page.open(self.time_picker)

    def carga_datos(self):
        resultado = leer_datos()
        if isinstance(resultado, dict):
            self.input_nombre.value = resultado['nombre']
            self.input_direccion.value = resultado['direccion']
            self.input_telefono.value = resultado['telefono']
            hora = resultado['horario'].split('-')
            self.input_apertura.value = hora[0]
            self.input_cierre.value = hora[1]
            self.update()

    def limpia_inputs(self, e):
        e.control.error_text = None
        self.update()

    def muestra_mensaje(self, titulo, mensaje, tipo):
        if tipo == "error":
            icono = ft.Icon(ft.icons.ERROR_ROUNDED, color=ft.colors.RED_ACCENT_400, size=150)
        else:
            icono = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=ft.colors.GREEN_ACCENT_400, size=150)
        contenido = ft.Column(
            controls=[icono, ft.Text(value=mensaje)],
            height=200,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.dlg.title = ft.Text(value=titulo)
        self.dlg.content = contenido
        self.page.open(self.dlg)

    def guardar(self, e):
        validacion = True
        inputs = [self.input_nombre, self.input_direccion, self.input_telefono, self.input_apertura, self.input_cierre]

        for entrada in inputs:
            if not entrada.value or len(str(entrada.value)) < 5:
                entrada.error_text = "El campo debe tener al menos 5 caracteres"
                validacion = False

        if validacion:
            resultado = actualizar_datos(
                nombre=self.input_nombre.value,
                direccion=self.input_direccion.value,
                telefono=self.input_telefono.value,
                horario=f"{str(self.input_apertura.value)}-{str(self.input_cierre.value)}"
            )
            if resultado is True:
                self.muestra_mensaje(titulo="Éxito", mensaje="Datos guardados con éxito", tipo="exito")
            else:
                self.muestra_mensaje(titulo="Error", mensaje=resultado, tipo="error")
        else:
            self.update()
