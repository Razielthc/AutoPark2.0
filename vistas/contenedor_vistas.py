import flet as ft
import logging
from decouple import AutoConfig
from vistas.Nav_left import Navleft
from vistas.clientes_page import ClientesPage
from vistas.cobro_page import CobroPage
from vistas.home_page import DashboardPage
from vistas.planes_page import PlanesPage
# from vistas.report_page import ReportPage
from vistas.settings_page import SettingsPage
from vistas.tarifas_page import TarifasPage
from vistas.users_page import UserPage
from utils.get_resorce_path import resource_path

config = AutoConfig(resource_path('.env'))

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


class Contenedorprincipal(ft.Row):
    def __init__(self, device):
        super().__init__()
        self.isolated = True
        self.expand = True
        self.device = device
        self.usuario = None
        self.modo_operacion = None

        self.controls = [
            Navleft(),
            ft.VerticalDivider(width=2),
            ft.Column()
        ]

    def did_mount(self):
        self.usuario = self.page.session.get('usuario')
        self.modo_operacion = config('OPERATION_MODE')

    def route_change(self, e):
        try:
            self.controls = self.controls[:2]

            if e.route == "/":
                self.controls.append(DashboardPage(self.usuario))
            elif e.route == "/cobro":
                self.controls.append(
                    CobroPage(device=self.device, usuario=self.usuario, modo_operacion=self.modo_operacion))
            elif e.route == "/clientes":
                self.controls.append(ClientesPage(usuario=self.usuario, device=self.device))
            elif e.route == "/planes":
                self.controls.append(PlanesPage(usuario_id=self.usuario[2], device=self.device))
            elif e.route == "/tarifas":
                self.controls.append(TarifasPage())
            # elif e.route == "/report":
            #     self.controls.append(ReportPage())
            elif e.route == "/users":
                self.controls.append(UserPage())
            elif e.route == "/settings":
                self.controls.append(SettingsPage(device=self.device))

            self.update()
        except Exception as e:
            logger.warning(f"Error al cargar la vista{e}")
