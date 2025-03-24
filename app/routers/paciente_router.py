from fastapi import APIRouter, HTTPException
from app.schemas.paciente import PacienteActivate
from app.services.paciente_service import activate_paciente

router = APIRouter(prefix="/paciente", tags=["Pacientes"])

@router.post("/activar-paciente")
async def activar_cuenta(token: str, data: PacienteActivate):
    result = await activate_paciente(token, data.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result