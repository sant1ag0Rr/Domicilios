import uvicorn
import os
import sys

# Script de arranque unificado
# Este script asegura que el backend se ejecute correctamente con la nueva arquitectura

if __name__ == "__main__":
    print("🚀 Iniciando sistema Delivery (Backend + Frontend)...")
    print("📂 Arquitectura: Separada (backend/ vs frontend/)")
    print("🌐 URL: http://127.0.0.1:8000")

    # Configurar paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")

    # Agregar backend al sys.path del proceso actual
    sys.path.append(backend_dir)

    # Agregar backend al PYTHONPATH para que el reloader de Uvicorn lo vea
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{backend_dir}{os.pathsep}{current_pythonpath}"
    
    # Ejecutar Uvicorn
    # Ahora podemos llamar a 'app.main:app' directamente porque 'backend/' está en el path
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido.")
