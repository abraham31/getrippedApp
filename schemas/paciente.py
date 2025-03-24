from pydantic import BaseModel, EmailStr, Field

class PacienteCreate(BaseModel):
    nombre: str = Field(..., min_length=2)
    email: EmailStr
    curp: str = Field(..., min_length=18, max_length=18)

class PacienteActivate(BaseModel):
    password: str = Field(..., min_length=6)
