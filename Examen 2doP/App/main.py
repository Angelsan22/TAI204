from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, time
import secrets

app = FastAPI(
    title="API Turnos Bancarios",
    description="API para gestión de turnos",
    version="1.0"
)

security = HTTPBasic()

turnos = []
contador_id = 1

def verificar_peticion(credentials: HTTPBasicCredentials = Depends(security)):
    usuarioAut = secrets.compare_digest(credentials.username, "banco")
    contrasenaAut = secrets.compare_digest(credentials.password, "2468")

    if not (usuarioAut and contrasenaAut):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return credentials.username

class RegistrarTurno(BaseModel):
    cliente: str = Field(..., min_length=8, max_length=100, example="Juan Perez")
    tipo_tramite: str = Field(..., pattern="^(Deposito|Retiro|Consulta)$")
    fecha_turno: datetime

class Turno(RegistrarTurno):
    id: int
    atendido: bool = False

def validar_turno(turno: RegistrarTurno):
    ahora = datetime.now()
    if turno.fecha_turno <= ahora:
        raise HTTPException(status_code=400, detail="La fecha debe ser futura")
    hora = turno.fecha_turno.time()
    if not (time(9, 0) <= hora <= time(15, 0)):
        raise HTTPException(status_code=400, detail="Horario permitido 09:00 a 15:00")
    turnos_cliente = [
        t for t in turnos
        if t["cliente"] == turno.cliente
        and datetime.fromisoformat(t["fecha_turno"]).date() == turno.fecha_turno.date()]
    if len(turnos_cliente) >= 5:
        raise HTTPException(status_code=400, detail="Máximo 5 turnos por cliente por día")


@app.get("/")
def inicio():
    return {"mensaje": "API Turnos Bancarios"}

@app.post("/v1/turnos", tags=["Turnos"], status_code=201)
def crear_turno(turno: RegistrarTurno):

    global contador_id

    validar_turno(turno)

    nuevo_turno = {
        "id": contador_id,
        "cliente": turno.cliente,
        "tipo_tramite": turno.tipo_tramite,
        "fecha_turno": turno.fecha_turno.isoformat(),
        "atendido": False
    }

    turnos.append(nuevo_turno)
    contador_id += 1

    return {"mensaje": "Turno creado", "turno": nuevo_turno}


@app.get("/v1/turnos", tags=["Turnos"])
def listar_turnos():
    return {
        "total": len(turnos),
        "turnos": turnos
    }


@app.get("/v1/turnos/{id}", tags=["Turnos"])
def consultar_turno(id: int):

    for turno in turnos:
        if turno["id"] == id:
            return turno

    raise HTTPException(status_code=404, detail="Turno no encontrado")

@app.put("/v1/turnos/{id}/atender", tags=["Turnos"])
def marcar_atendido(id: int, usuario: str = Depends(verificar_peticion)):

    for turno in turnos:
        if turno["id"] == id:
            turno["atendido"] = True
            return {"mensaje": "Turno marcado como atendido", "usuario": usuario}

    raise HTTPException(status_code=404, detail="Turno no encontrado")