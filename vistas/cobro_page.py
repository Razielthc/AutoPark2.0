import flet as ft

from models.model_aperturas import autos_dentro
from procedimientos.corte_x import nuevo_corte_x
from procedimientos.corte_z import nuevo_corte_z
from procedimientos.imprime_corte import imprime_corte
from procedimientos.reimprime_ticket import reimprime_no_impresos
from procedimientos.ticket_perdido import nuevo_ticket_perdido
from vistas.frames.egreso_dlg_frame import EgresoDlg
from vistas.frames.entrada_frame import EntradaFrame
from vistas.frames.salida_frame import SalidaFrame


class CobroPage(ft.Column):
    def __init__(self, device=None, usuario=None, modo_operacion=None):
        super().__init__()
        self.device = device
        self.isolated = True
        self.expand = True
        self.corte = None
        self.usuario = usuario
        self.modo_operacion = modo_operacion
        self.total_autos = ft.Text(value=f"{autos_dentro()} vehículo(s)", size=20)
        self.autos = ft.Column(
            controls=[ft.Text(value="Autos dentro", size=20),
                      ft.Row(controls=[ft.Icon(ft.icons.DIRECTIONS_CAR_FILLED_SHARP),
                                       self.total_autos])],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.entrada = EntradaFrame(self)
        self.salida = SalidaFrame(self)
        self.input_code_bar = ft.TextField(icon=ft.icons.QR_CODE_SCANNER_OUTLINED,
                                           on_submit=self.salida.actualiza_info_ticket,
                                           autofocus=True,
                                           input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9#\-: ]*$",
                                                                       # Patrón para números, '#', '-', ':', y espacio
                                                                       replacement_string=""
                                                                       # Reemplaza caracteres no permitidos con una cadena vacía
                                                                       ),
                                           width=600,
                                           text_size=30
                                           )
        self.dlg = ft.AlertDialog(on_dismiss=self.actualiza_vista)
        self.dlg_modal_corte = ft.AlertDialog(
            modal=True,
            title=ft.Text("Imprimir el Corte"),
            content=ft.Text("Desea imprimir el corte ?"),
            actions=[
                ft.TextButton("Si", on_click=self.imprimir_corte,
                              style=ft.ButtonStyle(color=ft.colors.GREEN_ACCENT_400)),
                ft.TextButton("No", on_click=self.cierra_modal_corte,
                              style=ft.ButtonStyle(color=ft.colors.RED_ACCENT_400)),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,

        )
        self.row_btn_acciones = ft.Row(spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        # Pasar self (CobroPage) a las instancias de EntradaFrame y SalidaFrame
        self.controls = [
            ft.Row(controls=[self.autos, self.input_code_bar], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
            self.row_btn_acciones,
            ft.Row(controls=[self.entrada, self.salida], expand=True)
        ]

    def did_mount(self):
        self.carga_modo_operacion()

    def carga_modo_operacion(self):
        botones = []
        if self.modo_operacion != "manual":
            botones.extend([
                ft.ElevatedButton(content=ft.Text(value="Corte Parcial", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c1",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Corte Final", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c2",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Reimprime Ticket/s", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c3",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Ticket Perdido", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c4",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#ff8c00", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Retirar Efectivo", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c5",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#ff8c00", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Abre entrada", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c6",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#ffcc00", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Abre salida", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c7",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_200,
                                                       shape=ft.RoundedRectangleBorder(radius=10)))
            ])
        else:
            botones.extend([
                ft.ElevatedButton(content=ft.Text(value="Corte Parcial", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c1",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Corte Final", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c2",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Reimprime Ticket/s", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c3",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#006699", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Ticket Perdido", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c4",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#ff8c00", shape=ft.RoundedRectangleBorder(radius=10))),

                ft.ElevatedButton(content=ft.Text(value="Retirar Efectivo", size=18, color=ft.colors.WHITE,
                                                  text_align=ft.TextAlign.CENTER),
                                  key="c5",
                                  on_click=self.ejecuta_commando,
                                  style=ft.ButtonStyle(bgcolor="#ff8c00", shape=ft.RoundedRectangleBorder(radius=10)))
            ])
        self.row_btn_acciones.controls = botones
        self.update()

    def actualiza_vista(self, e):
        self.total_autos.value = f"{autos_dentro()} vehículo(s)"
        self.input_code_bar.value = None
        self.input_code_bar.focus()
        # Recorremos los controles y verificamos si son instancias de ft.Column
        for control in self.entrada.card_botones.content.content.controls:
            if isinstance(control, ft.Column):
                # Eliminamos el control que es una instancia de ft.Column
                self.entrada.card_botones.content.content.controls.remove(control)
                break  # Opcional: Si solo deseas eliminar la primera instancia, usas break

        # Finalmente, refrescas la vista
        self.update()

    def muestra_mensaje(self, title, mensaje, tipo):
        self.dlg.titulo = ft.Text(value=title)
        self.dlg.mensaje = mensaje

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

        self.dlg.content = contenido
        self.page.open(self.dlg)

    def ejecuta_commando(self, e):
        if e.control.key == "c1":

            try:
                for control in self.entrada.card_botones.content.content.controls:
                    if isinstance(control, ft.Column):
                        # Eliminamos el control que es una instancia de ft.Column
                        self.entrada.card_botones.content.content.controls.remove(control)
                        break  # Opcional: Si solo deseas eliminar la primera instancia, usas break
                self.corte = nuevo_corte_x(self.usuario[2])
                self.entrada.card_botones.content.content.controls.append(
                    ft.Column(
                        controls=[ft.Text(value=f"Corte {self.corte['tipo']} No.{self.corte['id']} ",
                                          weight=ft.FontWeight.BOLD, size=30),
                                  ft.Text(self.corte["c_salida"])], expand=True))
                self.entrada.update()
                self.page.open(self.dlg_modal_corte)
            except Exception as error:
                self.muestra_mensaje("Error al crear corte Parcial", mensaje=error, tipo="error")

        elif e.control.key == "c2":

            try:
                for control in self.entrada.card_botones.content.content.controls:
                    if isinstance(control, ft.Column):
                        # Eliminamos el control que es una instancia de ft.Column
                        self.entrada.card_botones.content.content.controls.remove(control)
                        break  # Opcional: Si solo deseas eliminar la primera instancia, usas break
                self.corte = nuevo_corte_z(self.usuario[2])
                self.entrada.card_botones.content.content.controls.append(
                    ft.Column(
                        controls=[ft.Text(value=f"Corte {self.corte['tipo']} No.{self.corte['id']} ",
                                          weight=ft.FontWeight.BOLD, size=30),
                                  ft.Text(self.corte["c_salida"])], expand=True))
                self.entrada.update()
            except Exception as error:
                self.muestra_mensaje("Error al crear corte Total", mensaje=error, tipo="error")

        elif e.control.key == "c3":

            try:
                reimprime_no_impresos()
            except Exception as error:
                self.muestra_mensaje("Error", mensaje=error, tipo="error")

        elif e.control.key == "c4":

            try:
                ticket = nuevo_ticket_perdido(self.usuario[2])
                self.salida.cobra_ticket_perdido(e, ticket)
            except Exception as error:
                self.muestra_mensaje("Error", mensaje=error, tipo="error")

        elif e.control.key == "c5":

            try:
                self.page.open(EgresoDlg(usuario_id=self.usuario[2]))
            except Exception as error:
                self.muestra_mensaje("Error", mensaje=error, tipo="error")

        elif e.control.key == "c6":

            try:
                self.device.abrir_pluma(0, "entrada manual")
                self.muestra_mensaje("Comando Enviado", mensaje="Se abrio la entrada", tipo="exito")
            except (Exception, ValueError, SystemError) as error:
                self.muestra_mensaje("Error al abrir la barrera", mensaje=error, tipo="error")

        elif e.control.key == "c7":

            try:
                self.device.abrir_pluma(1, "salida manual")
                self.muestra_mensaje("Comando Enviado", mensaje="Se abrio la salida", tipo="exito")
            except (Exception, ValueError, SystemError, ConnectionError) as error:
                self.muestra_mensaje("Error al abrir la barrera", mensaje=error, tipo="error")

    def imprimir_corte(self, e):
        try:
            if self.corte is not None:
                imprime_corte(self.corte)
                self.cierra_modal_corte(e)
        except Exception as error:
            self.muestra_mensaje("Error al imprimir el Corte", mensaje=error, tipo="error")

    def cierra_modal_corte(self, e):
        self.page.close(self.dlg_modal_corte)
        self.corte = None
        # self.actualiza_vista(e)


if __name__ == "__main__":
    pass
