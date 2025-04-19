from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.dependencies import get_current_user, require_role
from app.schemas.nutriologo import NutriologoCreate
from app.core.security import verify_invite_token
from app.schemas.paciente import PacienteCreate
from app.schemas.product import ProductoRecomendadoCreate, ProductoRecomendadoUpdate
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

@router.post("/productos-recomendados")
async def registrar_producto_recomendado(
    data: ProductoRecomendadoCreate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    producto = data.dict()
    producto["nutriologo_id"] = ObjectId(current_user["sub"])
    producto["fecha"] = datetime.utcnow()

    await db.productos_recomendados.insert_one(producto)

    return {"msg": "Producto recomendado registrado correctamente"}

@router.put("/nutriologo/productos-recomendados/{producto_id}")
async def actualizar_producto_recomendado(
    producto_id: str = Path(..., description="ID del producto recomendado"),
    data: ProductoRecomendadoUpdate = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")

    result = await db.productos_recomendados.update_one(
        {
            "_id": ObjectId(producto_id),
            "nutriologo_id": ObjectId(current_user["sub"])
        },
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado o no autorizado")

    return {"msg": "Producto actualizado correctamente"}

