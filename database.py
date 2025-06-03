import os
import sqlite3

# Usar la ruta del disco persistente de Render
DB_PATH = "/data/tareas_limpieza.db"

def crear_conexion():
    conn = sqlite3.connect(DB_PATH)
    return conn

def inicializar_db():
    if not os.path.exists(DB_PATH):
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                centro TEXT,
                habitaculo TEXT,
                responsable TEXT,
                estado TEXT,
                comentarios TEXT
            )
        ''')
        conn.commit()
        conn.close()
