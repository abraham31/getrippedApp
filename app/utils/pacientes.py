from bson import ObjectId
from fastapi import HTTPException
from app.core.database import db


async def validar_paciente_activo(paciente_id: str, nutriologo_id: str):
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": nutriologo_id,
        "role": "paciente",
        "is_deleted": False
    })
    return paciente


async def obtener_paciente_para_nutriologo(paciente_id: str, nutriologo_id: str):
    paciente = await validar_paciente_activo(paciente_id, nutriologo_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente
