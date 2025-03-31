from datetime import datetime
from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, Path, HTTPException
from app.dependencies import get_current_user, require_role
from app.schemas.consulta import ConsultaOut, ConsultaCreate
from app.services.consulta_service import crear_consulta
from app.core.database import db

router = APIRouter(tags=["Consulta"])

@router.post("/pacientes/{paciente_id}/consultas")
async def registrar_consulta(
    paciente_id: str = Path(..., description="ID del paciente"),
    data: ConsultaCreate = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    # Validar paciente
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente",
        "is_deleted": False
    })
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Consultas anteriores
    consultas_anteriores = await db.consultas.find({
        "paciente_id": ObjectId(paciente_id)
    }).sort("fecha", -1).to_list(length=1)

    # Generar consulta + notificación
    resultado = crear_consulta(paciente_id, current_user["sub"], data.dict(), consultas_anteriores)

    # Insertar la consulta y obtener su ID generado por MongoDB
    insert_result = await db.consultas.insert_one(resultado["consulta"])
    consulta_id = insert_result.inserted_id

    # Insertar la notificación, vinculándola a la consulta
    await db.notificaciones.insert_one({
        "paciente_id": ObjectId(paciente_id),
        "titulo": resultado["notificacion"]["titulo"],
        "mensaje": resultado["notificacion"]["mensaje"],
        "fecha": datetime.utcnow(),
        "leido": False,
        "consulta_id": consulta_id
    })

    return {"msg": "Consulta registrada correctamente"}

@router.get("/pacientes/{paciente_id}/consultas", response_model=List[ConsultaOut])
async def obtener_historial_consultas(
    paciente_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente"
    })

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    consultas = await db.consultas.find(
        {"paciente_id": ObjectId(paciente_id)}
    ).sort("fecha", -1).to_list(length=None)

    return [
        {
            "id": str(c["_id"]),
            "fecha": c["fecha"],
            "tipo": c["tipo"],
            "progreso": c["progreso"],
            "observaciones": c.get("observaciones")
        }
        for c in consultas
    ]

@router.get("/consultas/{consulta_id}", response_model=ConsultaOut)
async def detalle_consulta(
    consulta_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    consulta = await db.consultas.find_one({"_id": ObjectId(consulta_id)})
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # Validar que el paciente le pertenezca
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(consulta["paciente_id"]),
        "nutriologo_id": current_user["sub"]
    })
    if not paciente:
        raise HTTPException(status_code=403, detail="No autorizado para ver esta consulta")

    return {
        "fecha": consulta["fecha"],
        "tipo": consulta["tipo"],
        "progreso": consulta["progreso"],
        "observaciones": consulta.get("observaciones")
    }

