from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies import get_current_user, require_role
from app.schemas.nutriologo import NutriologoCreate
from app.core.security import verify_invite_token
from app.schemas.paciente import PacienteCreate, PacienteOut
from app.services.paciente_service import crear_paciente
from app.services.user_service import create_nutriologo
from app.core.database import db

router = APIRouter(prefix="/nutriologo", tags=["Nutriólogo"])

@router.post("/activar-nutriologo")
async def activate_nutriologo(
    data: NutriologoCreate, token: str = Query(...)
):
    try:
        verify_invite_token(token)
    except:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    existing_user = await db.usuarios.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    return await create_nutriologo(data.dict())


@router.post("/generar-paciente-invite")
async def registrar_paciente(
    data: PacienteCreate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    result = await crear_paciente(data.dict(), current_user["sub"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "msg": "Paciente registrado. Se debe enviar el enlace de activación.",
        "activation_token": result["activation_token"]
    }

