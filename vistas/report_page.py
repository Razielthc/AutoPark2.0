import flet as ft


class ReportPage(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.texto = ft.Text(value="Esta es la ventana de reportes", color="red")
        self.controls = [self.texto]

    def did_mount(self):
        print("Se cargo vista Reportes")


if __name__ == "__main__":
    pass
