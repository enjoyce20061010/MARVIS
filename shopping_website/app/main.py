from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, products, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Website API", description="API for a simple shopping website", version="0.1.0")

app.include_router(products.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Shopping Website API!"}