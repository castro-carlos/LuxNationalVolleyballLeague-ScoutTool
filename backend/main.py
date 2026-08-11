from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.teams import router as teams_router
from api.players import router as players_router
from setup_db import initialize_database
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs automatically EVERY time the backend container starts up
    print("--- [STARTUP] Running database table setup ---")
    await initialize_database()
    print("--- [STARTUP] Database setup complete ---")
    yield

app = FastAPI(
    title="Volleyball Analytics Backend",
    lifespan=lifespan
)

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://castro-carlos.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams_router)
app.include_router(players_router)

@app.get("/")
def home():
    return {"status": "Online"}

