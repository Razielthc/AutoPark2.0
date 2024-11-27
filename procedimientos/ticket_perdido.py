from datetime import datetime

from models.model_tarifas import ticket_perdido_tarifa
from models.model_ticket import crear_ticket


def nuevo_ticket_perdido(usuario):
    try:
        hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        tarifa = ticket_perdido_tarifa()
        ticket = crear_ticket(hora_entrada=hora, hora_salida=hora, total=tarifa['costo'], tarifa_name=tarifa['nombre'],
                              tarifa_value=tarifa['costo'], usuario_id=usuario, impreso=True)
        return ticket
    except Exception as e:
        raise e
