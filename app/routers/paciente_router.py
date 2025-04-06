from datetime import date, datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Response
from app.dependencies import get_current_user, require_role
from app.schemas.notificacion import NotificacionResponse
from app.schemas.paciente import CumplimientoCreate, CumplimientoSemana, DiaCumplido, PacienteActivate
from app.schemas.notificacion import NotificacionResponse
from app.schemas.planalimenticio import PlanAlimenticio
from app.services.paciente_service import activate_paciente, generar_resumen_visual, generar_resumen_visual_semana, generar_imagen_con_progreso
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
            "leido": n["leido"],
            "tipo": n.get("tipo", "otro")
        })

    return notificaciones

@router.get("/notificaciones/{notificacion_id}/imagen")
async def generar_imagen_notificacion(
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

    paciente = await db.usuarios.find_one({"_id": ObjectId(current_user["sub"])})
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if noti["tipo"] == "progreso":
        if "consulta_id" not in noti:
            raise HTTPException(status_code=400, detail="Esta notificación no tiene progreso asociado.")

        consulta = await db.consultas.find_one({"_id": noti["consulta_id"]})
        if not consulta:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")

        progreso = consulta.get("progreso")
        if not progreso:
            raise HTTPException(status_code=400, detail="La consulta no tiene datos de progreso.")

        # Buscar una consulta anterior para comparar
        consultas_previas = await db.consultas.find({
            "paciente_id": ObjectId(current_user["sub"]),
            "_id": {"$ne": consulta["_id"]}
        }).sort("fecha", -1).to_list(length=1)

        if not consultas_previas:
            raise HTTPException(status_code=400, detail="Se necesita al menos una consulta anterior para comparar el progreso.")

        anterior = consultas_previas[0].get("progreso")
        resumen = generar_resumen_visual(progreso, anterior)

        nutriologo = await db.usuarios.find_one({"_id": consulta["nutriologo_id"]})
        nombre_nutriologo = nutriologo["nombre"] if nutriologo else "tu nutriólogo"

    elif noti["tipo"] == "resumen_semanal":
        total = noti.get("total_comidas", 0)
        cumplidas = noti.get("comidas_cumplidas", 0)
        porcentaje = round((cumplidas / total) * 100, 2) if total else 0

        resumen = generar_resumen_visual_semana(porcentaje, total, cumplidas)
        nombre_nutriologo = "tu nutriólogo"  # Aquí no hay relación directa con consulta

    else:
        raise HTTPException(status_code=400, detail="Este tipo de notificación no admite imagen.")

    image_bytes = generar_imagen_con_progreso(
        nombre_paciente=paciente["nombre"],
        nombre_nutriologo=nombre_nutriologo,
        resumen=resumen
    )

    return Response(content=image_bytes, media_type="image/png")


@router.get("/paciente/plan", response_model=PlanAlimenticio)
async def obtener_plan_actual_paciente(current_user: dict = Depends(get_current_user)):
    await require_role("paciente", current_user)

    # Buscar la consulta más reciente del paciente que tenga un plan asignado
    consulta = await db.consultas.find_one(
        {
            "paciente_id": ObjectId(current_user["sub"]),
            "plan_id": {"$exists": True}
        },
        sort=[("fecha", -1)]
    )

    if not consulta:
        raise HTTPException(status_code=404, detail="No se encontró un plan alimenticio asignado")

    plan = await db.planes.find_one({"_id": consulta["plan_id"]})
    if not plan:
        raise HTTPException(status_code=404, detail="El plan alimenticio no fue encontrado")

    return plan

@router.post("/pacientes/{paciente_id}/resumen-semanal")
async def generar_resumen_semanal(
    paciente_id: str = Path(..., description="ID del paciente"),
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    # Verifica que el paciente pertenezca al nutriólogo
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente"
    })
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar el cumplimiento de la semana más reciente (últimos 7 días)
    siete_dias_atras = datetime.utcnow() - timedelta(days=7)
    registros = await db.cumplimiento.find({
        "paciente_id": ObjectId(paciente_id),
        "fecha": {"$gte": siete_dias_atras}
    }).to_list(length=None)

    total_comidas = 0
    comidas_cumplidas = 0

    for registro in registros:
        for comida, cumplido in registro["cumplimiento"].items():
            total_comidas += 1
            if cumplido:
                comidas_cumplidas += 1

    if total_comidas == 0:
        raise HTTPException(status_code=400, detail="No hay registros de cumplimiento esta semana")

    porcentaje = round((comidas_cumplidas / total_comidas) * 100)

    # Mensaje motivacional
    if porcentaje >= 90:
        mensaje = "¡Excelente trabajo esta semana! ¡Sigue así! 💪"
    elif porcentaje >= 70:
        mensaje = "¡Buen avance! Puedes mejorar un poco más 🔥"
    else:
        mensaje = "¡No te desanimes! La constancia es la clave. 🚀"

    # Crear la notificación
    await db.notificaciones.insert_one({
        "paciente_id": ObjectId(paciente_id),
        "titulo": "Resumen semanal de cumplimiento",
        "mensaje": f"Comidas cumplidas: {comidas_cumplidas} de {total_comidas} ({porcentaje}%)\n{mensaje}",
        "fecha": datetime.utcnow(),
        "leido": False,
        "tipo": "resumen_semanal"
    })

    return {
        "msg": "Resumen semanal generado exitosamente",
        "porcentaje": porcentaje,
        "comidas_cumplidas": comidas_cumplidas,
        "total_comidas": total_comidas
    }

@router.get("/notificaciones/{notificacion_id}")
async def detalle_notificacion(
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

    # Marcar como leída
    await db.notificaciones.update_one(
        {"_id": noti["_id"]},
        {"$set": {"leido": True}}
    )

    detalle = {
        "id": str(noti["_id"]),
        "tipo": noti.get("tipo", "otro"),
        "titulo": noti["titulo"],
        "mensaje": noti["mensaje"],
        "fecha": noti["fecha"],
        "leido": True,
        "puede_generar_imagen": False,
    }

    # Si la notificación incluye progreso
    if noti.get("tipo") == "progreso" and "consulta_id" in noti:
        consulta = await db.consultas.find_one({"_id": noti["consulta_id"]})
        if consulta and consulta.get("progreso"):
            detalle["progreso"] = consulta["progreso"]
            detalle["puede_generar_imagen"] = True

    elif noti.get("tipo") == "resumen_semana":
        detalle["puede_generar_imagen"] = True

    return detalle









