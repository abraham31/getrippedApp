from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


class ProductoRecomendadoCreate(BaseModel):
    nombre: str
    marca: Optional[str]
    donde_comprar: Optional[str]
    imagen_url: Optional[HttpUrl]
    link_shopify: Optional[HttpUrl]

class ProductoRecomendadoUpdate(BaseModel):
    nombre: Optional[str]
    marca: Optional[str]
    donde_comprar: Optional[str]
    imagen_url: Optional[HttpUrl]
    link_shopify: Optional[HttpUrl]

class ProductoRecomendadoOut(BaseModel):
    id: str = Field(..., alias="_id")
    nombre: str
    marca: Optional[str]
    donde_comprar: Optional[str]
    imagen_url: Optional[HttpUrl]
    link_shopify: Optional[HttpUrl]

    class Config:
        allow_population_by_field_name = True