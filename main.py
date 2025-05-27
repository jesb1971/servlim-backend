from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta del archivo Excel
EXCEL_FILE = "TareasLimpieza_ConTabla.xlsx"

class TareaBase(BaseModel):
    fecha: str
    centro: str
    habitaculo: str
    responsable: str
    estado: str
    comentarios: Optional[str] = ""

class Tarea(TareaBase):
    id: int

@app.get("/tareas")
def listar_tareas():
    if not os.path.exists(EXCEL_FILE):
        return []
    df = pd.read_excel(EXCEL_FILE)
    df = df.fillna("")
    return df.to_dict(orient="records")

@app.post("/tareas")
def crear_tarea(tarea: TareaBase):
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
    else:
        df = pd.DataFrame(columns=["id", "fecha", "centro", "habitaculo", "responsable", "estado", "comentarios"])

    nuevo_id = df["id"].max() + 1 if not df.empty else 1
    nueva_fila = {
        "id": nuevo_id,
        "fecha": tarea.fecha,
        "centro": tarea.centro,
        "habitaculo": tarea.habitaculo,
        "responsable": tarea.responsable,
        "estado": tarea.estado,
        "comentarios": tarea.comentarios
    }
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    return {"mensaje": "Tarea creada", "id": nuevo_id}

# Servir archivos estáticos HTML
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/admin", response_class=HTMLResponse)
def cargar_admin():
    return FileResponse("static/panel_administrador.html")

@app.get("/operario", response_class=HTMLResponse)
def cargar_operario():
    return FileResponse("static/panel_operario.html")
@app.get("/informes", response_class=HTMLResponse)
def cargar_informes():
    return FileResponse("static/panel_informes.html")