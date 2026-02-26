from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import search, listings, garages, search_advanced

app = FastAPI(title="Car Prompt API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(search_advanced.router, prefix="/api/search", tags=["search"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(garages.router, prefix="/api/garages", tags=["garages"])


@app.get("/")
async def root():
    return {"message": "Car Prompt API", "version": "0.2.0"}
