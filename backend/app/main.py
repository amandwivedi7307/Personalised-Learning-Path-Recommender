from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from . import auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hackathon ke liye theek, production me restrict karna
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)