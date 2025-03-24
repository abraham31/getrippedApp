from core.database import db
from core.security import create_activation_token, verify_activation_token, hash_password
from email_service import send_activation_email
from bson import ObjectId

async def create_paciente(data: dict, nutriologo_id: str):
    # Verificar si ya existe paciente con ese email
    existing = await db.usuarios.find_one({"email": data["email"]})
    if existing:
        return {"error": "Email ya registrado"}

    paciente = {
        "nombre": data["nombre"],
        "email": data["email"],
        "curp": data["curp"],
        "role": "paciente",
        "nutriologo_id": nutriologo_id,
        "is_active": False,
        "password": None  # Se establecerá cuando el paciente active su cuenta
    }

    result = await db.usuarios.insert_one(paciente)

    # Generar token de activación
    activation_token = create_activation_token(str(result.inserted_id))
    
    return {
        "msg": "Paciente creado",
        "activation_token": activation_token  # Temporal, luego enviaremos por correo
    }

async def create_paciente(data: dict, nutriologo_id: str):
    # Verificar si ya existe paciente con ese email
    existing = await db.usuarios.find_one({"email": data["email"]})
    if existing:
        return {"error": "Email ya registrado"}

    paciente = {
        "nombre": data["nombre"],
        "email": data["email"],
        "curp": data["curp"],
        "role": "paciente",
        "nutriologo_id": nutriologo_id,
        "is_active": False,
        "password": None
    }

    result = await db.usuarios.insert_one(paciente)

    # Generar token de activación
    activation_token = create_activation_token(str(result.inserted_id))

    # Enviar correo al paciente
    try:
        send_activation_email(data["email"], activation_token)
    except:
        return {"error": "Error enviando email"}

    return {
        "msg": "Paciente creado, email de activación enviado."
    }

async def activate_paciente(token: str, password: str):
    try:
        payload = verify_activation_token(token)
        paciente_id = payload["user_id"]
    except:
        return {"error": "Token inválido o expirado"}

    paciente = await db.usuarios.find_one({"_id": ObjectId(paciente_id)})
    if not paciente:
        return {"error": "Paciente no encontrado"}

    if paciente.get("is_active"):
        return {"error": "Cuenta ya activada"}

    await db.usuarios.update_one(
        {"_id": ObjectId(paciente_id)},
        {
            "$set": {
                "password": hash_password(password),
                "is_active": True
            }
        }
    )
    return {"msg": "Cuenta activada correctamente"}