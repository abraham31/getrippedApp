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

    # Buscar último progreso registrado (si existe)
    ultimo_progreso = await db.progresos.find_one(
        {"paciente_id": ObjectId(paciente_id)},
        sort=[("fecha", -1)]
    )

    # Comparativa
    if ultimo_progreso:
        comparacion = {
            "peso_anterior": ultimo_progreso["peso"],
            "peso_actual": data["peso"],
            "diferencia_peso": round(data["peso"] - ultimo_progreso["peso"], 2)
        }
    else:
        comparacion = {
            "peso_inicial": paciente["peso"],
            "peso_actual": data["peso"],
            "diferencia_peso": round(data["peso"] - paciente["peso"], 2)
        }

    # Insertar progreso
    progreso = data.copy()
    progreso.update({
        "paciente_id": ObjectId(paciente_id),
        "nutriologo_id": ObjectId(nutriologo_id),
        "fecha": data.get("fecha", datetime.utcnow().date())
    })

    # Después de guardar el progreso
    await db.progresos.insert_one(progreso)

    # Generar mensaje motivacional basado en comparativa
    if "peso_anterior" in comparacion or "peso_inicial" in comparacion:
        diferencia = comparacion.get("diferencia_peso", 0)
        if diferencia < 0:
            titulo = "¡Felicidades por tu progreso!"
            mensaje = f"Desde tu inicio has bajado {abs(diferencia)} kg. ¡Sigue así!"
        elif diferencia > 0:
            titulo = "¡Sigamos avanzando!"
            mensaje = f"Aumentaste {diferencia} kg desde el último registro. ¡Podemos mejorar juntos!"
        else:
            titulo = "¡Mantenemos el ritmo!"
            mensaje = "Tu peso se mantiene igual. ¡No te detengas!"

        # Guardar notificación en Mongo
        await db.notificaciones.insert_one({
            "paciente_id": ObjectId(paciente_id),
            "titulo": titulo,
            "mensaje": mensaje,
            "fecha": datetime.utcnow(),
            "leido": False
        })

    return {"msg": "Progreso registrado", "comparacion": comparacion}