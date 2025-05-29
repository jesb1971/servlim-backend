import sqlite3

DB_NAME = "tareas_limpieza.db"

def crear_conexion():
    conn = sqlite3.connect(DB_NAME)
    return conn

def crear_tabla():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            centro TEXT NOT NULL,
            habitaculo TEXT NOT NULL,
            responsable TEXT NOT NULL,
            estado TEXT NOT NULL,
            comentarios TEXT
        )
    """)
    conn.commit()
    conn.close()

# Crear la tabla automáticamente al importar este módulo
crear_tabla()
