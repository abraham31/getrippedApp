from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.dependencies import get_current_user, require_role
from app.schemas.ingrediente import IngredienteCreate, IngredienteOut
from app.core.database import db

router = APIRouter(tags=["Ingredientes"])

@router.post("/ingredientes")
async def crear_ingrediente(
    ingrediente: IngredienteCreate,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    existe = await db.ingredientes.find_one({"nombre": ingrediente.nombre})
    if existe:
        raise HTTPException(status_code=400, detail="El ingrediente ya existe")

    await db.ingredientes.insert_one(ingrediente.dict())
    return {"msg": "Ingrediente registrado correctamente"}


@router.get("/ingredientes", response_model=List[IngredienteOut])
async def listar_ingredientes(nombre: Optional[str] = Query(None, description="Filtro por nombre")):
    filtro = {}
    if nombre:
        filtro["nombre"] = {"$regex": nombre, "$options": "i"}

    ingredientes = await db.ingredientes.find(filtro).sort("nombre", 1).to_list(length=20)
    return [{**i, "id": str(i["_id"])} for i in ingredientes]