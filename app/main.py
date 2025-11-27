# app/main.py
from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.rol_routes import routerRole as role_router
from routes.type_document_routes import router as type_document_router
from routes.appointment_routes import router as appointment_router
from routes.module_routes import router as module_router
from routes.module_x_rol_routes import router as module_x_rol_router
from routes.disease_type_routes import router as disease_type_router
from routes.state_appointment_routes import router as state_appointment_router
from routes.state_analysis_routes import router as state_analysis_router
from routes.users_x_attribute_routes import router as users_x_attribute_router
from routes.analysis_routes import router as analysis_router
from routes.patient_routes import router as patient_router
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os



app = FastAPI()

# === NUEVO: servir carpeta uploads ===
BASE_DIR = Path(__file__).resolve().parent  # -> /.../Backend/FastApi/app
UPLOADS_DIR = BASE_DIR / "uploads"          # -> /.../Backend/FastApi/app/uploads

# Crear la carpeta si no existe (por si acaso)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Montar /uploads -> carpeta física app/uploads
app.mount(
    "/uploads",                            # URL donde se accederá
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads"
)   

# --- ⚙️ Ajuste aquí ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(role_router)
app.include_router(type_document_router)
app.include_router(appointment_router)  # Nueva ruta
app.include_router(module_router)
app.include_router(module_x_rol_router)
app.include_router(disease_type_router)
app.include_router(state_appointment_router)
app.include_router(state_analysis_router)
app.include_router(users_x_attribute_router)
app.include_router(analysis_router)
app.include_router(patient_router)

# Servir la carpeta uploads como archivos estáticos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


#app.include_router()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
