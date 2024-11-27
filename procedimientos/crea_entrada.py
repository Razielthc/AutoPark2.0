from datetime import datetime

from models.model_ticket import crear_ticket
from procedimientos.Imprime_ticket import imprime_ticket


def nueva_entrada(tarifa_name, tarifa_valor, user_id):
    hora = datetime.now()
    try:
        ticket = crear_ticket(hora_entrada=hora.strftime("%Y-%m-%d %H:%M:%S"), tarifa_name=tarifa_name,
                              tarifa_value=tarifa_valor, usuario_id=user_id)
        imprime_ticket(ticket)
    except Exception as e:
        raise


if __name__ == "__main__":
    pass
