#Importaciones
from fastapi import FastAPI
import asyncio
from typing import Optional

#Instancia del servidor
app = FastAPI(
    title="Mi Primer API",
    description="Jose Angel Sanchez Linares",
    version="1.0"
)

#TB ficticia
usuarios = [
    {"id": 1, "nombre": "Diego","edad": 21},
    {"id": 2, "nombre": "Coral","edad": 21},
    {"id": 3, "nombre": "saul","edad": 21}
]
   
#Endpoints
@app.get("/", tags=['Inicio'])
async def bienvenida():
    return {"mesaje": "Bienvenido a FastAPI"}


@app.get("/holaMundo", tags=['Asincronia'])
async def Hola():
    await asyncio.sleep(5)#Peticion, consultaBD, Archivo
    return {
        "mesaje": "Hola Mundo",
        "status": "200"
        }

@app.get("/v1/usuario/{id}", tags=['Parametro obligatorio'])
async def consultauno(id:int):
    return {"mesaje": "Usuario encontrado",
            "usuario": id,
            "status": "200"}
 
@app.get("/v1/usuarios/", tags=['Parametro opcional'])
async def consultatodos(id:Optional[int] = None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return {"mesaje": "Usuario encontrado",
                        "usuario": usuarioK,
                        "status": "200"}
        return {"mesaje": "Usuarios no encontrado", "status":"200"}
    else:
        return {"mesaje": "No se proporciono id", "status":"200"}
 