from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Email AI Copilot MVP")
app.include_router(router, prefix="/api")
