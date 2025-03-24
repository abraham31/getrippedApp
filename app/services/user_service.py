from app.core.database import db
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status

async def create_nutriologo(data: dict):
    user = {
        "nombre": data["nombre"],
        "email": data["email"],
        "password": hash_password(data["password"]),
        "role": "nutriologo",
        "is_active": True  # <- Aquí!
    }
    await db.usuarios.insert_one(user)
    return {"msg": "Nutriólogo creado correctamente"}

async def authenticate_user(email: str, password: str):
    user = await db.usuarios.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    if not user.get("is_active", False):
        raise HTTPException(status_code=403, detail="Usuario inactivo")   
    # Aquí generamos el token JWT
    token_data = {
        "sub": str(user["_id"]),
        "role": user["role"]
    }
    token = create_access_token(token_data)
    return token
