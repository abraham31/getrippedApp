from pydantic import BaseModel
from datetime import datetime

class NotificacionResponse(BaseModel):
    id: str
    titulo: str
    mensaje: str
    fecha: datetime
    leido: bool

    class Config:
        from_attributes = True

class NotificacionPreview(BaseModel):
    id: str
    titulo: str
    fecha: datetime
    leido: bool

    class Config:
        from_attributes = True

