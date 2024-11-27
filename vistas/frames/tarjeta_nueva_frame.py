import flet as ft
import re


class TarjetaForm(ft.Column):
    def __init__(self):
        super().__init__()
        self.isolated = True
        self.width = 600
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.datos_tarjeta = {}

        self.numero_tarjeta_input = ft.TextField(label="Ingresa el numero de tarjeta", input_filter=ft.NumbersOnlyInputFilter())
        self.controls = [
            ft.Text("Ingresa numero de tarjeta", size=24, weight=ft.FontWeight.BOLD),
            self.numero_tarjeta_input
        ]

    def valida_tarjeta(self):

        if not self.validar_datos(self.numero_tarjeta_input.value or "", "tarjeta"):
            self.numero_tarjeta_input.error_text = "Tarjeta no valida"
            self.update()
            return False, None

        numero_hex = self.convertir_a_hexadecimal(self.numero_tarjeta_input.value)
        self.datos_tarjeta['numero_tarjeta'] = self.numero_tarjeta_input.value
        self.datos_tarjeta['numero_hex'] = numero_hex
        return True, self.datos_tarjeta

    @staticmethod
    def validar_datos(valor, tipo):
        patrones = {
            "tarjeta": r"^\d{7,10}$",  # Solo números, entre 7 y 10 dígitos
        }

        patron = patrones.get(tipo)
        if patron and re.match(patron, valor):
            return True
        else:
            return False

    @staticmethod
    def convertir_a_hexadecimal(valor: str) -> str:
        """
        Convierte un número en formato string a su representación hexadecimal con ceros iniciales.

        Args:
            valor (str): Número en formato string.

        Returns:
            str: Representación hexadecimal de 8 caracteres.
        """
        try:
            # Convertir el valor de cadena a entero
            numero = int(valor)

            # Convertir el número a hexadecimal y asegurar que tenga 8 caracteres
            hexadecimal = f"{numero:08X}"  # Mayúsculas y rellenado con ceros

            return hexadecimal
        except ValueError:
            # Manejar el caso en el que no sea un número válido
            return "Valor no válido"


if __name__ == "__main__":
    pass
