from fastapi import FastAPI
import app.models
from app import routes

app = FastAPI()

app.include_router(routes.router)