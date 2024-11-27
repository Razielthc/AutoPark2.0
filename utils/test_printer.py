from escpos.exceptions import DeviceNotFoundError, USBNotFoundError
from escpos.printer import Network, Win32Raw


async def verificar_impresora(printer_type, name=None, port=None):
    try:
        if printer_type == "printer_system":
            p = Win32Raw(name)
        elif printer_type == "printer_entrada":
            p = Network(port)
        else:
            return "Tipo de impresora desconocido"

        p.set(align='center')
        p.text("Prueba de impresión\n")
        p.cut()
        p.close()
        return True
    except (DeviceNotFoundError, USBNotFoundError) as e:
        return str(e)
    except Exception as e:
        return f"Error al conectar la impresora: {e}"


if __name__ == "__main__":
    pass
