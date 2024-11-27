import flet as ft

from models.model_clientes import leer_clientes, soft_elimina_cliente
from models.model_ingresos import elimina_ingreso
from models.model_planes import crear_plan, elimina_plan
from models.model_tarifas import renovacion_tarjeta_tarifa
from models.model_tarjetas import crear_tarjeta, desactiva_tarjeta, elimina_tarjeta
from procedimientos.imprime_recibo_renovacion import imprime_recibo_renovacion
from vistas.frames.cliente_dlg_frame import ClienteDlg
from vistas.frames.cobro_dlg_frame import CobroDlg
from vistas.frames.renueva_dlg import RenuevaDlg


class ClientesPage(ft.Column):
    def __init__(self, usuario=None, device=None):
        super().__init__()

        self.device = device
        self.num_paginas = None
        self.usuario = usuario
        self.isolated = True
        self.alignment = ft.MainAxisAlignment.START
        self.expand = True
        self.spacing = 100
        self.scroll = ft.ScrollMode.AUTO

        # Busqueda Cliente
        self.filtro = ""
        self.search_input = ft.TextField(
            hint_text="Buscar por nombre, folio o correo...",
            expand=True,
            on_change=self.buscar_clientes,
        )
        self.btn_search = ft.FilledButton(
            text="Buscar",
            icon="SEARCH",
            style=ft.ButtonStyle(
                bgcolor=ft.colors.BLUE_ACCENT_400,
                color="white"
            ),
            on_click=self.buscar_clientes
        )

        # Paginación
        self.pagina_actual = 1
        self.registros_por_pagina = 20

        self.dlg = ft.AlertDialog(on_dismiss=self.actualiza_tabla_clientes)

        self.bar = ft.Row(controls=[
            ft.Text(value="Clientes", size=40),
            ft.ElevatedButton(content=ft.Container(content=ft.Text(value="Nuevo Plan", size=20, expand=True,
                                                                   color="white"),
                                                   padding=10),
                              bgcolor="#3795BD",
                              on_click=self.actualizar_cliente)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Folio documento")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Estado Plan")),
                ft.DataColumn(ft.Text("Tipo Plan")),
                ft.DataColumn(ft.Text("Inicio")),
                ft.DataColumn(ft.Text("Fin")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            expand=True
        )

        # Controles de paginación
        self.pagination_controls = ft.Row(
            controls=[
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=self.pagina_anterior, icon_size=20),
                ft.Text(f"Página {self.pagina_actual}", key="pagina_label", size=20),
                ft.IconButton(icon=ft.icons.ARROW_FORWARD, on_click=self.pagina_siguiente, icon_size=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.controls = [
            self.bar,
            ft.Row(controls=[
                self.search_input, self.btn_search
            ]),
            self.table,
            self.pagination_controls
        ]

    def did_mount(self):
        self.actualiza_tabla_clientes()
        self.actualiza_controles_paginacion()

    def actualiza_tabla_clientes(self, e=None):
        # Leer clientes y calcular total de páginas
        clientes, total_registros = leer_clientes(
            pagina=self.pagina_actual,
            registros_por_pagina=self.registros_por_pagina,
            filtro=self.filtro  # Aplica el filtro si existe
        )
        self.calcular_num_paginas(total_registros)

        # Crear botones como métodos para reutilizarlos
        def crear_boton_editar(data_cliente):
            return ft.IconButton(
                icon=ft.icons.EDIT,
                icon_color="YELLOW",
                on_click=lambda _: self.actualizar_cliente(cliente=data_cliente),
                tooltip="Editar Cliente"
            )

        def crear_boton_eliminar(cliente_id):
            return ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color="red",
                on_click=lambda _: self.delete_cliente(cliente_id),
                tooltip="Eliminar Cliente"
            )

        def crear_boton_renovar_plan(cliente_id):
            return ft.IconButton(
                icon=ft.icons.AUTORENEW,
                icon_color=ft.colors.BLUE_ACCENT_400,
                on_click=lambda _: self.renueva_plan(cliente_id),
                tooltip="Renovar Plan"
            )

        def crear_boton_renovar_tarjeta(cliente_id, tarjeta_id, tarjeta_hex):
            return ft.IconButton(
                icon=ft.icons.CREDIT_CARD_ROUNDED,
                icon_color=ft.colors.ORANGE_200,
                on_click=lambda _: self.renovar_tarjeta(cliente_id, tarjeta_id, tarjeta_hex),
                tooltip="Renovar Tarjeta"
            )

        # Crear filas para la tabla
        def crear_fila(cliente_data, acciones_data, plan_esta_activo):
            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(value=cliente_data.get('nombre_cliente'))),
                    ft.DataCell(ft.Text(value=cliente_data.get('folio_documento'))),
                    ft.DataCell(ft.Text(value=cliente_data.get('email'))),
                    ft.DataCell(ft.Text(value=cliente_data.get('telefono'))),
                    ft.DataCell(
                        ft.Icon(
                            name=ft.icons.CHECK_CIRCLE if plan_esta_activo else ft.icons.CANCEL,
                            color=ft.colors.GREEN_ACCENT_400 if plan_esta_activo else ft.colors.RED_ACCENT_400,
                            size=20
                        )
                    ),
                    ft.DataCell(ft.Text(value=cliente_data.get('tarifa_duracion', ""))),
                    ft.DataCell(ft.Text(value=cliente_data.get('fecha_inicio', ""))),
                    ft.DataCell(ft.Text(value=cliente_data.get('fecha_fin', ""))),
                    ft.DataCell(ft.Row(acciones_data))
                ]
            )

        filas = []

        for cliente in clientes:
            # Crear acciones comunes
            acciones = [
                crear_boton_editar(cliente),
                crear_boton_eliminar(cliente.get('cliente_id'))
            ]

            # Determinar si el cliente tiene un plan activo
            plan_activo = cliente.get('tarifa_duracion') is not None

            # Agregar botones según la condición del plan
            acciones.append(crear_boton_renovar_tarjeta(cliente.get('cliente_id'), cliente.get('tarjeta_id'),
                                                        cliente.get('tarjeta_hex')))
            if not plan_activo:
                acciones.append(crear_boton_renovar_plan(cliente.get('cliente_id')))

            # Crear fila y agregarla a la lista
            filas.append(crear_fila(cliente, acciones, plan_activo))

        # Actualizar las filas en la tabla y refrescar la vista
        self.table.rows = filas
        self.update()

    def actualizar_cliente(self, e=None, cliente=None):

        def on_add_update_completado(exito, error=None):
            if exito is True:
                if cliente is not None:
                    self.muestra_mensaje(title="Actualizacion Cliente", mensaje="Cliente actualizado exitosamente.",
                                         tipo="exito")
                else:
                    self.muestra_mensaje(title="Alta Cliente", mensaje="Cliente guardado exitosamente.", tipo="exito")

            else:
                self.muestra_mensaje(title="Error al guardar", mensaje=f"Error {error}",
                                     tipo="error")

        if cliente is not None:
            dlg_cliente = ClienteDlg(cliente=cliente, on_complete=on_add_update_completado,
                                     usuario_id=self.usuario[2])
            self.page.open(dlg_cliente)
        else:
            self.page.go("/planes")

    def delete_cliente(self, id_cliente):
        soft_elimina_cliente(cliente_id=id_cliente)
        self.actualiza_tabla_clientes()

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

    def pagina_anterior(self, e):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualiza_tabla_clientes()
            self.actualiza_controles_paginacion()

    def pagina_siguiente(self, e):
        if self.pagina_actual < self.num_paginas:
            self.pagina_actual += 1
            self.actualiza_tabla_clientes()
            self.actualiza_controles_paginacion()

    def actualiza_controles_paginacion(self):
        # Deshabilitar "Página Anterior" si estás en la primera página
        self.pagination_controls.controls[0].disabled = (self.pagina_actual == 1)

        # Deshabilitar "Página Siguiente" si estás en la última página
        self.pagination_controls.controls[2].disabled = (self.pagina_actual >= self.num_paginas)

        # Actualizar el texto del paginador
        self.pagination_controls.controls[1].value = f"Página {self.pagina_actual} de {self.num_paginas}"

        self.update()

    def calcular_num_paginas(self, total_registros):
        self.num_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)

    def buscar_clientes(self, e):
        self.filtro = self.search_input.value.strip()  # Obtén el texto del buscador
        self.pagina_actual = 1  # Reinicia a la primera página
        self.actualiza_tabla_clientes()  # Vuelve a cargar los datos con el filtro
        self.actualiza_controles_paginacion()  # Actualiza la paginación

    def renueva_plan(self, cliente_id):
        def on_complete_plan(plan, resultado):
            if not resultado:
                return

            try:
                # Crear el nuevo plan
                nuevo_plan = crear_plan(
                    cliente_id=cliente_id,
                    tarifa_costo=plan['tarifa_costo'],
                    tarifa_duracion=plan['tarifa_duracion'],
                    fecha_inicio=plan['fecha_inicio'],
                    fecha_fin=plan['fecha_fin'],
                    usuario_id=self.usuario[2]
                )

                # Definir el callback para ejecutar tras el cobro exitoso
                def on_cobro_exitoso(cambio):
                    if self.device.user_modify(user_id=str(cliente_id), valid_begin_time=plan['valid_begin_time'],
                                               valid_end_time=plan['valid_end_time']):
                        imprime_recibo_renovacion(cliente_id=cliente_id, datos_plan=plan, cambio=cambio)
                        self.muestra_mensaje(
                            title="Plan Renovado",
                            mensaje="Plan renovado correctamente",
                            tipo="exito"
                        )

                # Abrir el modal de cobro
                self.abre_modal_cobro(
                    total=plan['tarifa_costo'],
                    referencia_tipo="plan",
                    referencia_id=nuevo_plan,
                    tipo="renovacion plan",
                    on_success=on_cobro_exitoso  # Pasar el callback
                )

            except Exception as e:
                # Manejo de errores
                if 'nuevo_plan' in locals() and nuevo_plan:
                    elimina_plan(nuevo_plan)
                self.muestra_mensaje(
                    title="Error Plan",
                    mensaje=f"Error al renovar el plan {e}",
                    tipo="error"
                )

        # Crear y abrir el diálogo de renovación
        dlg_renueva_plan = RenuevaDlg(tipo="plan", on_complete=on_complete_plan)
        self.page.open(dlg_renueva_plan)

    def abre_modal_cobro(self, total, referencia_tipo, referencia_id, tipo, on_success=None):
        def on_cobro_completado(cambio, exito, mensaje=None):
            if not exito:
                self.maneja_error_cobro(referencia_id, referencia_tipo,
                                        f"Cobro fallido o cancelado por el usuario. {mensaje}")
                return

            try:

                # Ejecutar callback si se proporciona
                if on_success:
                    on_success(cambio)
            except Exception as e:
                elimina_ingreso(total, referencia_tipo, referencia_id)
                self.maneja_error_cobro(referencia_id, referencia_tipo, f"Error al procesar el cobro: {e}")

        # Crear y abrir el diálogo de cobro
        dlg_cobro = CobroDlg(
            total=total,
            on_complete=on_cobro_completado,
            referencia_tipo=referencia_tipo,
            referencia_id=referencia_id,
            tipo=tipo,
            usuario_id=self.usuario[2]
        )
        self.page.open(dlg_cobro)

    def maneja_error_cobro(self, referencia_id, referencia_tipo, mensaje_error):
        """
        Maneja errores en el proceso de cobro y elimina el plan, si corresponde.
        """
        if referencia_tipo == "plan":
            elimina_plan(referencia_id)
        elif referencia_tipo == "renovacion":
            elimina_tarjeta(tarjeta_id=referencia_id)

        self.muestra_mensaje(
            title="Error al procesar el cobro",
            mensaje=mensaje_error,
            tipo="error"
        )

    def renovar_tarjeta(self, cliente_id, tarjeta_id, tarjeta_hex):

        def on_complete_tarjeta(tarjeta, resultado):
            if not resultado:
                return

            try:

                nueva_tarjeta = crear_tarjeta(cliente_id=cliente_id,
                                              numero_tarjeta=tarjeta['numero_tarjeta'],
                                              tarjeta_hex=tarjeta['numero_hex'],
                                              usuario_id=self.usuario[2])

                # Definir el callback para ejecutar tras el cobro exitoso
                def on_cobro_exitoso(cambio):
                    if desactiva_tarjeta(tarjeta_id=tarjeta_id):

                        card_insert = self.device.card_insert(cliente_id=str(cliente_id),
                                                              tarjeta_hex=tarjeta['numero_hex'])

                        if not card_insert:
                            raise Exception("Error al ingresar la tarjeta.")

                        remove_card = self.device.card_remove(tarjeta_hex=tarjeta_hex)

                        if not remove_card:
                            raise Exception("Error al eliminar la tarjeta.")

                        imprime_recibo_renovacion(cliente_id=cliente_id, datos_tarjeta=tarjeta, cambio=cambio)
                        self.muestra_mensaje(
                            title="Tarjeta Renovada",
                            mensaje="Tarjeta renovada correctamente",
                            tipo="exito"
                        )

                costo_renovacion = renovacion_tarjeta_tarifa()
                # Abrir el modal de cobro
                self.abre_modal_cobro(
                    total=costo_renovacion['costo'],
                    referencia_tipo=costo_renovacion['tipo'],
                    referencia_id=nueva_tarjeta,
                    tipo=costo_renovacion['nombre'],
                    on_success=on_cobro_exitoso  # Pasar el callback
                )

            except Exception as e:
                # Manejo de errores
                if 'nueva tarjeta' in locals() and nueva_tarjeta:
                    elimina_tarjeta(tarjeta_id=tarjeta_id)
                self.muestra_mensaje(
                    title="Error Tarjeta",
                    mensaje=f"Error al renovar tarjeta {e}",
                    tipo="error"
                )

            # Crear y abrir el diálogo de renovación

        dlg_renueva_plan = RenuevaDlg(tipo="tarjeta", on_complete=on_complete_tarjeta)
        self.page.open(dlg_renueva_plan)


if __name__ == "__main__":
    pass
