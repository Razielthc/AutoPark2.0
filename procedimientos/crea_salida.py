from models.model_ticket import actualiza_ticket
from procedimientos.imprime_recibo import imprime_recibo


def nueva_salida(ticket_id: int, hora_salida: str, total, cambio):
    try:
        ticket_actualizado = actualiza_ticket(ticket_id, hora_salida, total)
        if isinstance(ticket_actualizado, dict):
            imprime_recibo(ticket_actualizado, cambio)
        else:
            raise ValueError(f"Error al actualizar ticket: {ticket_actualizado}")
    except Exception as e:
        raise e  # Propaga el error hacia el nivel superior
