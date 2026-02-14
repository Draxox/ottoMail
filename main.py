"""Main FastAPI application"""
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import app as api_app
from app.models import init_db

# Initialize
init_db()
app = FastAPI(title="Email AI Copilot MVP")

app.mount("/api", api_app)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    with open("dashboard.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
