#Importaciones
from fastapi import FastAPI
import asyncio

#Instancia del servidor
app = FastAPI()

#Endpoints
@app.get("/")
async def bienvenida():
    return {"mesaje": "Bienvenido a FastAPI"}

@app.get("/holaMundo")
async def Hola():
    await asyncio.sleep(5)#Peticion, consultaBD, Archivo
    return {
        "mesaje": "Hola Mundo",
        "status": "200"
        }
    