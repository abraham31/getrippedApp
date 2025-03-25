from app.core.database import db
from bson import ObjectId
from datetime import datetime

async def registrar_progreso(paciente_id: str, nutriologo_id: str, data: dict):
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": nutriologo_id,
        "role": "paciente",
        "is_deleted": False
    })

    if not paciente:
        return {"error": "Paciente no encontrado"}

    # Buscar último progreso registrado
    ultimo_progreso = await db.progresos.find_one(
        {"paciente_id": ObjectId(paciente_id)},
        sort=[("fecha", -1)]
    )

    es_primera_consulta = ultimo_progreso is None
    comparacion = {}

    # Construir documento de progreso
    progreso = {
        "paciente_id": ObjectId(paciente_id),
        "nutriologo_id": ObjectId(nutriologo_id),
        "fecha": data.get("fecha", datetime.utcnow().date()),
        "peso": data["peso"],
        "masa_muscular": data.get("masa_muscular"),
        "masa_grasa": data.get("masa_grasa"),
        "porcentaje_grasa_corporal": data.get("porcentaje_grasa_corporal"),
        "agua_corporal_total": data.get("agua_corporal_total"),
        "observaciones": data.get("observaciones")
    }

    # Guardar progreso
    await db.progresos.insert_one(progreso)

    # Generar notificación
    if es_primera_consulta:
        titulo = "¡Bienvenido a tu seguimiento!"
        mensaje = "Tu primera consulta ha sido registrada. A partir de ahora haremos seguimiento a tu evolución. 🎯"

        resumen = []
        if data.get("peso"):
            resumen.append(f"Peso: {data['peso']} kg")
        if data.get("masa_muscular") is not None:
            resumen.append(f"Masa muscular: {data['masa_muscular']} kg")
        if data.get("masa_grasa") is not None:
            resumen.append(f"Masa grasa: {data['masa_grasa']} kg")
        if data.get("porcentaje_grasa_corporal") is not None:
            resumen.append(f"% grasa corporal: {data['porcentaje_grasa_corporal']}%")

        if resumen:
            mensaje += "\n\n📝 Resultados iniciales:\n" + "\n".join(resumen)

    else:
        referencia = ultimo_progreso
        mensajes = []

        if referencia.get("peso") is not None and data.get("peso") is not None:
            dif = round(data["peso"] - referencia["peso"], 2)
            comparacion["peso"] = {
                "anterior": referencia["peso"],
                "actual": data["peso"],
                "diferencia": dif
            }
            if dif < 0:
                mensajes.append(f"Has bajado {abs(dif)} kg de peso.")
            elif dif > 0:
                mensajes.append(f"Has subido {dif} kg de peso.")

        if referencia.get("masa_muscular") is not None and data.get("masa_muscular") is not None:
            dif = round(data["masa_muscular"] - referencia["masa_muscular"], 2)
            comparacion["masa_muscular"] = {
                "anterior": referencia["masa_muscular"],
                "actual": data["masa_muscular"],
                "diferencia": dif
            }
            if dif > 0:
                mensajes.append(f"Ganaste {dif} kg de masa muscular 💪.")

        if referencia.get("masa_grasa") is not None and data.get("masa_grasa") is not None:
            dif = round(data["masa_grasa"] - referencia["masa_grasa"], 2)
            comparacion["masa_grasa"] = {
                "anterior": referencia["masa_grasa"],
                "actual": data["masa_grasa"],
                "diferencia": dif
            }
            if dif < 0:
                mensajes.append(f"Reduciste {abs(dif)} kg de grasa corporal 🔥.")

        if referencia.get("porcentaje_grasa_corporal") is not None and data.get("porcentaje_grasa_corporal") is not None:
            dif = round(data["porcentaje_grasa_corporal"] - referencia["porcentaje_grasa_corporal"], 2)
            comparacion["porcentaje_grasa_corporal"] = {
                "anterior": referencia["porcentaje_grasa_corporal"],
                "actual": data["porcentaje_grasa_corporal"],
                "diferencia": dif
            }
            if dif < 0:
                mensajes.append(f"Bajaste {abs(dif)}% de grasa corporal 🏆.")

        if mensajes:
            titulo = "¡Felicidades por tu progreso!"
            mensaje = " ".join(mensajes)
        else:
            titulo = "¡Seguimos trabajando!"
            mensaje = "No hubo cambios significativos esta vez. ¡Vamos con todo en la próxima consulta!"

    # Guardar notificación
    await db.notificaciones.insert_one({
        "paciente_id": ObjectId(paciente_id),
        "titulo": titulo,
        "mensaje": mensaje,
        "fecha": datetime.utcnow(),
        "leido": False
    })

    return {
        "msg": "Progreso registrado",
        "comparacion": comparacion if not es_primera_consulta else "Primera consulta - sin comparación"
    }
