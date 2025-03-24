from fastapi import APIRouter, Depends, HTTPException
from schemas.paciente import PacienteCreate, PacienteActivate
from services.paciente_service import create_paciente, activate_paciente
from dependencies import get_current_user, require_role

router = APIRouter(prefix="/nutriologo", tags=["Pacientes"])

@router.post("/pacientes")
async def registrar_paciente(
    data: PacienteCreate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    result = await create_paciente(data.dict(), current_user["sub"])
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "msg": "Paciente registrado. Se debe enviar el enlace de activación.",
        "activation_token": result["activation_token"]
    }

@router.post("/activate-account")
async def activar_cuenta(token: str, data: PacienteActivate):
    result = await activate_paciente(token, data.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result