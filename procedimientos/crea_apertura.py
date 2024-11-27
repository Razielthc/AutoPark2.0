from models.model_aperturas import crear_apertura
from models.model_session import session_activa


def nueva_apertura(apertura: dict):
    try:
        user = session_activa()
        door_name = None
        if apertura['door_channel'] == "0":
            door_name = "Entrada"
        elif apertura['door_channel'] == "1":
            door_name = "Salida"

        crear_apertura(door_name=door_name,
                       metodo_entrada=apertura['metodo_entrada'],
                       card_number=apertura['card_number'],
                       card_status=apertura['card_status'],
                       error_code=apertura['error_code'],
                       fecha=apertura['time_str'],
                       usuario_id=user['usuario_id'])

    except Exception as e:
        raise e
