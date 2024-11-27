import sys
import os


def resource_path(relative_path):
    """ Obtiene la ruta absoluta del archivo, sea en modo empaquetado o no """
    try:
        # Si estamos empaquetados, usa el path de la aplicación
        base_path = sys._MEIPASS
    except AttributeError:
        # Si estamos en desarrollo, usa el directorio actual del script
        utils_path = os.path.dirname(os.path.abspath(__file__))

        base_path = os.path.dirname(utils_path)

    return os.path.join(base_path, relative_path)
