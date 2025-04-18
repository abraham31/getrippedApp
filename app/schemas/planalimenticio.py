from pydantic import BaseModel
from typing import List, Optional

class IngredientePlan(BaseModel):
    nombre: str
    cantidad: str
    producto_id: Optional[str] = None  # Si viene de la tienda
    alternativas: Optional[List["IngredientePlan"]] = None  # Ingredientes alternativos
    link_producto: Optional[str] = None
    seleccionado: Optional["IngredientePlan"] = None 

class TiempoComidaPlan(BaseModel):
    nombre: str  # ejemplo: desayuno, comida, colación, etc.
    descripcion: Optional[str] = None  # Ej: "omelette de jamón"
    ingredientes: List[IngredientePlan]

class DiaPlan(BaseModel):
    nombre: str  # Ej: "Lunes"
    comidas: List[TiempoComidaPlan]

class PlanAlimenticio(BaseModel):
    dias: List[DiaPlan]
    semanas_de_plan: int

IngredientePlan.update_forward_refs()