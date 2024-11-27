import asyncio
import logging
import flet as ft

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)


class CargaSistema(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.boton_event = asyncio.Event()
        self.status_text = ft.Text("Iniciando Sistema", size=30)
        self.progresbar = ft.ProgressBar(height=20)
        self.dlg_aviso = ft.AlertDialog()
        self.colum_progresbar = ft.Column([ft.Text("Cargando..."), self.progresbar])
        self.controls = [self.status_text, self.colum_progresbar]
        self.expand = True
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        self.column_errores = ft.Column()
        self.boton = ft.Row(
            controls=[ft.ElevatedButton(content=ft.Text(value="Entrar", size=30),
                                        on_click=self.carga_login,
                                        color="WHITE",
                                        bgcolor=ft.colors.GREEN_ACCENT_200)]
            , expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.END

        )

    async def muestra_errores(self, errores):
        logger.info('Se inicia ventana de errores')
        if not isinstance(errores, (list, tuple)):
            self.muestra_mensaje(errores)
            return

        self.status_text.value = "Errores durante la inicialización: Revise los mensajes y contacte a soporte"
        num_errores = len(errores)

        if num_errores > 0:
            # Iniciamos la barra de progreso
            logger.info('Se aumenta el progresbar para mostrar despues los errores')
            incremento = 1 / num_errores
            self.progresbar.value = 0

            for i, error in enumerate(errores):
                logger.info('bucle del progres bar')
                self.progresbar.value += incremento
                self.column_errores.controls.append(ft.Text(f" {i} - {error}", color="red", size=20))
                self.update()
                await asyncio.sleep(1)

            # Ocultamos la barra de progreso y mostramos los errores
            logger.debug('Se muestran los errores')
            self.controls.remove(self.colum_progresbar)
        else:
            # Si no hay errores, mostramos un mensaje más amigable
            logger.info('No hay errores que mostrar')
            self.controls.remove(self.colum_progresbar)
            self.status_text.value = "Inicialización exitosa"

        self.controls.append(self.column_errores)
        self.controls.append(self.boton)
        self.alignment = ft.MainAxisAlignment.START
        self.update()

    def carga_login(self, e):
        logger.info('Finaliza la ventana de errores')
        self.boton_event.set()  # Marca el evento como completado

    async def esperar_boton(self):
        await self.boton_event.wait()

    def muestra_mensaje(self, mensaje):
        self.dlg_aviso.modal = True
        self.dlg_aviso.title = ft.Text("Error Fatal")
        self.dlg_aviso.content = ft.Column(controls=[
            ft.Icon(ft.icons.DANGEROUS),
            ft.Text(
                f"No se encontraron los archivos necesarios para la ejecucion del programa contacte a soporte {mensaje}")
        ])
        self.dlg_aviso.actions = [ft.TextButton("Aceptar", on_click=self.cierra_programa)]
        self.page.open(self.dlg_aviso)

    def cierra_programa(self, e):
        self.page.window.destroy()
