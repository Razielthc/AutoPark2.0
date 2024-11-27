import logging
import flet as ft

from procedimientos.inicializador import inicializar_sistema
from utils.control_barreras import Device
from utils.get_size_monitor import size_monitor
from vistas.app_bar import BarPagina
from vistas.carga_sistema_page import CargaSistema
from vistas.contenedor_vistas import Contenedorprincipal
from vistas.login_page import LoginPage
from utils.get_resorce_path import resource_path

try:
    logging.basicConfig(
        filename='mi_app.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    )
    logging.info("Iniciando el logging correctamente")
except Exception as e:
    print(f"Error al configurar el logging: {e}")


def main(page: ft.Page):
    logging.info('Inicio del sistema')
    page.title = "AutoParkMX"
    page.fonts = {
        "Lato": "/fonts/Lato-Regular.ttf"
    }
    page.theme = ft.Theme(font_family="Lato")
    width_monitor, height_monitor = size_monitor()
    page.window.width = width_monitor * 4 // 8
    page.window.height = height_monitor * 4 // 8
    page.window.center()
    page.window.resizable = False
    page.window.maximizable = False

    # clases de inicio
    contenedor_carga = CargaSistema()
    login_page = LoginPage()
    app_bar_pagina = BarPagina()

    dlg_alerta = ft.AlertDialog()

    page.add(contenedor_carga)

    def muestra_mensaje(title, mensaje, tipo):
        dlg_alerta.titulo = ft.Text(value=title)
        dlg_alerta.mensaje = mensaje

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

        dlg_alerta.content = contenido
        page.open(dlg_alerta)

    device = Device(muestra_mensaje=muestra_mensaje, agrega_notificacion=app_bar_pagina.agrega_notificacion)
    right_column = Contenedorprincipal(device=device)

    def cerrar_ventana(e):
        if e.data == "close":
            device.logout()
            page.window.destroy()

    page.window.prevent_close = True
    page.window.on_event = cerrar_ventana

    async def start_sistema():
        logging.info('Comienza la inicializacion del sistema')
        # Ejecuta la inicialización de forma asíncrona
        resultado, modo = await inicializar_sistema(device)
        logging.info('Finaliza la inicializacion')
        if resultado is True:
            logging.debug('No hay errores en la inializacion')
            page.clean()
            page.add(login_page)
            await login_page.esperar_login()
            logging.info('Se carga Login')
        else:
            logging.info('Errores en la initialization')
            await contenedor_carga.muestra_errores(resultado)
            await contenedor_carga.esperar_boton()
            page.clean()
            logging.info('Se limpian los errores')
            page.add(login_page)
            logging.info('Se carga Login')
            await login_page.esperar_login()

        page.window.resizable = True
        page.window.maximizable = True
        page.window.maximized = True
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.controls.clear()
        page.views.clear()
        logging.info('Se limpian los controles del login y de la ventana de errores')
        page.views.append(ft.View(
            "/",
            appbar=app_bar_pagina,
            controls=[right_column]
        ))
        logging.info('Se agrega los nuevos controles')
        page.update()
        page.on_route_change = right_column.route_change

    page.run_task(start_sistema)
    logging.debug('Se crea entra en el bucle principal del programa')


if __name__ == "__main__":
    ft.app(target=main, assets_dir=resource_path("./assets"))
