from pydantic import BaseModel, EmailStr, Field

class PacienteCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    email: EmailStr

class PacienteActivate(BaseModel):
    password: str = Field(..., min_length=6)
