from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from bson import ObjectId
from app.dependencies import get_current_user, require_role
from app.schemas.paciente import (
    PacienteUpdate,
    PacienteOut, PacienteStatusUpdate
)
from app.core.database import db
from app.services.paciente_service import crear_paciente
from app.utils.pacientes import obtener_paciente_para_nutriologo

router = APIRouter(tags=["Nutriólogo (Pacientes)"])

@router.get("/pacientes", response_model=List[PacienteOut])
async def listar_pacientes(current_user: dict = Depends(get_current_user)):
    await require_role("nutriologo", current_user)

    pacientes_raw = await db.usuarios.find({
        "nutriologo_id": current_user["sub"],
        "is_deleted": False,
        "role": "paciente"
    }).to_list(length=None)

    pacientes = []
    for p in pacientes_raw:
        pacientes.append({
            "id": str(p["_id"]),
            "nombre": p.get("nombre"),
            "email": p.get("email"),
            "is_active": p.get("is_active"),
            "sexo": p.get("sexo"),
            "fecha_nacimiento": p.get("fecha_nacimiento"),
            "peso": p.get("peso"),
            "estatura": p.get("estatura"),
        })

    return pacientes

@router.get("/pacientes/{paciente_id}", response_model=PacienteOut)
async def obtener_paciente(
    paciente_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "is_deleted": False,
        "role": "paciente"
    })

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    paciente["id"] = str(paciente["_id"])
    del paciente["_id"]

    return paciente

@router.put("/pacientes/{paciente_id}")
async def editar_paciente(
    paciente_id: str,
    data: PacienteUpdate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await obtener_paciente_para_nutriologo(paciente_id, current_user["sub"])
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": update_data}
    )
    return {"msg": "Paciente actualizado correctamente"}

@router.put("/pacientes/{paciente_id}/status")
async def cambiar_status_paciente(
    paciente_id: str,
    status: PacienteStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await obtener_paciente_para_nutriologo(paciente_id, current_user["sub"])
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": {"is_active": status.is_active}}
    )
    return {"msg": "Estado actualizado correctamente"}

@router.delete("/pacientes/{paciente_id}")
async def eliminar_paciente(
    paciente_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await obtener_paciente_para_nutriologo(paciente_id, current_user["sub"])
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": {"is_deleted": True, "is_active": False}}
    )
    return {"msg": "Paciente eliminado correctamente"}
