from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from database import inicializar_db
inicializar_db()

from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path
import sqlite3

from database import crear_conexion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")


class TareaBase(BaseModel):
    fecha: str
    centro: str
    habitaculo: str
    responsable: str
    estado: str
    comentarios: Optional[str] = ""

class Tarea(TareaBase):
    id: int


@app.get("/admin", response_class=HTMLResponse)
def admin():
    html_path = Path("static/panel_administrador.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="Archivo HTML no encontrado")

@app.get("/operario", response_class=HTMLResponse)
def operario():
    html_path = Path("static/panel_operario.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="Archivo HTML no encontrado")

@app.get("/informes_panel", response_class=HTMLResponse)
def informes_panel():
    html_path = Path("static/panel_informes.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    raise HTTPException(status_code=404, detail="Archivo HTML no encontrado")


@app.get("/tareas")
def listar_tareas():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas")
    columnas = [col[0] for col in cursor.description]
    tareas = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return tareas


@app.post("/tareas")
def crear_tarea(tarea: TareaBase):
    try:
        fecha_tarea = datetime.strptime(tarea.fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa AAAA-MM-DD.")
    if fecha_tarea < datetime.now().date():
        raise HTTPException(status_code=400, detail="No se puede crear una tarea con fecha anterior a hoy.")

    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tareas (fecha, centro, habitaculo, responsable, estado, comentarios)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (tarea.fecha, tarea.centro, tarea.habitaculo, tarea.responsable, tarea.estado, tarea.comentarios or "")
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    return {"mensaje": "Tarea creada correctamente", "id": nuevo_id}


@app.put("/tareas/{id}")
def actualizar_tarea(id: int, tarea: Tarea):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tareas WHERE id = ?", (id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    cursor.execute("""
        UPDATE tareas
        SET fecha = ?, centro = ?, habitaculo = ?, responsable = ?, estado = ?, comentarios = ?
        WHERE id = ?""",
        (tarea.fecha, tarea.centro, tarea.habitaculo, tarea.responsable, tarea.estado, tarea.comentarios, id)
    )
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea actualizada correctamente"}


@app.delete("/tareas/{id}")
def eliminar_tarea(id: int):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea eliminada correctamente"}


# Diccionario con claves de acceso para operarios
CLAVES_OPERARIOS = {
    "Candelaria": "43616041",
    "Natalia": "54041797",
    "Soledad": "45455315"
}

class Credenciales(BaseModel):
    nombre: str
    clave: str

@app.post("/login_operario")
def login_operario(credenciales: Credenciales):
    if credenciales.nombre not in CLAVES_OPERARIOS or CLAVES_OPERARIOS[credenciales.nombre] != credenciales.clave:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    hoy = datetime.now().strftime("%Y-%m-%d")
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tareas
        WHERE responsable = ? AND fecha = ?""", (credenciales.nombre, hoy))
    columnas = [col[0] for col in cursor.description]
    tareas = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    conn.close()
    return tareas
