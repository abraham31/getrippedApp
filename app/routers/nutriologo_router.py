from fastapi import Depends, Path, Body, APIRouter, HTTPException, Query
from bson import ObjectId
from app.dependencies import get_current_user, require_role
from app.schemas.nutriologo import NutriologoCreate
from app.schemas.paciente import PacienteUpdate, PacienteCreate
from app.core.security import verify_invite_token
from app.services.user_service import create_nutriologo
from app.services.paciente_service import create_paciente
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

@router.get("/pacientes")
async def listar_pacientes(current_user: dict = Depends(get_current_user)):
    await require_role("nutriologo", current_user)

    pacientes_cursor = db.usuarios.find({
        "nutriologo_id": current_user["sub"],
        "is_deleted": False,
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
        "is_deleted": False,
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

@router.delete("/pacientes/{paciente_id}")
async def eliminar_paciente(
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

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": {"is_deleted": True, "is_active": False}}
    )

    return {"msg": "Paciente eliminado correctamente"}

@router.put("/pacientes/{paciente_id}/status")
async def cambiar_status_paciente(
    paciente_id: str,
    status: dict = Body(...),
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

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": {"is_active": status.get("is_active", False)}}
    )

    return {"msg": "Estado actualizado correctamente"}

@router.put("/pacientes/{paciente_id}")
async def editar_paciente(
    paciente_id: str,
    data: PacienteUpdate,
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

    # Solo actualizamos campos enviados
    update_data = {k: v for k, v in data.dict().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {"$set": update_data}
    )

    return {"msg": "Paciente actualizado correctamente"}