from fastapi import FastAPI
from app.routers import admin_router, auth_router, paciente_router

app = FastAPI(title="API Nutrición")

app.include_router(admin_router.router)
app.include_router(auth_router.router)
app.include_router(paciente_router.router)
