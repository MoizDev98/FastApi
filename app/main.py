# app/main.py
from fastapi import FastAPI
from routes.user_routes import router as user_router
from routes.rol_routes import routerRole as role_router
from routes.type_document_routes import router as type_document_router
from routes.auth_router import router as router_login
from routes.appointment_routes import router as appointment_router  # Nueva ruta
#from routes.analysis_routes import router as analysis_router      # Nueva ruta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
app.include_router(role_router)
app.include_router(type_document_router)
app.include_router(router_login)
app.include_router(appointment_router)  # Nueva ruta

#app.include_router()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
