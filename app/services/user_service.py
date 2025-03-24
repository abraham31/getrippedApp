from app.core.database import db
from app.core.security import hash_password, verify_password, create_access_token

async def create_nutriologo(data: dict):
    user = {
        "nombre": data["nombre"],
        "email": data["email"],
        "password": hash_password(data["password"]),
        "curp": data["curp"],
        "role": "nutriologo",
        "is_active": True  # <- Aquí!
    }
    await db.usuarios.insert_one(user)
    return {"msg": "Nutriólogo creado correctamente"}

async def authenticate_user(email: str, password: str):
    user = await db.usuarios.find_one({"email": email})
    if not user:
        return None

    if not verify_password(password, user["password"]):
        return None
    
    if not user.get("is_active", False):
        return None     
    # Aquí generamos el token JWT
    token_data = {
        "sub": str(user["_id"]),
        "role": user["role"]
    }
    token = create_access_token(token_data)
    return token
