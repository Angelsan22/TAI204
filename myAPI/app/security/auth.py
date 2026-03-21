#SEguridad con htttp Basic 
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBasicCredentials
import secrets
from fastapi import status, HTTPException, Depends 

#Seguridad con HTTP  BASIC

security= HTTPBasic()

def verificar_peticion(credenciales:HTTPBasicCredentials=Depends(security)):
    usuarioAut= secrets.compare_digest(credenciales.username, "angelsanchez")
    contraAuth= secrets.compare_digest(credenciales.password, "123456")

    if not (usuarioAut and contraAuth):
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no autorizadas",
        )
    
    return credenciales.username