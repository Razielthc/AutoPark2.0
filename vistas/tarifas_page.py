import flet as ft

from models.model_tarifas import leer_tarifas, eliminar_tarifa
from vistas.frames.tarifa_dlg import TarifaDlg


class TarifasPage(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.alignment = ft.MainAxisAlignment.CENTER
        self.expand = True
        self.dlg = ft.AlertDialog(on_dismiss=self.actualiza_tabla_tarifas)

        self.bar = ft.Row(controls=[
            ft.Text(value="Tarifas", size=40),
            ft.ElevatedButton(content=ft.Container(content=ft.Text(value="Nuevo Tarifa", size=20, expand=True,
                                                                   color="white"),
                                                   padding=10),
                              bgcolor="#3795BD",
                              on_click=self.agregar_tarifa)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=25)),
                ft.DataColumn(ft.Text("costo", size=25)),
                ft.DataColumn(ft.Text("Tipo", size=25)),
                ft.DataColumn(ft.Text("Acciones", size=25))
            ],
            expand=True
        )
        self.controls = [
            self.bar,
            self.table
        ]

    def did_mount(self):
        self.actualiza_tabla_tarifas()

    def actualiza_tabla_tarifas(self, e=None):
        tarifas = leer_tarifas()
        filas = []

        def crear_boton_editar(tarifa_data):
            return ft.IconButton(
                icon=ft.icons.EDIT,
                icon_color="YELLOW",
                on_click=lambda _: self.actualizar_tarifa(tarifa=tarifa_data),
                tooltip="Editar Tarifa"
            )

        def crear_boton_eliminar(tarifa_id):
            return ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color="red",
                on_click=lambda _: self.delete_tarifa(tarifa_id),
                tooltip="Eliminar Tarifa"
            )

        if isinstance(tarifas, list):
            for tarifa in tarifas:
                # Crear una nueva lista de acciones para cada tarifa
                acciones = [crear_boton_editar(tarifa)]

                # Condición para agregar el botón de eliminar
                if tarifa['tipo'] in ['hora', 'servicio'] and tarifa['nombre'] != 'auto':
                    acciones.append(crear_boton_eliminar(tarifa['id']))

                filas.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(value=tarifa['nombre'])),
                        ft.DataCell(ft.Text(value=str(tarifa['costo']))),
                        ft.DataCell(ft.Text(value=tarifa['tipo'])),
                        ft.DataCell(ft.Row(acciones))
                    ]
                ))
            # Actualizar las filas en la tabla y refrescar la vista
            self.table.rows = filas
            self.update()

    def agregar_tarifa(self, e):
        def on_complete(exito, mensaje=None):
            if exito:
                self.muestra_mensaje(title="Tarifa Creada", mensaje="Tarifa creada correctamente", tipo="exito")
            else:
                self.muestra_mensaje(title="Error Tarifa", mensaje=f"Error al crear la tarifa {mensaje}", tipo="error")

        tarifa_form = TarifaDlg(on_complete=on_complete)
        self.page.open(tarifa_form)

    def actualizar_tarifa(self, tarifa):
        def on_complete(exito, mensaje=None):
            if exito:
                self.muestra_mensaje(title="Tarifa Editada", mensaje="Tarifa editada correctamente", tipo="exito")
            else:
                self.muestra_mensaje(title="Error Tarifa", mensaje=f"Error al editar la tarifa {mensaje}", tipo="error")

        tarifa_form = TarifaDlg(tarifa=tarifa, on_complete=on_complete)
        self.page.open(tarifa_form)

    def delete_tarifa(self, id_tarifa):
        try:
            eliminar_tarifa(tarifa_id=id_tarifa)
            self.muestra_mensaje(title="Tarifa Eliminada", mensaje="Tarifa Eliminada correctamente", tipo="exito")
            self.actualiza_tabla_tarifas()
        except Exception as e:
            self.muestra_mensaje(title="Error Tarifa", mensaje=f"Error al eliminar la tarifa {e}", tipo="error")

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


if __name__ == "__main__":
    pass
