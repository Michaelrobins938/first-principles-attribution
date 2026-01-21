from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.router import router

app = FastAPI(
    title="Attribution Matrix API",
    description="Markov-Shapley Hybrid Attribution Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1/attribution")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "attribution-matrix", "version": "2.0.0"}
