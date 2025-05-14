from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.download import router as download_router
from app.api.metadata import router as metadata_router
from app.api.history import router as history_router
from app.api.auth import router as auth_router
from app.api.users_admin import router as users_admin_router
from app.api.users_self import router as users_self_router
from app.db.init_db import init_db
import webbrowser

# FastAPI App
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


# Redirect root (/) to /static/index.html
@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url="/static/index.html")

@app.on_event("startup")
async def startup_event():
    #await init_db()
    webbrowser.open("http://localhost:8000/")

# Routers
app.include_router(auth_router)
app.include_router(download_router)
app.include_router(history_router)
app.include_router(metadata_router)
app.include_router(users_admin_router)
app.include_router(users_self_router)