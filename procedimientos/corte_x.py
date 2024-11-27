from datetime import datetime

from models.model_corte import crear_corte, generar_corte


def nuevo_corte_x(user_id):
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

        # guarda el corte en la bd tabla cortes
        corte = crear_corte(tipo="CorteX", monto=total_neto, fecha=fecha, c_salida=c_salida,
                            usuario_id=user_id)
        # envia corte a flet(corte)
        return corte

    except Exception as e:
        raise e


if __name__ == "__main__":
    pass
