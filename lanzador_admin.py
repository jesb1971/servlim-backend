import os
import subprocess
import webbrowser
import sys

# Ruta base (directorio donde se encuentra el ejecutable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")

print("Ruta base detectada:", BASE_DIR)
print("Buscando entorno virtual en:", VENV_DIR)

# Verificar si el entorno virtual existe
if not os.path.isdir(VENV_DIR):
    print("❌ ERROR: No se encontró el entorno virtual.")
    print("Por favor, crea el entorno con: python -m venv venv")
    print("Luego instala las dependencias necesarias.")
    input("Pulsa Enter para salir...")
    sys.exit(1)

# Rutas a los ejecutables dentro del venv
python_path = os.path.join(VENV_DIR, "Scripts", "python.exe")

# Ejecutar el servidor con uvicorn
print("✅ Entorno encontrado. Iniciando servidor...")
subprocess.Popen([python_path, "-m", "uvicorn", "api_tareas_limpieza:app", "--reload"], cwd=BASE_DIR)

# Abrir el panel del administrador en el navegador
webbrowser.open(os.path.join(BASE_DIR, "panel_administrador.html"))
