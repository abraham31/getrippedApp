from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from app.core.database import db
from app.dependencies import get_current_user, require_role
from app.schemas.planalimenticio import PlanAlimenticio

router = APIRouter(tags=["Consulta"])

@router.post("/consultas/{consulta_id}/plan")
async def asignar_plan_alimenticio(
    consulta_id: str = Path(..., description="ID de la consulta"),
    plan: PlanAlimenticio = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    # Buscar la consulta
    consulta = await db.consultas.find_one({
        "_id": ObjectId(consulta_id),
        "nutriologo_id": ObjectId(current_user["sub"])
    })

    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # Insertar plan
    plan_dict = plan.dict()
    plan_dict["created_at"] = datetime.utcnow()
    result = await db.planes.insert_one(plan_dict)

    # Actualizar consulta con el ID del plan
    await db.consultas.update_one(
        {"_id": ObjectId(consulta_id)},
        {"$set": {"plan_id": result.inserted_id}}
    )

    return {"msg": "Plan alimenticio asignado exitosamente", "plan_id": str(result.inserted_id)}

@router.get("/consultas/{consulta_id}/plan", response_model=PlanAlimenticio)
async def obtener_plan_alimenticio(
    consulta_id: str = Path(..., description="ID de la consulta"),
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    consulta = await db.consultas.find_one({
        "_id": ObjectId(consulta_id),
        "nutriologo_id": ObjectId(current_user["sub"])
    })

    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    plan_id = consulta.get("plan_id")
    if not plan_id:
        raise HTTPException(status_code=404, detail="Esta consulta no tiene un plan asignado")

    plan = await db.planes.find_one({"_id": plan_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan alimenticio no encontrado")

    return plan

@router.put("/consultas/{consulta_id}/plan", response_model=dict)
async def actualizar_plan_alimenticio(
    consulta_id: str = Path(..., description="ID de la consulta"),
    plan: PlanAlimenticio = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    consulta = await db.consultas.find_one({
        "_id": ObjectId(consulta_id),
        "nutriologo_id": ObjectId(current_user["sub"])
    })

    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")

    # Crear nuevo plan
    plan_dict = plan.dict()
    plan_dict["created_at"] = datetime.utcnow()
    nuevo_plan = await db.planes.insert_one(plan_dict)

    # Actualizar la consulta con el nuevo plan
    await db.consultas.update_one(
        {"_id": ObjectId(consulta_id)},
        {"$set": {"plan_id": nuevo_plan.inserted_id}}
    )

    return {"msg": "Plan alimenticio actualizado correctamente", "plan_id": str(nuevo_plan.inserted_id)}