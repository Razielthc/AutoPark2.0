import flet as ft
from dotenv import set_key
import os
import logging
from decouple import AutoConfig
from utils.get_resorce_path import resource_path

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config_path = resource_path('.env')
config = AutoConfig(config_path)


class OperationMode(ft.Row):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.expand = True
        self.mode_selected = None
        self.checkbox_manual = ft.Checkbox(on_change=self.seleccionar_modo, key='manual')
        self.checkbox_semiautomatico = ft.Checkbox(on_change=self.seleccionar_modo, key='semi')
        self.checkbox_automatico = ft.Checkbox(on_change=self.seleccionar_modo, key='auto')
        self.group_checkbox = [self.checkbox_manual, self.checkbox_semiautomatico, self.checkbox_automatico]

        self.dlg_modal = ft.AlertDialog(
            modal=True,
        )

        # Definir la tabla con las opciones
        self.tabla_modos = ft.DataTable(
            data_row_max_height=float("inf"),
            columns=[
                ft.DataColumn(label=ft.Text("Seleccionar")),
                ft.DataColumn(label=ft.Text("Modo de Operación")),
                ft.DataColumn(label=ft.Text("Tarifas Múltiples")),
                ft.DataColumn(label=ft.Text("Pantalla de Entrada")),
                ft.DataColumn(label=ft.Text("Impresión de Tickets")),
                ft.DataColumn(label=ft.Text("Apertura de Barreras")),
                ft.DataColumn(label=ft.Text("Hardware Adicional Requerido")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(self.checkbox_manual),
                    ft.DataCell(ft.Text("Manual")),
                    ft.DataCell(ft.Text("Habilitado")),
                    ft.DataCell(ft.Text("Sí")),
                    ft.DataCell(ft.Text("El ticket de entrada se imprime en la impresora del sistema")),
                    ft.DataCell(ft.Text("Manual, Botones físicos")),
                    ft.DataCell(ft.Text("")),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(self.checkbox_semiautomatico),
                    ft.DataCell(ft.Text("Semiautomático")),
                    ft.DataCell(ft.Text("Habilitado")),
                    ft.DataCell(ft.Text("Sí")),
                    ft.DataCell(ft.Text("El ticket de entrada se imprime en la impresora del sistema")),
                    ft.DataCell(ft.Text("Automatico,Software")),
                    ft.DataCell(ft.Text("Controlador de barreras")),
                ]),
                ft.DataRow(cells=[
                    ft.DataCell(self.checkbox_automatico),
                    ft.DataCell(ft.Text("Automático")),
                    ft.DataCell(ft.Text("Deshabilitado")),
                    ft.DataCell(ft.Text("Deshabilitado")),
                    ft.DataCell(ft.Text("El ticket de entrada se imprime en la impresora del dispensador")),
                    ft.DataCell(ft.Text("Automatico , Software")),
                    ft.DataCell(ft.Text("Controlador de barreras y dispensador de tickets")),
                ]),
            ]
        )
        # Botón para guardar la selección
        self.seleccionar_btn = ft.FilledButton(text="Guardar", on_click=self.guarda_config,
                                               style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400))
        self.controls = [ft.Column(controls=[
            self.tabla_modos, self.seleccionar_btn
        ])]

    def did_mount(self):
        try:
            self.mode_selected = config('OPERATION_MODE')
            for control in self.group_checkbox:
                control.value = control.key == self.mode_selected
                control.disabled = control.key == self.mode_selected

            self.update()
        except KeyError as e:
            logger.warning(f"Error al cargar la  configuracion {e}")
            mensaje = (f"Error de Configuración por favor reinicie el sistema"
                       f"si el error continua contacte a soporte {e}")

            self.mostrar_dialogo("Error", mensaje, "error")

    def seleccionar_modo(self, e):
        self.mode_selected = e.control.key
        for control in self.group_checkbox:
            control.value = control.key == self.mode_selected
            control.disabled = control.key == self.mode_selected
        self.update()

    def guarda_config(self, e):
        try:
            # Verificar si el archivo .env existe
            if not os.path.exists(config_path):
                logger.warning(f"archivo .env no encontrado en ruta {config_path}")
                raise FileNotFoundError(f"El archivo .env no se encuentra en la ruta: {config_path}")

            if config('OPERATION_MODE') != self.mode_selected:
                set_key(config_path, 'OPERATION_MODE', str(self.mode_selected))
                set_key(config_path, 'PRINTER_SYSTEM_ENABLED', 'False')
                set_key(config_path, 'PRINTER_ENTRADA_ENABLED', 'False')
                set_key(config_path, 'ARDUINO_ENABLED', 'False')
                # Crear el diccionario de configuración para guardar

                self.mostrar_dialogo("Configuración",
                                     "El modo de operacion ha cambiado la configuracion del hardware se restablecerá", "exito")
        except (FileNotFoundError, KeyError) as e:
            logger.warning(f"Error al guardar la configuracion {e}")
            mensaje = (f"Error de Configuración por favor reinicie el sistema"
                       f"si el error continua contacte a soporte {e}")

            self.mostrar_dialogo("Error", mensaje, "error")

    def mostrar_dialogo(self, titulo, mensaje, tipo):
        self.dlg_modal.title = ft.Text(titulo)
        self.dlg_modal.content = ft.Text(mensaje)
        self.dlg_modal.actions = [ft.TextButton("Si", on_click=self.handle_close, key=tipo)]
        self.dlg_modal.actions_alignment = ft.MainAxisAlignment.END
        self.page.open(self.dlg_modal)

    def handle_close(self, e):
        if e.control.key == "exito":
            self.page.window.destroy()
        elif e.control.key == "error":
            self.page.close(self.dlg_modal)
            self.update()
