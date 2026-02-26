# Importaciones
from fastapi import FastAPI
import asyncio

# Instancia del servidor
app = FastAPI(
    title="Mi Primer API",
    description="Jose Angel Sanchez Linares",
    version="1.0"
)

# Endpoints
@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "Bienvenido a FastAPI"}


@app.get("/holaMundo", tags=["Asincronia"])
async def hola():
    await asyncio.sleep(5)
    return {
        "mensaje": "Hola Mundo",
        "status": "200"
    }