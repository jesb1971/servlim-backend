from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

from database import crear_conexion, inicializar_db

# Inicializa la base de datos al arrancar
inicializar_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TareaBase(BaseModel):
    fecha: str
    centro: str
    habitaculo: str
    responsable: str
    estado: str
    comentarios: Optional[str] = ""

class Tarea(TareaBase):
    id: int

@app.get("/")
def home():
    return {"status": "ok"}

@app.get("/favicon.ico")
def favicon():
    icon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(icon_path):
        return FileResponse(icon_path)
    else:
        raise HTTPException(status_code=404, detail="Favicon no encontrado")

@app.head("/{full_path:path}")
async def head_handler(full_path: str, request: Request):
    return {}

@app.get("/admin")
def admin_panel():
    return FileResponse("static/panel_administrador.html")

@app.get("/operario")
def operario_panel():
    return FileResponse("static/panel_operario.html")

@app.get("/informes_panel")
def informes_panel():
    return FileResponse("static/panel_informes.html")

@app.get("/tareas")
def listar_tareas():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas")
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(columnas, fila)) for fila in filas]

@app.post("/tareas")
def crear_tarea(tarea: TareaBase):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tareas (fecha, centro, habitaculo, responsable, estado, comentarios)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tarea.fecha, tarea.centro, tarea.habitaculo, tarea.responsable, tarea.estado, tarea.comentarios))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea creada exitosamente"}

@app.put("/tareas/{tarea_id}")
def actualizar_tarea(tarea_id: int, tarea: TareaBase):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tareas SET fecha=?, centro=?, habitaculo=?, responsable=?, estado=?, comentarios=?
        WHERE id=?
    """, (tarea.fecha, tarea.centro, tarea.habitaculo, tarea.responsable, tarea.estado, tarea.comentarios, tarea_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea actualizada"}

@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(tarea_id: int):
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    return {"mensaje": "Tarea eliminada"}

@app.post("/login_operario")
def login_operario(datos: dict):
    nombre = datos.get("nombre")
    clave = datos.get("clave")
    claves_validas = {"Candelaria": "43616041", "Natalia": "54041797", "Soledad": "45455315"}

    if claves_validas.get(nombre) != clave:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    hoy = datetime.now().strftime("%Y-%m-%d")
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas WHERE responsable = ? AND fecha = ?", (nombre, hoy))
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    conn.close()

    return [dict(zip(columnas, fila)) for fila in filas]

@app.get("/informes")
def filtrar_informes(desde: str, hasta: str, responsable: Optional[str] = None, estado: Optional[str] = None):
    conn = crear_conexion()
    cursor = conn.cursor()

    query = "SELECT * FROM tareas WHERE fecha BETWEEN ? AND ?"
    params = [desde, hasta]

    if responsable and responsable != "Todos":
        query += " AND responsable = ?"
        params.append(responsable)

    if estado and estado != "Todos":
        query += " AND estado = ?"
        params.append(estado)

    cursor.execute(query, params)
    filas = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    conn.close()

    return [dict(zip(columnas, fila)) for fila in filas]

@app.get("/exportar_excel_filtrado")
def exportar_excel_filtrado(desde: str, hasta: str, responsable: Optional[str] = None, estado: Optional[str] = None):
    from openpyxl import Workbook

    datos = filtrar_informes(desde, hasta, responsable, estado)

    wb = Workbook()
    ws = wb.active
    ws.title = "Informe Filtrado"

    if datos:
        ws.append(list(datos[0].keys()))
        for fila in datos:
            ws.append(list(fila.values()))

    archivo = "informe_filtrado.xlsx"
    wb.save(archivo)
    return FileResponse(archivo, filename=archivo, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
