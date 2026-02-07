# 🚀 CÓMO EJECUTAR LA APLICACIÓN

## Opción 1: Ejecución Manual (Paso a Paso)

### Paso 1: Abrir Terminal
Abre PowerShell o CMD en la carpeta del proyecto:
```powershell
cd c:\Users\victo\Downloads\MASCOTAS
```

### Paso 2: Instalar Dependencias (Solo la primera vez)
```bash
pip install -r requirements.txt
```

### Paso 3: Inicializar Datos
```bash
python init_data.py
```

### Paso 4: Iniciar el Servidor
```bash
python -m uvicorn app.main:app --reload
```

O alternativamente:
```bash
uvicorn app.main:app --reload
```

### Paso 5: Abrir en el Navegador
Abre tu navegador y ve a:
- **http://127.0.0.1:8000** - Página principal
- **http://127.0.0.1:8000/delivery** - Módulo de delivery
- **http://127.0.0.1:8000/dogs** - Módulo de cruce de perros
- **http://127.0.0.1:8000/api/docs** - Documentación API

---

## Opción 2: Script Automático (Windows)

Si tienes el archivo `start.bat`, simplemente haz doble clic o ejecuta:
```bash
start.bat
```

---

## Opción 3: Comandos Rápidos

### Todo en uno (si ya tienes dependencias instaladas):
```bash
python init_data.py && python -m uvicorn app.main:app --reload
```

---

## ⚠️ Solución de Problemas

### Si aparece "uvicorn no se reconoce":
```bash
python -m uvicorn app.main:app --reload
```

### Si hay errores de importación:
Asegúrate de estar en la carpeta raíz del proyecto:
```bash
cd c:\Users\victo\Downloads\MASCOTAS
```

### Si el puerto 8000 está ocupado:
```bash
python -m uvicorn app.main:app --reload --port 8001
```

---

## 📋 Estado Actual

✅ **Servidor corriendo**: http://127.0.0.1:8000
✅ **Datos inicializados**: 15 negocios, 59 productos, 20 perros

---

## 🛑 Detener el Servidor

Presiona `CTRL + C` en la terminal donde está corriendo el servidor.
