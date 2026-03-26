import asyncio

from fastapi import status, HTTPException, Depends, APIRouter
from app.data.database import usuarios
from app.models.usuarios import crear_usuario
from app.security.auth import verificar_peticion
from typing import Optional

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.database import usuarios as usuarioDB
from app.data import db

router = APIRouter(
    prefix="/v1/usuarios", tags = ['CRUD HTTP']
)



#Endpoints
@router.get("/", tags=['Inicio'])
async def bienvenida(): 
    return {"mesaje": "Bienvenido a FastAPI"}


@router.get("/", tags=['Asincronia'])
async def Hola():
    await asyncio.sleep(5)#Peticion, consultaBD, Archivo
    return {
        "mesaje": "Hola Mundo",
        "status": "200"
        }

@router.get("/{id}", tags=['Parametro obligatorio'])
async def consultauno(id:int):
    return {"mesaje": "Usuario encontrado",
            "usuario": id,
            "status": "200"}
 
@router.get("/", tags=['Parametro opcional'])
async def consultatodos(id:Optional[int] = None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return {"mesaje": "Usuario encontrado",
                        "usuario": usuarioK,
                        "status": "200"}
        return {"mesaje": "Usuarios no encontrado", "status":"200"  }
    else:
        return {"mesaje": "No se proporciono id", "status":"200"}
 
@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):

    query = db.query(usuarioDB).all()
    return{
        "status": "200",
        "total": len(query),
        "usuarios": query
    }


@router.post("/", tags=['CRUD HTTP'])
async def agregar_usuario(usuarioP:crear_usuario):
    usuarioNuevo = usuarioDB(nombre=usuarioP.nombre, edad=usuarioP.edad)
    db.add(usuarioNuevo)
    db.commit()
    db.refresh(usuarioNuevo)

    return{
        "Mensaje":"Usuario agregado",
        "usuario": usuarioP,
        "status":"200"
    }

@router.put("/", tags=['CRUD HTTP'])
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

@router.delete("/{id}", tags=['CRUD HTTP'])
async def eliminar_usuario(id:int,usuarioauth:str=Depends(verificar_peticion)):
    global usuarios
    usuarios = [usr for usr in usuarios if usr["id"] != id]
    return{
        "Mensaje": f"Usuario eliminado por {usuarioauth}",
        "status":"200"
    }