from datetime import datetime

from models.model_session import session_activa
from models.model_tarifas import tarifa_default
from models.model_ticket import crear_ticket
from procedimientos.Imprime_ticket import imprime_ticket


def nueva_entrada_auto():
    tarifa = tarifa_default()
    user = session_activa()
    hora = datetime.now()
    try:
        ticket = crear_ticket(hora_entrada=hora.strftime("%Y-%m-%d %H:%M:%S"), tarifa_name=tarifa['nombre'],
                              tarifa_value=tarifa['costo'], usuario_id=user['usuario_id'])
        imprime_ticket(ticket)

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
