from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi
from app.routers import admin_router, auth_router, paciente_router, nutriologo_router

app = FastAPI(title="API Nutrición")

# Incluir routers
app.include_router(admin_router.router)
app.include_router(auth_router.router)
app.include_router(paciente_router.router)
app.include_router(nutriologo_router.router)

# Seguridad para Swagger (HTTP Bearer)
bearer_scheme = HTTPBearer()

# Custom OpenAPI para agregar Bearer Token en Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Nutrición",
        version="1.0",
        description="API para gestión de nutrición",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
