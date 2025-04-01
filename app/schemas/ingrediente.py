from pydantic import BaseModel, Field
from typing import Optional


class IngredienteCreate(BaseModel):
    nombre: str
    unidad: str  # Ej: "g", "ml", "piezas"
    es_producto_tienda: bool = False
    enlace_producto: Optional[str] = None

class IngredienteOut(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str
    unidad: Optional[str] = None
    es_tienda: bool = False
    link: Optional[str] = None

    class Config:
        allow_population_by_field_name = True