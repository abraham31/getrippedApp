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

    await db.progresos.insert_one(progreso)

    return {"msg": "Progreso registrado", "comparacion": comparacion}