# ---------- Importaciones ----------
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional
import asyncio

# ============================================================
# 1. CONFIGURACIÓN OAuth2 / JWT
# ============================================================
SECRET_KEY = "clave-super-secreta-jwt-2026"   # En producción usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1              # Límite máximo: 30 minutos

# Esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================
# 2. BASE DE DATOS FICTICIA DE USUARIOS
# ============================================================
fake_users_db = {
    "angelsanchez": {
        "username": "angelsanchez",
        "hashed_password": pwd_context.hash("123456"),
    }
}

# ============================================================
# 3. MODELOS PYDANTIC
# ============================================================
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, example="Juanito Doe")
    edad: int = Field(..., ge=1, le=125, description="Edad valida entre 1 y 125")

# ============================================================
# 4. FUNCIONES DE AUTENTICACIÓN Y JWT
# ============================================================

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def autenticar_usuario(username: str, password: str):
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verificar_password(password, user["hashed_password"]):
        return False
    return user

def crear_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ============================================================
# 5. DEPENDENCIA – VALIDACIÓN DE TOKEN
# ============================================================

async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(token_data.username)
    if user is None:
        raise credentials_exception
    return user["username"]

# ============================================================
# 6. INSTANCIA DEL SERVIDOR
# ============================================================
app = FastAPI(
    title="Mi Primer API – JWT Edition",
    description="Jose Angel Sanchez Linares",
    version="2.0"
)

# ============================================================
# 7. TABLA FICTICIA DE USUARIOS
# ============================================================
usuarios = [
    {"id": 1, "nombre": "Diego", "edad": 21},
    {"id": 2, "nombre": "Coral", "edad": 21},
    {"id": 3, "nombre": "saul",  "edad": 21}
]

# ============================================================
# 8. ENDPOINT DE LOGIN – GENERA EL TOKEN
# ============================================================

@app.post("/token", response_model=Token, tags=["Autenticacion"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = autenticar_usuario(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = crear_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ============================================================
# 9. ENDPOINTS
# ============================================================

@app.get("/", tags=["Inicio"])
async def bienvenida():
    return {"mensaje": "Bienvenido a FastAPI – JWT Edition"}


@app.get("/holaMundo", tags=["Asincronia"])
async def Hola():
    await asyncio.sleep(5)
    return {"mensaje": "Hola Mundo", "status": "200"}


@app.get("/v1/ParametroOb/{id}", tags=["Parametro obligatorio"])
async def consultauno(id: int):
    return {"mensaje": "Usuario encontrado", "usuario": id, "status": "200"}


@app.get("/v1/ParametroOp/", tags=["Parametro opcional"])
async def consultatodos(id: Optional[int] = None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return {"mensaje": "Usuario encontrado", "usuario": usuarioK, "status": "200"}
        return {"mensaje": "Usuario no encontrado", "status": "200"}
    return {"mensaje": "No se proporcionó id", "status": "200"}


@app.get("/v1/usuarios/", tags=["CRUD HTTP"])
async def consultaT():
    return {"status": "200", "total": len(usuarios), "Usuarios": usuarios}


@app.post("/v1/usuarios/", tags=["CRUD HTTP"])
async def agregar_usuario(usuario: crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
    usuarios.append(usuario.dict())
    return {"Mensaje": "Usuario agregado", "usuario": usuario, "status": "200"}


# ---------- PROTEGIDO CON JWT ----------

@app.put("/v1/usuarios/", tags=["CRUD HTTP"])
async def modificar_usuario(
    usuario: dict,
    usuario_actual: str = Depends(obtener_usuario_actual)   #requiere JWT válido
):
    """Modifica un usuario. Requiere token JWT válido."""
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario.get("id"):
            usuarios[i] = usuario
            return {
                "Mensaje": f"Usuario modificado por {usuario_actual}",
                "usuario": usuario,
                "status": "200"
            }
    raise HTTPException(status_code=404, detail="El id no existe")


@app.delete("/v1/usuarios/{id}", tags=["CRUD HTTP"])
async def eliminar_usuario(
    id: int,
    usuario_actual: str = Depends(obtener_usuario_actual)   #requiere JWT válido
):
    """Elimina un usuario. Requiere token JWT válido."""
    global usuarios
    usuarios = [usr for usr in usuarios if usr["id"] != id]
    return {
        "Mensaje": f"Usuario eliminado por {usuario_actual}",
        "status": "200"
    }