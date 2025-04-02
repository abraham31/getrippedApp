from pydantic import BaseModel, Field
from typing import List, Optional

class IngredientePlan(BaseModel):
    nombre: str
    cantidad: str  # Ej: "100g", "1 pieza"
    alternativas: Optional[List[str]] = []  # Ej: ["machaca", "jamón de pavo"]
    es_tienda: Optional[bool] = False
    link_producto: Optional[str] = None

class ComidaPlan(BaseModel):
    nombre: str  # Ej: "Desayuno", "Comida", "Cena"
    descripcion: Optional[str] = None  # Ej: "Omelette de jamón"
    ingredientes: List[IngredientePlan]

class DiaPlan(BaseModel):
    dia: str  # Ej: "Lunes", "Martes"
    comidas: List[ComidaPlan]

class PlanAlimenticioCreate(BaseModel):
    consulta_id: str
    dias: List[DiaPlan]