#Importaciones
from fastapi import FastAPI, status, HTTPException
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

@app.get("/v1/ParametroOb/{id}", tags=['Parametro obligatorio'])
async def consultauno(id:int):
    return {"mesaje": "Usuario encontrado",
            "usuario": id,
            "status": "200"}
 
@app.get("/v1/ParametroOp/", tags=['Parametro opcional'])
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
 
@app.get("/v1/usuarios/", tags=['CRUD HTTP'])
async def consultaT():
    return{
        "status":"200",
        "total": len(usuarios),
        "Usuarios":usuarios
    }

@app.post("/v1/usuarios/", tags=['CRUD HTTP'])
async def agregar_usuario(usuario:dict):
    for usr in usuarios:
        if usr["id"] == usuario.get("id"):
            raise HTTPException(
                status_code= 400,
                detail="El id ya existe"
                )
    usuarios.append(usuario)
    return{
        "Mensaje":"Usuario agregado",
        "usuario": usuario,
        "status":"200"
    }

@app.put("/v1/usuarios/", tags=['CRUD HTTP'])
async def modificar_usuario(usuario:dict):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario.get("id"):
            usuarios[i] = usuario
            return{
                "Mensaje":"Usuario modificado",
                "usuario": usuario,
                "status":"200"
            }
    raise HTTPException(
        status_code= 404,
        detail="El id no existe"
        )

@app.delete("/v1/usuarios/{id}", tags=['CRUD HTTP'])
async def eliminar_usuario(id:int):
    global usuarios
    usuarios = [usr for usr in usuarios if usr["id"] != id]
    return{
        "Mensaje":"Usuario eliminado",
        "status":"200"
    }