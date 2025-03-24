from pydantic import BaseModel, EmailStr, Field

class NutriologoCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)

