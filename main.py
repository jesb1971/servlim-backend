from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
from pandas import ExcelWriter

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

ARCHIVO = "TareasLimpieza_ConTabla.xlsx"

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
    df = pd.read_excel(ARCHIVO)
    df = df.fillna("")
    return df.to_dict(orient="records")

@app.post("/tareas")
def crear_tarea(tarea: TareaBase):
    try:
        fecha_tarea = datetime.strptime(tarea.fecha, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa AAAA-MM-DD.")

    if fecha_tarea < datetime.now().date():
        raise HTTPException(status_code=400, detail="No se puede crear una tarea con fecha anterior a hoy.")

    df = pd.read_excel(ARCHIVO)
    df["id"] = df.get("id", pd.Series(dtype=int)).fillna(0).astype(int)
    nuevo_id = int(df["id"].max()) + 1 if not df.empty else 1

    nueva_fila = {
        "id": nuevo_id,
        "fecha": tarea.fecha,
        "centro": tarea.centro,
        "habitaculo": tarea.habitaculo,
        "responsable": tarea.responsable,
        "estado": tarea.estado,
        "comentarios": tarea.comentarios or ""
    }

    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_excel(ARCHIVO, index=False)

    return {"mensaje": "Tarea creada correctamente", "id": int(nuevo_id)}

@app.delete("/tareas/{id}")
def eliminar_tarea(id: int):
    df = pd.read_excel(ARCHIVO)
    df["id"] = df["id"].astype(int)
    if id in df["id"].values:
        df = df[df["id"] != id]
        df.to_excel(ARCHIVO, index=False)
        return {"mensaje": "Tarea eliminada correctamente"}
    else:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.put("/tareas/{id}")
def actualizar_tarea(id: int, tarea: Tarea):
    df = pd.read_excel(ARCHIVO)
    df = df.fillna("")
    df["id"] = df["id"].astype(int)

    if id not in df["id"].values:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    index = df[df["id"] == id].index[0]
    df.at[index, "fecha"] = tarea.fecha
    df.at[index, "centro"] = tarea.centro
    df.at[index, "habitaculo"] = tarea.habitaculo
    df.at[index, "responsable"] = tarea.responsable
    df.at[index, "estado"] = tarea.estado
    df.at[index, "comentarios"] = tarea.comentarios

    df.to_excel(ARCHIVO, index=False)

    return {"mensaje": "Tarea actualizada correctamente"}

# Diccionario con las claves de los operarios
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
    if credenciales.nombre not in CLAVES_OPERARIOS:
        raise HTTPException(status_code=401, detail="Nombre no válido")

    if CLAVES_OPERARIOS[credenciales.nombre] != credenciales.clave:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    df = pd.read_excel(ARCHIVO)
    df = df.fillna("")
    hoy = pd.Timestamp.now().strftime("%Y-%m-%d")

    tareas_hoy = df[
        (df["responsable"] == credenciales.nombre) &
        (df["fecha"] == hoy)
    ]

    return tareas_hoy.to_dict(orient="records")

@app.get("/informes")
def obtener_informes(
    desde: str = Query(...),
    hasta: str = Query(...),
    responsable: Optional[str] = None,
    estado: Optional[str] = None
):
    df = pd.read_excel(ARCHIVO)
    df = df.fillna("")
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    desde_fecha = pd.to_datetime(desde).date()
    hasta_fecha = pd.to_datetime(hasta).date()

    df_filtrado = df[(df["fecha"] >= desde_fecha) & (df["fecha"] <= hasta_fecha)]

    if responsable:
        df_filtrado = df_filtrado[df_filtrado["responsable"] == responsable]
    if estado:
        df_filtrado = df_filtrado[df_filtrado["estado"] == estado]

    return df_filtrado.to_dict(orient="records")

@app.get("/exportar_excel_filtrado")
def exportar_excel(
    desde: str = Query(...),
    hasta: str = Query(...),
    responsable: Optional[str] = None,
    estado: Optional[str] = None
):
    df = pd.read_excel(ARCHIVO)
    df = df.fillna("")
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    desde_fecha = pd.to_datetime(desde).date()
    hasta_fecha = pd.to_datetime(hasta).date()

    df_filtrado = df[(df["fecha"] >= desde_fecha) & (df["fecha"] <= hasta_fecha)]

    if responsable:
        df_filtrado = df_filtrado[df_filtrado["responsable"] == responsable]
    if estado:
        df_filtrado = df_filtrado[df_filtrado["estado"] == estado]

    resumen_general = pd.DataFrame({
        "fecha": [f"Total de tareas encontradas: {len(df_filtrado)}"],
        "centro": [""],
        "habitaculo": [""],
        "responsable": [""],
        "estado": [""],
        "comentarios": [""]
    })

    resumen_resp = df_filtrado.groupby("responsable").size().reset_index(name="total_tareas")
    resumen_resp.insert(0, "resumen", "Por responsable")

    resumen_est = df_filtrado.groupby("estado").size().reset_index(name="total_tareas")
    resumen_est.insert(0, "resumen", "Por estado")

    archivo_export = "Informe_Filtrado.xlsx"
    with ExcelWriter(archivo_export, engine="openpyxl") as writer:
        resumen_general.to_excel(writer, index=False, sheet_name="Informe")
        df_filtrado.to_excel(writer, index=False, sheet_name="Informe", startrow=2)
        resumen_resp.to_excel(writer, index=False, sheet_name="Resumen", startrow=0)
        resumen_est.to_excel(writer, index=False, sheet_name="Resumen", startrow=len(resumen_resp) + 3)

    return FileResponse(
        path=archivo_export,
        filename=archivo_export,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
