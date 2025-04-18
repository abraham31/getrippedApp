from pydantic import BaseModel, Field
from typing import Optional


class IngredienteCreate(BaseModel):
    nombre: str
    unidad: str  # Ej: "g", "ml", "piezas"
    es_producto_tienda: bool = False
    precio: Optional[float] = None
    link_producto: Optional[str] = None
    producto_shopify_id: Optional[str] = None
    costo_extra: Optional[float] = Field(0, ge=0, example=50.0)


class IngredienteUpdate(BaseModel):
    nombre: Optional[str]
    unidad: Optional[str]
    es_producto_tienda: Optional[bool]
    precio: Optional[float]
    link_producto: Optional[str]
    producto_shopify_id: Optional[str]
    costo_extra: Optional[float] = Field(None, ge=0)


class IngredienteOut(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str
    unidad: Optional[str] = None
    es_producto_tienda: bool = False
    link_producto: Optional[str] = None
    producto_shopify_id: Optional[str] = None

    class Config:
        allow_population_by_field_name = True