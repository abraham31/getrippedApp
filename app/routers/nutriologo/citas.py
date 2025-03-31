from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, require_role
from app.schemas.cita import CitaCreate, CitaOut, CitaUpdate
from app.core.database import db

router = APIRouter(tags=["Citas"])

@router.post("/pacientes/{paciente_id}/citas")
async def agendar_cita(
    paciente_id: str,
    data: CitaCreate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente",
        "is_deleted": False
    })
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    cita = {
        "paciente_id": ObjectId(paciente_id),
        "nutriologo_id": ObjectId(current_user["sub"]),
        "fecha": data.fecha,
        "motivo": data.motivo,
        "estado": "activa",
        "creada_en": datetime.utcnow()
    }

    await db.citas.insert_one(cita)
    return {"msg": "Cita agendada correctamente"}

@router.get("/citas", response_model=List[CitaOut])
async def obtener_citas_nutriologo(current_user: dict = Depends(get_current_user)):
    await require_role("nutriologo", current_user)

    citas = await db.citas.find({
        "nutriologo_id": ObjectId(current_user["sub"]),
        "estado": "activa"
    }).sort("fecha", 1).to_list(length=None)

    # Convertir ObjectId a str
    for c in citas:
        c["_id"] = str(c["_id"])
        c["paciente_id"] = str(c["paciente_id"])

    return citas

@router.put("/citas/{cita_id}")
async def actualizar_cita(
    cita_id: str,
    data: CitaUpdate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    cita = await db.citas.find_one({"_id": ObjectId(cita_id)})
    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    if str(cita["nutriologo_id"]) != current_user["sub"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No se envió ningún dato para actualizar")

    await db.citas.update_one({"_id": ObjectId(cita_id)}, {"$set": update_data})

    return {"msg": "Cita actualizada correctamente"}
