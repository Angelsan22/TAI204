# Importaciones
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date


# Instancia del servidor
app = FastAPI(
    title="Biblioteca Digital API",
    description="Jose Angel Sanchez Linares",
    version="1.0"
)



# TB ficticia - Libros
libros = [
    {"id": 1, "nombre": "Cien años de soledad", "autor": "Gabriel García Márquez", "anio": 1967, "paginas": 417, "estado": "disponible"},
    {"id": 2, "nombre": "El principito", "autor": "Antoine de Saint-Exupéry", "anio": 1943, "paginas": 96, "estado": "disponible"},
    {"id": 3, "nombre": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "anio": 1605, "paginas": 863, "estado": "disponible"},
]



# TB ficticia - Prestamos
prestamos = []

ANO_ACTUAL = date.today().year


# Modelos Pydantic de validación

class RegistrarLibro(BaseModel):
    id: int = Field(..., gt=0, description="Identificador único del libro")
    nombre: str = Field(..., min_length=2, max_length=100, example="El principito")
    autor: str = Field(..., min_length=3, max_length=100, example="Antoine de Saint-Exupéry")
    anio: int = Field(..., gt=1450, le=ANO_ACTUAL, description=f"Año entre 1451 y {ANO_ACTUAL}")
    paginas: int = Field(..., gt=1, description="Número de páginas mayor a 1")
    estado: str = Field(default="disponible", pattern="^(disponible|prestado)$", description="Estado: disponible o prestado")

class RegistrarPrestamo(BaseModel):
    libro_id: int = Field(..., gt=0, description="ID del libro a prestar")
    usuario_nombre: str = Field(..., min_length=3, max_length=100, example="Juan Pérez")
    usuario_correo: EmailStr = Field(..., example="juan@correo.com")




# Endpoints

@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "Bienvenido a la API de Biblioteca Digital"}




#LIBROS

@app.get("/v1/libros/", tags=["Libros"])
async def listar_libros():
    return {
        "status": "200",
        "total": len(libros),
        "libros": libros
    }


@app.get("/v1/libros/buscar/", tags=["Libros"])
async def buscar_libro(nombre: Optional[str] = None):
    if nombre is None:
        return {"mensaje": "No se proporcionó nombre", "status": "200"}

    resultados = [l for l in libros if nombre.lower() in l["nombre"].lower()]

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontró ningún libro con ese nombre")

    return {
        "mensaje": "Libros encontrados",
        "total": len(resultados),
        "libros": resultados,
        "status": "200"
    }


@app.post("/v1/libros/", tags=["Libros"], status_code=201)
async def registrar_libro(libro: RegistrarLibro):
    # Validar nombre no vacío extra
    if not libro.nombre.strip():
        raise HTTPException(status_code=400, detail="El nombre del libro no es válido")

    # Validar duplicado por id
    for l in libros:
        if l["id"] == libro.id:
            raise HTTPException(status_code=400, detail="Ya existe un libro con ese ID")

    libros.append(libro.dict())
    return {
        "mensaje": "Libro registrado exitosamente",
        "libro": libro,
        "status": "201"
    }





#PRESTAMOS

@app.post("/v1/prestamos/", tags=["Préstamos"])
async def registrar_prestamo(prestamo: RegistrarPrestamo):
    # Buscar el libro
    libro_encontrado = None
    for l in libros:
        if l["id"] == prestamo.libro_id:
            libro_encontrado = l
            break

    if libro_encontrado is None:
        raise HTTPException(status_code=404, detail="El libro no existe")

    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(status_code=409, detail="El libro ya está prestado")

    # Registrar préstamo
    nuevo_prestamo = {
        "id": len(prestamos) + 1,
        "libro_id": prestamo.libro_id,
        "libro_nombre": libro_encontrado["nombre"],
        "usuario_nombre": prestamo.usuario_nombre,
        "usuario_correo": prestamo.usuario_correo,
        "fecha_prestamo": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estado": "activo"
    }
    prestamos.append(nuevo_prestamo)

    # Actualizar estado del libro
    libro_encontrado["estado"] = "prestado"

    return {
        "mensaje": "Préstamo registrado exitosamente",
        "prestamo": nuevo_prestamo,
        "status": "200"
    }


@app.put("/v1/prestamos/{prestamo_id}/devolver/", tags=["Préstamos"])
async def devolver_libro(prestamo_id: int):
    # Buscar el préstamo
    prestamo_encontrado = None
    for p in prestamos:
        if p["id"] == prestamo_id:
            prestamo_encontrado = p
            break

    if prestamo_encontrado is None:
        raise HTTPException(status_code=409, detail="El registro de préstamo no existe")

    if prestamo_encontrado["estado"] == "devuelto":
        raise HTTPException(status_code=409, detail="El libro ya fue devuelto anteriormente")

    # Marcar préstamo como devuelto
    prestamo_encontrado["estado"] = "devuelto"
    prestamo_encontrado["fecha_devolucion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Actualizar estado del libro
    for l in libros:
        if l["id"] == prestamo_encontrado["libro_id"]:
            l["estado"] = "disponible"
            break

    return {
        "mensaje": "Libro devuelto exitosamente",
        "prestamo": prestamo_encontrado,
        "status": "200"
    }


@app.delete("/v1/prestamos/{prestamo_id}/", tags=["Préstamos"])
async def eliminar_prestamo(prestamo_id: int):
    global prestamos

    existe = any(p["id"] == prestamo_id for p in prestamos)
    if not existe:
        raise HTTPException(status_code=409, detail="El registro de préstamo ya no existe")

    prestamos = [p for p in prestamos if p["id"] != prestamo_id]

    return {
        "mensaje": "Registro de préstamo eliminado",
        "status": "200"
    }