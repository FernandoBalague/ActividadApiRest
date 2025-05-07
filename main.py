from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import os
import uvicorn  # Asegúrate de que esté en tu requirements.txt

app = FastAPI()

usuarios = {
    "admin": {"contrasena": "1234", "rol": "Administrador"},
    "orquestador": {"contrasena": "abcd", "rol": "Orquestador"},
    "usuario": {"contrasena": "xyz", "rol": "Usuario"},
}

servicios = {}
tokens_validos = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autenticar-usuario")

# Modelos
class AutenticacionInput(BaseModel):
    nombre_usuario: str
    contrasena: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ServicioInput(BaseModel):
    nombre: str
    descripcion: str
    endpoints: List[str]

class OrquestarInput(BaseModel):
    servicio_destino: str
    parametros_adicionales: dict

class ReglasOrquestacionInput(BaseModel):
    reglas: dict

class AccesoInput(BaseModel):
    recursos: List[str]
    rol_usuario: str

# Dependencia para obtener usuario autenticado
def get_usuario_actual(token: str = Depends(oauth2_scheme)):
    if token not in tokens_validos:
        raise HTTPException(status_code=401, detail="Token inválido")
    return tokens_validos[token]

# Endpoint 1: Autenticación de Usuario
@app.post("/autenticar-usuario", response_model=TokenResponse)
def autenticar_usuario(auth: AutenticacionInput):
    user = usuarios.get(auth.nombre_usuario)
    if not user or user["contrasena"] != auth.contrasena:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = f"token_{auth.nombre_usuario}"
    tokens_validos[token] = {"usuario": auth.nombre_usuario, "rol": user["rol"]}
    return {"access_token": token}

# Endpoint 2: Obtener Información del Servicio
@app.get("/informacion-servicio/{id}")
def obtener_servicio(id: str, usuario=Depends(get_usuario_actual)):
    if id not in servicios:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicios[id]

# Endpoint 3: Registrar Nuevo Servicio
@app.post("/registrar-servicio")
def registrar_servicio(servicio: ServicioInput, usuario=Depends(get_usuario_actual)):
    if usuario["rol"] != "Administrador":
        raise HTTPException(status_code=403, detail="Permiso denegado")
    servicios[servicio.nombre] = servicio.dict()
    return {"mensaje": "Servicio registrado correctamente"}

# Endpoint 4: Orquestar Servicios
@app.post("/orquestar")
def orquestar_servicios(data: OrquestarInput, usuario=Depends(get_usuario_actual)):
    if usuario["rol"] not in ["Administrador", "Orquestador"]:
        raise HTTPException(status_code=403, detail="Permiso denegado")
    return {
        "mensaje": f"Servicio {data.servicio_destino} orquestado correctamente",
        "parametros": data.parametros_adicionales
    }

# Endpoint 5: Actualizar Reglas de Orquestación
@app.put("/actualizar-reglas-orquestacion")
def actualizar_reglas(data: ReglasOrquestacionInput, usuario=Depends(get_usuario_actual)):
    if usuario["rol"] != "Orquestador":
        raise HTTPException(status_code=403, detail="Permiso denegado")
    return {"mensaje": "Reglas de orquestación actualizadas", "reglas": data.reglas}

# Endpoint 6: Autorización de Acceso
@app.post("/autorizar-acceso")
def autorizar_acceso(data: AccesoInput, usuario=Depends(get_usuario_actual)):
    if usuario["rol"] != data.rol_usuario:
        raise HTTPException(status_code=403, detail="Rol no autorizado para los recursos solicitados")
    return {"mensaje": "Acceso autorizado", "recursos": data.recursos}

# 🚀 Agregado para Railway: correr en el puerto dinámico
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Usa el puerto de Railway o 8000 por defecto
    uvicorn.run("ApiRest:app", host="0.0.0.0", port=port, reload=False)
