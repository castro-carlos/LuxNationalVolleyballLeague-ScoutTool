from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.teams import router as teams_router

app = FastAPI(title="Volleyball Analytics Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(teams_router)

@app.get("/")
def home():
    return {"status": "Online"}