import flet as ft

from vistas.frames.datos_config_frame import DatosEstacionamiento
from vistas.frames.device_config_frame import DeviceConfig
from vistas.frames.printer_config_frame import PrinterConfig
from vistas.frames.mail_settings_frame import SettingMail
from vistas.frames.operation_config_frame import OperationMode


class SettingsPage(ft.Column):
    def __init__(self, device=None):
        super().__init__()
        self.device = device
        self.isolated = True
        self.expand = True
        self.t = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Modo de operación",
                    icon=ft.icons.SETTINGS,
                    content=ft.Container(
                        content=ft.Column(
                            controls=[ft.Text(value="Modo de operación", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                                      ft.Divider(height=9, thickness=3),
                                      OperationMode()])
                    ),
                ),
                ft.Tab(
                    text="Configuracion de Impresoras",
                    icon=ft.icons.LOCAL_PRINT_SHOP_ROUNDED,
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Configuracion de Impresoras", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                            ft.Divider(height=9, thickness=3),
                            PrinterConfig()]
                    ),
                ),
                ft.Tab(
                    text="Configuracion Controlador",
                    icon=ft.icons.SETTINGS_REMOTE,
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Configuracion del Controlador", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                            ft.Divider(height=9, thickness=3),
                            DeviceConfig(device=self.device)]
                    ),
                ),
                ft.Tab(
                    text="Datos del estacionamiento",
                    icon=ft.icons.FACT_CHECK,
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Datos del estacionamiento", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                            ft.Divider(height=9, thickness=3),
                            DatosEstacionamiento()]
                    ),
                ),
                ft.Tab(
                    text="Correo del sistema",
                    icon=ft.icons.CONTACT_MAIL,
                    content=ft.Column(
                        controls=[
                            ft.Text(value="Correo para envio de reportes", theme_style=ft.TextThemeStyle.DISPLAY_SMALL),
                            ft.Divider(height=9, thickness=3),
                            SettingMail()]
                    ),
                ),
            ],
            expand=1
        )
        self.controls = [self.t]

    def will_unmount(self):
        self.controls.clear()


if __name__ == "__main__":
    pass
