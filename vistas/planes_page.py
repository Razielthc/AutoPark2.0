import flet as ft

from models.model_clientes import crear_cliente, elimina_cliente
from models.model_ingresos import elimina_ingreso
from models.model_planes import crear_plan
from models.model_tarjetas import crear_tarjeta
from vistas.frames.cliente_nuevo_frame import ClienteForm
from vistas.frames.cobro_dlg_frame import CobroDlg
from vistas.frames.plan_nuevo_frame import PlanForm
from vistas.frames.resumen_plan_frame import ResumenPlan
from vistas.frames.tarjeta_nueva_frame import TarjetaForm
from procedimientos.imprime_recibo_nuevo_plan import imprime_recibo


class PlanesPage(ft.Column):
    def __init__(self, usuario_id, device):
        super().__init__()
        self.dlg = ft.AlertDialog(on_dismiss=self.regresar_ruta)
        self.isolated = True
        self.expand = True
        self.spacing = 20
        self.usuario_id = usuario_id
        self.device = device
        self.cliente_form = ClienteForm()
        self.plan_form = PlanForm()
        self.tarjeta_form = TarjetaForm()

        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.alignment = ft.MainAxisAlignment.SPACE_AROUND
        # Variables para almacenar los datos
        self.datos_cliente = None
        self.plan_seleccionado = None
        self.tarjeta_info = None

        # Control de pasos
        self.current_step = 0
        self.step_count = 3

        # Estructura del formulario por pasos
        self.steps = [
            self.cliente_form,
            self.plan_form,
            self.tarjeta_form

        ]

        # Barra de progreso

        self.barra_progreso = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text("1", size=20, weight=ft.FontWeight.BOLD),
                    border=ft.border.all(3, ft.colors.BLUE_ACCENT_400),
                    border_radius=ft.border_radius.all(100),  # Aumenta el valor para hacerlo más circular
                    width=50,  # Define un ancho fijo
                    height=50,  # Define una altura fija
                    alignment=ft.alignment.center,  # Centra el contenido dentro del contenedor
                    key="0"
                ),
                ft.Container(
                    width=100,  # Longitud de la línea
                    height=2,  # Grosor de la línea
                    bgcolor=ft.colors.BLACK,
                    alignment=ft.alignment.center,
                ),

                ft.Container(
                    content=ft.Text("2", size=20, weight=ft.FontWeight.BOLD),
                    border=ft.border.all(2, ft.colors.BLUE_GREY_800),
                    border_radius=ft.border_radius.all(100),  # Aumenta el valor para hacerlo más circular
                    width=50,  # Define un ancho fijo
                    height=50,  # Define una altura fija
                    alignment=ft.alignment.center,  # Centra el contenido dentro del contenedor
                    key="1"
                ),
                ft.Container(
                    width=100,  # Longitud de la línea
                    height=2,  # Grosor de la línea
                    bgcolor=ft.colors.BLACK,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=ft.Text("3", size=20, weight=ft.FontWeight.BOLD),
                    border=ft.border.all(2, ft.colors.BLUE_GREY_800),
                    border_radius=ft.border_radius.all(100),  # Aumenta el valor para hacerlo más circular
                    width=50,  # Define un ancho fijo
                    height=50,  # Define una altura fija
                    alignment=ft.alignment.center,  # Centra el contenido dentro del contenedor
                    key="2"
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Botones de navegación
        self.botones_navegacion = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "Anterior",
                    on_click=self.retroceder,
                    icon=ft.icons.ARROW_BACK,
                    disabled=True,
                ),
                ft.FilledButton(
                    content=ft.Text("Confirmar", size=25),
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_400),
                    visible=False,
                    on_click=self.muestra_modal_cobro
                ),
                ft.ElevatedButton(
                    "Siguiente",
                    on_click=self.avanzar,
                    icon=ft.icons.ARROW_FORWARD,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
        )

        # Contenido inicial
        self.controls = [
            self.barra_progreso,
            self.steps[self.current_step],
            self.botones_navegacion,
        ]

    def avanzar(self, e):
        """Avanza al siguiente paso si es válido."""
        if self.validar_paso_actual():
            self.current_step += 1
            if self.current_step >= self.step_count:
                self.finalizar_formulario()
                return
            self.actualizar_paso()

    def retroceder(self, e):
        """Regresa al paso anterior."""
        if self.current_step > 0:
            self.current_step -= 1
            self.actualizar_paso()

    def actualizar_paso(self):
        """Actualiza la interfaz para mostrar el paso actual."""
        self.controls = [self.barra_progreso, self.steps[self.current_step], self.botones_navegacion]
        self.botones_navegacion.controls[0].disabled = (self.current_step == 0)
        self.botones_navegacion.controls[1].visible = (self.current_step == 3)
        self.botones_navegacion.controls[2].disabled = (self.current_step == 3)

        for control in self.barra_progreso.controls:
            if control.key == str(self.current_step):
                control.border = ft.border.all(3, ft.colors.BLUE_ACCENT_400)
            else:
                control.border = ft.border.all(3, ft.colors.BLUE_GREY_800)
        self.update()

    def validar_paso_actual(self):
        """Valida el paso actual del formulario."""

        if self.current_step == 0:
            resultado, datos_clientes = self.cliente_form.valida_cliente()
            if not resultado:
                return False
            self.datos_cliente = datos_clientes

        elif self.current_step == 1:
            # Validar selección del plan
            resultado, plan_seleccionado = self.plan_form.valida_plan()
            if not resultado:
                return False
            self.plan_seleccionado = plan_seleccionado
        elif self.current_step == 2:
            # validar tarjeta
            resultado, tarjeta_info = self.tarjeta_form.valida_tarjeta()
            if not resultado:
                return False
            self.tarjeta_info = tarjeta_info

        return True

    def finalizar_formulario(self):
        self.controls = [ResumenPlan(datos_cliente=self.datos_cliente, datos_plan=self.plan_seleccionado,
                                     numero_tarjeta=self.tarjeta_info), self.botones_navegacion]
        self.botones_navegacion.controls[1].visible = (self.current_step == 3)
        self.botones_navegacion.controls[2].disabled = (self.current_step == 3)
        self.update()

    def muestra_modal_cobro(self, e):
        cliente_nuevo = None
        nuevo_plan = None

        try:
            # Crear cliente
            cliente_nuevo = crear_cliente(
                nombre=self.datos_cliente['nombre'],
                documento=self.datos_cliente['documento'],
                folio_documento=self.datos_cliente['folio_documento'],
                email=self.datos_cliente['email'],
                telefono=self.datos_cliente['telefono'],
                direccion=self.datos_cliente['direccion'],
                placa=self.datos_cliente['placa'],
                modelo=self.datos_cliente['modelo'],
                usuario_id=self.usuario_id
            )

            # Crear plan
            if cliente_nuevo:
                nuevo_plan = crear_plan(
                    cliente_id=cliente_nuevo,
                    tarifa_costo=self.plan_seleccionado['tarifa_costo'],
                    tarifa_duracion=self.plan_seleccionado['tarifa_duracion'],
                    fecha_inicio=self.plan_seleccionado['fecha_inicio'],
                    fecha_fin=self.plan_seleccionado['fecha_fin'],
                    usuario_id=self.usuario_id
                )

                nueva_tarjeta = crear_tarjeta(cliente_id=cliente_nuevo,
                                              numero_tarjeta=self.tarjeta_info['numero_tarjeta'],
                                              tarjeta_hex=self.tarjeta_info['numero_hex'],
                                              usuario_id=self.usuario_id)

            def on_cobro_completado(cambio, exito):
                try:
                    if not exito:
                        raise Exception("Cobro fallido o cancelado por el usuario.")

                    # Validar cambio (si aplica)
                    if cambio > 0:
                        self.cambio = cambio
                        imprime_recibo(datos_cliente=self.datos_cliente, datos_plan=self.plan_seleccionado, datos_tarjeta=self.tarjeta_info,
                                       cambio=100)

                    # Agregar usuario al dispositivo y registrar tarjeta
                    user_device = self.device.addClient(
                        clientId=str(cliente_nuevo),
                        valid_begin_time=self.plan_seleccionado['valid_begin_time'],
                        valid_end_time=self.plan_seleccionado['valid_end_time']
                    )

                    if not user_device:
                        raise Exception("Error al registrar el usuario en el dispositivo.")

                    # Insertar tarjeta
                    self.device.card_insert(
                        tarjeta_hex=self.tarjeta_info['numero_hex'],
                        cliente_id=str(cliente_nuevo)
                    )

                    self.muestra_mensaje(
                        title="Plan Creado",
                        mensaje="Plan creado correctamente",
                        tipo="exito"
                    )
                except Exception as error_cobro:
                    if cliente_nuevo:
                        elimina_cliente(cliente_nuevo)
                        elimina_ingreso(self.plan_seleccionado['tarifa_costo'], "plan", nuevo_plan)
                    self.muestra_mensaje(
                        title="Error al procesar el cobro",
                        mensaje=f"Error: {error_cobro}",
                        tipo="error"
                    )

            # Crear diálogo de cobro
            dlg_cobro = CobroDlg(
                total=self.plan_seleccionado['tarifa_costo'],
                on_complete=on_cobro_completado,
                referencia_tipo="plan",
                referencia_id=nuevo_plan,
                tipo="nuevo plan",
                usuario_id=self.usuario_id
            )
            self.page.open(dlg_cobro)

        except Exception as error:
            # Eliminar cliente si algo falla
            if cliente_nuevo:
                elimina_cliente(cliente_nuevo)

            self.muestra_mensaje(
                title="Error al crear el plan",
                mensaje=f"Error: {error}",
                tipo="error"
            )

    def limpia_inputs(self, e):
        e.control.error_text = None
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

    def regresar_ruta(self, e):
        self.page.go("/clientes")


if __name__ == "__main__":
    pass
