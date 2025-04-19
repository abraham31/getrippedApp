from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, Path, HTTPException, Query
from app.dependencies import get_current_user, require_role
from app.schemas.ingrediente import IngredienteCreate, IngredienteOut, IngredienteUpdate
from app.core.database import db
from app.schemas.product import ProductoRecomendadoOut

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

@router.put("/ingredientes/{ingrediente_id}")
async def actualizar_ingrediente(
    ingrediente_id: str = Path(..., description="ID del ingrediente"),
    data: IngredienteUpdate = ...,
    current_user: dict = Depends(get_current_user)
):
    await require_role("nutriologo", current_user)

    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar")

    result = await db.ingredientes.update_one(
        {"_id": ObjectId(ingrediente_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

    return {"msg": "Ingrediente actualizado correctamente"}

@router.get("/ingredientes", response_model=List[IngredienteOut])
async def listar_ingredientes(nombre: Optional[str] = Query(None, description="Filtro por nombre")):
    filtro = {}
    if nombre:
        filtro["nombre"] = {"$regex": nombre, "$options": "i"}

    ingredientes = await db.ingredientes.find(filtro).sort("nombre", 1).to_list(length=20)
    return [{**i, "id": str(i["_id"])} for i in ingredientes]

@router.get("/productos-recomendados", response_model=List[ProductoRecomendadoOut])
async def listar_productos_recomendados(current_user: dict = Depends(get_current_user)):
    # Cualquier usuario autenticado puede ver esta lista
    productos = await db.productos_recomendados.find().to_list(length=None)

@router.get("/productos-recomendados", response_model=List[ProductoRecomendadoOut])
async def listar_productos_recomendados(
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    marca: Optional[str] = Query(None, description="Buscar por marca"),
    current_user: dict = Depends(get_current_user)
):
    filtro = {}
    if nombre:
        filtro["nombre"] = {"$regex": nombre, "$options": "i"}
    if marca:
        filtro["marca"] = {"$regex": marca, "$options": "i"}

    productos = await db.productos_recomendados.find(filtro).to_list(length=None)
    return productos
