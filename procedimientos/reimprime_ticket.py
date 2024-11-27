from models.model_ticket import tickets_no_impresos, busca_ticket
from procedimientos.Imprime_ticket import imprime_ticket


def reimprime_uno(ticket_id: int):
    try:
        ticket = busca_ticket(ticket_id)
        imprime_ticket(ticket, True)
    except Exception as e:
        raise e


def reimprime_no_impresos():
    try:
        tickets = tickets_no_impresos()

        # Validar si la lista está vacía
        if not tickets:
            raise ValueError("No hay tickets pendientes de reimpresión.")

        # Sí hay tickets, continuar con el proceso de reimpresión
        for ticket in tickets:
            imprime_ticket(ticket, True)  # Función que manejaría la reimpresión de cada ticket

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
