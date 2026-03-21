#Se queda 
from fastapi import FastAPI
from app.routers import usuarios, varios




#instancia del servidor
#instacioa del servidor 
app = FastAPI(
   title="Mi primer API",
   description="Alberto Adrian Muñiz Lopez",
   version="1.0"
)


app.include_router(usuarios.router)
app.include_router(varios.routerV)