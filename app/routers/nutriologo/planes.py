from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from app.core.database import db
from app.dependencies import get_current_user, require_role
from app.schemas.planalimenticio import PlanAlimenticio

router = APIRouter(tags=["Consulta"])


@router.post("/pacientes/{paciente_id}/plan-alimenticio")
async def crear_plan_alimenticio(
    paciente_id: str = Path(..., description="ID del paciente"),
    plan: PlanAlimenticio = Body(...),
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    # Validar que el paciente pertenezca al nutriólogo
    paciente = await db.usuarios.find_one({
        "_id": ObjectId(paciente_id),
        "nutriologo_id": current_user["sub"],
        "role": "paciente",
        "is_deleted": False
    })
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Crear documento
    documento = {
        "paciente_id": ObjectId(paciente_id),
        "nutriologo_id": ObjectId(current_user["sub"]),
        "plan": plan.dict(by_alias=True),
        "fecha_creacion": datetime.utcnow()
    }

    await db.planes_alimenticios.insert_one(documento)

    return {"msg": "Plan alimenticio registrado correctamente"}
