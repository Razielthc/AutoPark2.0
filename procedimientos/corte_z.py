from datetime import datetime

from decouple import config

from models.model_aperturas import autos_dentro, aperturas_del_turno, marcar_aperturas_corte
from models.model_corte import crear_corte, generar_corte
from models.model_ticket import marcar_ticket_corte
from procedimientos.enviar_correo import enviar_correo
from procedimientos.imprime_corte import imprime_corte


def nuevo_corte_z(user_id):
    try:
        # Consulta los tickets que no tengan corte
        totales, ingresos, egresos = generar_corte()
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_neto = totales['total_ingresos'] - totales['total_egresos']

        c_salida = (f"Total de Ingresos: ${totales['total_ingresos']} \n"
                    f"Total de Egresos : ${totales['total_egresos']} \n"
                    f"--------------------------------------------- \n"
                    f"Total en caja: ${total_neto} \n"
                    f"Total de tickets emitidos: {totales['total_tickets']} \n"
                    f"Total de tickets cobrados: {totales['tickets_cobrados']} \n"
                    f"Total de tickets sin cobrar: {totales['tickets_sin_cobrar']} \n")

        if ingresos:
            c_salida += f"\n Resumen de Ingresos por Tipo: \n"
            for ingreso in ingresos:
                c_salida += f"Ingreso: {ingreso['tipo']}, Total: {ingreso['total_por_tipo']}\n"

        if egresos:
            c_salida += f"\n Resumen de Egresos por Tipo: \n"

            for egreso in egresos:
                c_salida += f"Egreso: {egreso['tipo']} Descripción {egreso['descripcion']} Total: {egreso['total_por_tipo']}\n"

        autos = autos_dentro()
        c_salida += f"\n Autos dentro: {autos} \n"
        aperturas = aperturas_del_turno()
        total_aperturas = 0
        c_salida += f"\n Aperturas durante el turno \n"
        for apertura in aperturas:
            total_aperturas += int(apertura['total'])
            c_salida += f"{apertura['door_name']} {apertura['metodo_entrada']} {apertura['total']}\n"

        c_salida += f"Total de aperturas: {total_aperturas}"

        # guarda el corte en la bd tabla cortes
        corte = crear_corte(tipo="CorteZ", monto=total_neto, fecha=fecha, c_salida=c_salida,
                            usuario_id=user_id)
        # envia corte a flet(corte)
        imprime_corte(corte)
        if config('SMTP_ENABLED', cast=bool) is True:
            enviar_correo(mensaje=c_salida, asunto=f"Reporte de Cierre de Caja {fecha}")

        marcar_ticket_corte()
        marcar_aperturas_corte()
        return corte

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
