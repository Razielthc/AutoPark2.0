import re
from datetime import datetime

import flet as ft

from models.model_ingresos import crear_ingreso
from models.model_ticket import busca_ticket
from procedimientos.crea_salida import nueva_salida
from vistas.frames.cobro_dlg_frame import CobroDlg


class SalidaFrame(ft.Column):
    def __init__(self, cobro_page):
        super().__init__()
        # se establecen las propiedades de la vista
        self.cobro_page = cobro_page
        self.device = None
        self.usuario = self.cobro_page.usuario
        self.modo_operacion = self.cobro_page.modo_operacion
        self.expand = True
        self.isolated = True
        self.hora_salida = None
        self.ticket_total = None
        self.ticket = None
        self.cambio = 0
        self.alignment = ft.MainAxisAlignment.START
        self.spacing = 20
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.btn_cobrar = ft.FilledButton(content=ft.Text(value="COBRAR", size=30),
                                          style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400, color="WHITE"),
                                          visible=False,
                                          key="c10",
                                          on_click=self.muestra_modal_cobro)

        self.ticket_info = ft.Row(expand=True)
        self.card_ticket = ft.Card(content=ft.Column(controls=[self.ticket_info, self.btn_cobrar],
                                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                   expand=True)
        self.controls = [self.card_ticket]

    def did_mount(self):
        if self.modo_operacion != "manual":
            self.device = self.cobro_page.device

    def actualiza_info_ticket(self, e):

        # Validar que el código del ticket tenga el formato esperado
        ticket_code = e.control.value.strip()

        # Usamos una expresión regular para verificar el formato "47#2024-09-08 00:29:33"
        pattern = r"^\d+#\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        if not re.match(pattern, ticket_code):
            # Si no coincide, muestra un mensaje de error y sale de la función
            e.control.error_text = "Código de ticket inválido, por favor verifica."
            # En caso de error, mostrar un mensaje
            self.cobro_page.muestra_mensaje(title="Error al consultar el codigo",
                                            mensaje="Código de ticket inválido, por favor verifica.", tipo="error")
            return

        # Si el formato es correcto, continuar
        try:

            ticket_id = ticket_code.split('#')
            self.ticket = busca_ticket(int(ticket_id[0]))  # Obtener el ticket por ID

            dias, horas, minutos = self.calcular_tiempo_transcurrido(fecha_hora_str=self.ticket['hora_entrada'],
                                                                     monto_tarifa=self.ticket['tarifa_value'])

            # Mostrar información del ticket
            datos_ticket = ft.Text(
                size=20,
                weight=ft.FontWeight.BOLD,
                value=(
                    f"Ticket Numero {self.ticket['id']}\n"
                    f"Tarifa = {self.ticket['tarifa_name']}\n"
                    f"Hora entrada = {self.ticket['hora_entrada']}\n"
                    f"Hora Salida = {self.hora_salida.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Tarifa = {self.ticket['tarifa_value']}\n"
                    f"Total a pagar  = ${self.ticket_total}\n"
                    f"Tiempo transcurrido = {int(dias)} Día(s) {int(horas)} HORAS(s) y {int(minutos)} MINUTO(S)\n"
                )
            )

            # Limpiar el campo de entrada y actualizar la interfaz
            e.control.value = None
            self.ticket_info.controls = [datos_ticket]
            self.btn_cobrar.visible = True
            self.update()

        except Exception as ex:
            # En caso de error, mostrar un mensaje
            self.cobro_page.muestra_mensaje(title="Error al consultar el ticket", mensaje=ex, tipo="error")

    def calcular_tiempo_transcurrido(self, fecha_hora_str: str, monto_tarifa) -> tuple:
        # Definir el formato de la fecha y hora almacenada en la base de datos
        formato_fecha_hora = "%Y-%m-%d %H:%M:%S"

        # Convertir la cadena a un objeto datetime
        fecha_hora_ticket = datetime.strptime(fecha_hora_str, formato_fecha_hora)

        # Obtener la fecha y hora actual
        self.hora_salida = datetime.now()

        # Calcular la diferencia de tiempo
        diferencia = self.hora_salida - fecha_hora_ticket

        self.ticket_total = diferencia * monto_tarifa

        dias = diferencia.days
        horas, resto = divmod(diferencia.seconds, 3600)
        minutos, _ = divmod(resto, 60)

        # Calcular las horas totales redondeando hacia arriba (incluyendo días)
        horas_totales = dias * 24 + horas + (1 if minutos > 0 else 0)

        self.ticket_total = horas_totales * monto_tarifa

        return dias, horas, minutos

    def cobra_ticket_perdido(self, e, ticket):
        self.ticket = ticket
        self.ticket_total = ticket['total']
        self.hora_salida = datetime.now()
        self.muestra_modal_cobro(e)

    def muestra_modal_cobro(self, e):
        tipo = None

        def on_cobro_completado(cambio, exito):
            if exito:
                try:
                    # Aquí puedes realizar las comprobaciones necesarias
                    if cambio > 0:
                        self.cambio = cambio
                    nueva_salida(ticket_id=self.ticket['id'],
                                 hora_salida=self.hora_salida.strftime('%Y-%m-%d %H:%M:%S'), total=self.ticket_total,
                                 cambio=self.cambio)
                    self.device.abrir_pluma(1, "sistema")
                    self.muestra_cambio(e)

                except Exception as error:
                    self.cobro_page.muestra_mensaje(title="Error al cobrar el ticket",
                                                    mensaje=f"{error}", tipo="error")

            else:
                self.cobro_page.muestra_mensaje(title="Error al cobrar el ticket",
                                                mensaje="Error al cobrar o cancelado", tipo="error")

        # Pasar el callback al modal
        if e.control.key == "c4":
            tipo = "ticket perdido"
        elif e.control.key == "c10":
            tipo = "ticket"

        dlg_cobro = CobroDlg(total=self.ticket_total, on_complete=on_cobro_completado, referencia_tipo="ticket",
                             referencia_id=self.ticket['id'], tipo=tipo, usuario_id=self.usuario[2])
        self.page.open(dlg_cobro)

    def muestra_cambio(self, e):
        self.btn_cobrar.visible = False
        self.ticket_info.controls = [ft.Text(value=f"Cambio ${self.cambio}", size=40, weight=ft.FontWeight.BOLD)]
        self.cobro_page.actualiza_vista(e)
