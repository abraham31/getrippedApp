from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from app.dependencies import get_current_user, require_role
from app.schemas.notificacion import NotificacionResponse
from app.schemas.paciente import PacienteActivate
from app.schemas.notificacion import NotificacionResponse
from app.services.paciente_service import activate_paciente, generar_resumen_visual, generar_imagen_con_progreso
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

    progreso = None
    if "consulta_id" in notificacion:
        consulta = await db.consultas.find_one({"_id": notificacion["consulta_id"]})
        if consulta:
            progreso = consulta.get("progreso")

    return {
        "id": str(notificacion["_id"]),
        "titulo": notificacion["titulo"],
        "mensaje": notificacion["mensaje"],
        "fecha": notificacion["fecha"],
        "leido": True,
        "progreso": progreso  
    }

@router.get("/notificaciones/{notificacion_id}/imagen")
async def generar_imagen_progreso(
    notificacion_id: str,
    current_user: dict = Depends(get_current_user)
):
    await require_role("paciente", current_user)

    noti = await db.notificaciones.find_one({
        "_id": ObjectId(notificacion_id),
        "paciente_id": ObjectId(current_user["sub"])
    })

    if not noti:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")

    if "consulta_id" not in noti:
        raise HTTPException(status_code=400, detail="Aún no hay un progreso registrado para generar una imagen.")

    consulta = await db.consultas.find_one({"_id": noti["consulta_id"]})
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    progreso = consulta.get("progreso")
    if not progreso:
        raise HTTPException(status_code=400, detail="Aún no hay un progreso registrado para generar una imagen.")

    # Obtener consulta anterior
    consultas_previas = await db.consultas.find({
        "paciente_id": ObjectId(current_user["sub"]),
        "_id": {"$ne": consulta["_id"]}
    }).sort("fecha", -1).to_list(length=1)

    anterior = consultas_previas[0]["progreso"] if consultas_previas else None
    resumen = generar_resumen_visual(progreso, anterior)

    paciente = await db.usuarios.find_one({"_id": ObjectId(current_user["sub"])})
    nutriologo = await db.usuarios.find_one({"_id": consulta["nutriologo_id"]})

    image_bytes = generar_imagen_con_progreso(
        nombre_paciente=paciente["nombre"],
        nombre_nutriologo=nutriologo["nombre"],
        resumen=resumen
    )

    return Response(content=image_bytes, media_type="image/png")



