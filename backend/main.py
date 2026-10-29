from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.teams import router as teams_router
from api.players import router as players_router
from api.graph import router as graph_router


app = FastAPI(title="Volleyball Analytics Backend")

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
app.include_router(graph_router, prefix="/api", tags=["Graph"])

@app.get("/")
def home():
    return {"status": "Online"}

