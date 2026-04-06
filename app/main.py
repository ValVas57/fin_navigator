from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import auth, profile, goals, chat, upload

init_db()

app = FastAPI(title="ФинНавигатор API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(goals.router)
app.include_router(chat.router)
app.include_router(upload.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "ФинНавигатор работает!"}