from fastapi import Depends, Path, APIRouter, HTTPException, Query
from bson import ObjectId
from app.dependencies import get_current_user, require_role
from app.schemas.nutriologo import NutriologoCreate
from app.core.security import verify_invite_token
from app.services.user_service import create_nutriologo
from app.core.database import db

router = APIRouter(prefix="/nutriologo", tags=["Nutriólogo"])

@router.post("/register")
async def register_nutriologo(
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

@router.get("/pacientes")
async def listar_pacientes(current_user: dict = Depends(get_current_user)):
    await require_role("nutriologo", current_user)

    pacientes_cursor = db.usuarios.find({
        "nutriologo_id": current_user["sub"],
        "role": "paciente"
    })

    pacientes = []
    async for paciente in pacientes_cursor:
        pacientes.append({
            "id": str(paciente["_id"]),
            "nombre": paciente["nombre"],
            "email": paciente["email"],
            "is_active": paciente["is_active"]
        })

    return {"pacientes": pacientes}

@router.get("/pacientes/{paciente_id}")
async def obtener_paciente(
    paciente_id: str = Path(..., description="ID del paciente"),
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

    paciente_info = {
        "id": str(paciente["_id"]),
        "nombre": paciente["nombre"],
        "email": paciente["email"],
        "is_active": paciente["is_active"],
        # Agregamos más campos si quieres incluir más info nutricional
    }

    return paciente_info