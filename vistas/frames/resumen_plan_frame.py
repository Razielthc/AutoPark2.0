import flet as ft


class ResumenPlan(ft.Column):
    def __init__(self, datos_cliente, datos_plan, numero_tarjeta):
        super().__init__()
        self.datos_cliente = datos_cliente
        self.datos_plan = datos_plan
        self.numero_tarjeta = numero_tarjeta

        # Crear y añadir controles para mostrar la información
        self.controls = [
            ft.Text("Resumen del Plan", weight=ft.FontWeight.W_800),
            ft.Divider(),
            # Información del cliente
            ft.Text("Datos del Cliente:", weight=ft.FontWeight.BOLD),
            ft.Text(f"Nombre: {datos_cliente['nombre']}"),
            ft.Row(controls=[
                ft.Text(f"Documento: {datos_cliente['documento']}"),
                ft.Text(f"Folio del Documento: {datos_cliente['folio_documento']}"),
            ]),
            ft.Row(controls=[
                ft.Text(f"Email: {datos_cliente['email']}"),
                ft.Text(f"Teléfono: {datos_cliente['telefono']}"),

            ]),
            ft.Text(f"Dirección: {datos_cliente['direccion']}"),
            ft.Row(controls=[
                ft.Text(f"Modelo del Vehículo: {datos_cliente['modelo']}"),
                ft.Text(f"Placa del Vehículo: {datos_cliente['placa']}"),

            ]),

            ft.Divider(),

            # Información del plan
            ft.Text("Plan Seleccionado:", weight=ft.FontWeight.BOLD),
            ft.Text(f"Tarifa Costo: ${datos_plan['tarifa_costo']:.2f}"),
            ft.Text(f"Duración: {datos_plan['tarifa_duracion']}"),
            ft.Text(f"Fecha de Inicio: {datos_plan['fecha_inicio']}"),
            ft.Text(f"Fecha de Fin: {datos_plan['fecha_fin']}"),
            ft.Divider(),

            # Información de la tarjeta
            ft.Text("Información de la Tarjeta:", weight=ft.FontWeight.BOLD),
            ft.Text(f"Número de Tarjeta: {numero_tarjeta['numero_tarjeta']}")
        ]


if __name__ == "__main__":
    pass
