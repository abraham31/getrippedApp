from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path
from app.dependencies import get_current_user, require_role
from app.schemas.notificacion import NotificacionPreview, NotificacionResponse
from app.schemas.paciente import PacienteActivate
from app.schemas.notificacion import NotificacionResponse
from app.services.paciente_service import activate_paciente
from bson import ObjectId
from app.core.database import db

router = APIRouter(prefix="/paciente", tags=["Paciente (App)"])

@router.post("/activar-paciente")
async def activar_cuenta(token: str, data: PacienteActivate):
    result = await activate_paciente(token, data.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/notificaciones", response_model=List[NotificacionResponse])
async def listar_notificaciones(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    notificaciones_cursor = db.notificaciones.find({
        "paciente_id": ObjectId(current_user["sub"])
    }, sort=[("fecha", -1)])

    notificaciones = []
    async for n in notificaciones_cursor:
        notificaciones.append({
            "id": str(n["_id"]),
            "titulo": n["titulo"],
            "mensaje": n["mensaje"],
            "fecha": n["fecha"],
            "leido": n["leido"]
        })

    return notificaciones

@router.get("/notificaciones", response_model=List[NotificacionPreview])
async def listar_notificaciones(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    notificaciones_cursor = db.notificaciones.find({
        "paciente_id": ObjectId(current_user["sub"])
    }, sort=[("fecha", -1)])

    notificaciones = []
    async for n in notificaciones_cursor:
        notificaciones.append({
            "id": str(n["_id"]),
            "titulo": n["titulo"],
            "fecha": n["fecha"],
            "leido": n["leido"]
        })

    return notificaciones

@router.get("/notificaciones/{notificacion_id}", response_model=NotificacionResponse)
async def obtener_notificacion(
    notificacion_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("paciente", current_user)

    notificacion = await db.notificaciones.find_one({
        "_id": ObjectId(notificacion_id),
        "paciente_id": ObjectId(current_user["sub"])
    })

    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    # Marcar como leída
    await db.notificaciones.update_one(
        {"_id": ObjectId(notificacion_id)},
        {"$set": {"leido": True}}
    )

    return {
        "id": str(notificacion["_id"]),
        "titulo": notificacion["titulo"],
        "mensaje": notificacion["mensaje"],
        "fecha": notificacion["fecha"],
        "leido": True  # Ya está marcada como leída
    }
