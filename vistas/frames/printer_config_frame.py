import asyncio
import flet as ft
import logging
import win32print
from dotenv import set_key
import os
from decouple import AutoConfig
from utils.test_printer import verificar_impresora
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config_path = resource_path('.env')
config = AutoConfig(config_path)


class PrinterConfig(ft.Row):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.expand = True
        self.dlg_modal = ft.AlertDialog()
        self.checkbox_system_printer = ft.Checkbox(on_change=self.enable_input, key='check_system')
        self.input_printer_system = ft.Dropdown(width=300, label="Impresora del sistema",
                                                on_change=self.limpia_error_input)
        self.grupo_inputs_printer_system = [self.checkbox_system_printer, self.input_printer_system,
                                            ft.FilledButton(text="Probar", on_click=lambda e: asyncio.run(
                                                self.probar_hardware("printer_system")),
                                                            key="printer_system"),
                                            ft.FilledButton(text="guardar", key="printer_system",
                                                            on_click=self.guarda_config,
                                                            style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400))]
        self.checkbox_entrada_printer = ft.Checkbox(on_change=self.enable_input, key='check_entrada')
        self.input_printer_entrada = ft.TextField(label="Impresora dispensador", helper_text="Introduce la IP",
                                                  on_change=self.limpia_error_input)
        self.grupo_inputs_printer_entrada = [self.checkbox_entrada_printer, self.input_printer_entrada,
                                             ft.FilledButton(text="Probar", on_click=lambda e: asyncio.run(
                                                 self.probar_hardware("printer_entrada")),
                                                             key="printer_entrada"),
                                             ft.FilledButton(text="guardar", key="printer_entrada",
                                                             on_click=self.guarda_config,
                                                             style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400))]

        self.row1 = ft.Row(self.grupo_inputs_printer_system, spacing=50, alignment=ft.MainAxisAlignment.START)
        self.row2 = ft.Row(self.grupo_inputs_printer_entrada, spacing=50, alignment=ft.MainAxisAlignment.START,
                           visible=False)

        self.inputs_container = ft.Column(
            controls=[self.row1, self.row2])
        self.controls = [
            self.inputs_container
        ]

    def did_mount(self):
        self.listar_impresoras()
        self.carga_configuracion()

    def enable_input(self, e):
        control_map = {
            "check_system": self.grupo_inputs_printer_system[2:],
            "check_entrada": self.grupo_inputs_printer_entrada[2:]
        }
        controls = control_map.get(e.control.key, [])
        for control in controls:
            control.visible = e.control.value
        self.update()

    def listar_impresoras(self):
        """Lista todas las impresoras instaladas en el sistema."""
        printers = []
        printer_enum = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 2)

        for printer in printer_enum:
            printers.append(printer['pPrinterName'])  # El nombre de la impresora está en el índice 2

        self.input_printer_system.options = [ft.dropdown.Option(str(printer)) for printer in printers]
        self.update()

    async def probar_hardware(self, dispositivo):
        if dispositivo == "printer_system":
            if self.input_printer_system.value and self.input_printer_system.value.strip():
                # Mostrar el modal con el ProgressRing
                await self.muestra_mensaje(title="Verificando", mensaje="Por favor, espere...", tipo="progreso")

                resultado = await verificar_impresora(printer_type="printer_system",
                                                      name=self.input_printer_system.value)
                await self.actualizar_mensaje(resultado)
            else:
                self.input_printer_system.error_text = "Selecciona una impresora"
                self.update()

        elif dispositivo == "printer_entrada":
            if self.input_printer_entrada.value and self.input_printer_entrada.value.strip():
                # Mostrar el modal con el ProgressRing
                await self.muestra_mensaje(title="Verificando", mensaje="Por favor, espere...", tipo="progreso")

                resultado = await verificar_impresora(printer_type="printer_entrada",
                                                      port=self.input_printer_entrada.value)
                await self.actualizar_mensaje(resultado)
            else:
                self.input_printer_entrada.error_text = "Introduce una IP"
                self.update()

    async def actualizar_mensaje(self, resultado):
        if resultado is True:
            await self.muestra_mensaje(title="Prueba Exitosa", mensaje="La prueba ha resultado exitosa", tipo="exito")
        else:
            await self.muestra_mensaje(title="Error", mensaje=resultado, tipo="error")

    async def muestra_mensaje(self, title, mensaje, tipo):
        if tipo == "progreso":
            contenido = ft.Column(
                [ft.ProgressRing(height=100, width=100, stroke_width=5)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                height=200,
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            icono = ft.Icon(ft.icons.CHECK_CIRCLE_ROUNDED, color=ft.colors.GREEN_ACCENT_400, size=150)
            if tipo == "error":
                icono = ft.Icon(ft.icons.ERROR_ROUNDED, color=ft.colors.RED_ACCENT_400, size=150)
            contenido = ft.Column(
                controls=[icono, ft.Text(value=mensaje)],
                height=200,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )

        self.dlg_modal.title = ft.Text(value=title)
        self.dlg_modal.content = contenido
        self.page.open(self.dlg_modal)

    def carga_configuracion(self):

        modo_operacion = config('OPERATION_MODE')

        if config('PRINTER_SYSTEM_ENABLED', cast=bool):
            self.checkbox_system_printer.value = True
            self.checkbox_system_printer.disabled = True
            self.input_printer_system.value = config('PRINTER_SYSTEM_NAME')
        else:
            self.checkbox_system_printer.value = False
            self.enable_input(ft.ControlEvent(control=self.checkbox_system_printer, target="", data="",
                                              page=self.page, name="on_changue"))

        if modo_operacion == "auto":
            self.row2.visible = True

            if config('PRINTER_ENTRADA_ENABLED', cast=bool):
                self.checkbox_entrada_printer.value = True
                self.checkbox_entrada_printer.disabled = True
                self.input_printer_entrada.value = config('PRINTER_ENTRADA_PORT')
            else:
                self.checkbox_entrada_printer.value = False
                self.enable_input(ft.ControlEvent(control=self.checkbox_entrada_printer, target="", data="",
                                                  page=self.page, name="on_changue"))
        self.update()

    def guarda_config(self, e):
        try:
            # Verificar si el archivo .env existe
            if not os.path.exists(config_path):
                logger.warning(f"archivo .env no encontrado en ruta {config_path}")
                raise FileNotFoundError(f"El archivo .env no se encuentra en la ruta: {config_path}")

            # Verifica si la key es "printer_system" y el input no está vacío
            if e.control.key == "printer_system" and self.input_printer_system.value and self.input_printer_system.value.strip():
                set_key(config_path, 'PRINTER_SYSTEM_ENABLED', str(self.checkbox_system_printer.value))
                set_key(config_path, 'PRINTER_SYSTEM_NAME', self.input_printer_system.value)

            # Verifica si la key es "printer_entrada" y el input no está vacío
            elif e.control.key == "printer_entrada" and self.input_printer_entrada.value and self.input_printer_entrada.value.strip():
                set_key(config_path, 'PRINTER_ENTRADA_ENABLED', str(self.checkbox_entrada_printer.value))
                set_key(config_path, 'PRINTER_ENTRADA_PORT', self.input_printer_entrada.value)

            asyncio.run(self.muestra_mensaje(title="Configuracion Guardada",
                                             mensaje="Se ha guardado la configuracion es necesario reiniciar",
                                             tipo="exito"))

        except FileNotFoundError as e:
            asyncio.run(self.muestra_mensaje(title="Error", mensaje=e, tipo="error"))

        except Exception as e:
            asyncio.run(self.muestra_mensaje(title="Error", mensaje=e, tipo="error"))

    def limpia_error_input(self, e):
        e.control.error_text = None
        self.update()


if __name__ == "__main__":
    pass
