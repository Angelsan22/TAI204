import asyncio
from typing import Optional
from app.data.database import usuarios
from fastapi import APIRouter

routerV = APIRouter(prefix="/Inicio")

#endpoints
@routerV.get("/")
async def bienvenido():
    return {"mensaje": "Bienvenido a FastAPI"}


@routerV.get("/")
async def Hola():
    await asyncio.sleep(5)  # simulación de espera
    return {
        "mensaje": "Hola mundo",
        "status": 200
    }