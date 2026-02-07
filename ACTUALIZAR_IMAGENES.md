# 📸 Cómo Actualizar las Imágenes de Productos de Jumbo

## ✅ Servidor Ejecutándose

La aplicación está corriendo en: **http://127.0.0.1:8000**

Puedes ver los productos de Jumbo en: **http://127.0.0.1:8000/jumbo**

---

## 🔄 Opción 1: Actualizar Imágenes Interactivamente

Ejecuta el script y sigue las instrucciones:

```bash
python update_jumbo_images.py
```

Luego ingresa las URLs en el formato:
```
1 = https://jumbocolombia.vteximg.com.br/arquivos/ids/123456
```

O por nombre del producto:
```
Nevera Samsung RT38K5932S8 380L = https://jumbocolombia.vteximg.com.br/arquivos/ids/123456
```

---

## 🔄 Opción 2: Actualizar desde un Diccionario Python

Puedes crear un script temporal o usar Python directamente:

```python
from update_jumbo_images import update_from_dict

# Ejemplo: Actualizar productos por ID
imagenes = {
    "1": "https://jumbocolombia.vteximg.com.br/arquivos/ids/123456",
    "2": "https://jumbocolombia.vteximg.com.br/arquivos/ids/123457",
    "3": "https://jumbocolombia.vteximg.com.br/arquivos/ids/123458",
    # ... más URLs
}

update_from_dict(imagenes)
```

---

## 🔄 Opción 3: Editar el JSON Directamente

Puedes editar directamente el archivo `data/jumbo_products.json`:

1. Abre `data/jumbo_products.json`
2. Busca el producto que quieres actualizar
3. Cambia el campo `"image"` con la nueva URL
4. Guarda el archivo
5. El servidor se recargará automáticamente (modo --reload activo)

---

## 📋 Formato de URLs de Jumbo

Las URLs de imágenes de Jumbo suelen tener estos formatos:

- **VTEX CDN**: `https://jumbocolombia.vteximg.com.br/arquivos/ids/XXXXXX`
- **Jumbo Directo**: `https://www.jumbocolombia.com/imagenes/productos/XXXXXX.jpg`
- **Con parámetros**: `https://jumbocolombia.vteximg.com.br/arquivos/ids/XXXXXX?v=1`

---

## 🚀 Ver Cambios en Tiempo Real

El servidor está configurado con `--reload`, así que:

1. ✅ Actualiza las imágenes usando cualquiera de los métodos anteriores
2. ✅ El servidor se recargará automáticamente
3. ✅ Refresca la página en el navegador (F5 o Ctrl+R)
4. ✅ Verás las nuevas imágenes inmediatamente

---

## 📝 Ejemplo Completo

```bash
# 1. Ejecutar el script
python update_jumbo_images.py

# 2. Ingresar URLs (una por línea):
1 = https://jumbocolombia.vteximg.com.br/arquivos/ids/123456
2 = https://jumbocolombia.vteximg.com.br/arquivos/ids/123457
3 = https://jumbocolombia.vteximg.com.br/arquivos/ids/123458
[Presiona ENTER sin texto para terminar]

# 3. Verificar en el navegador:
# http://127.0.0.1:8000/jumbo
```

---

## 🛑 Detener el Servidor

Para detener el servidor, presiona `CTRL + C` en la terminal donde está corriendo.

---

## 💡 Tips

- Puedes actualizar múltiples productos a la vez
- El script busca coincidencias por ID o nombre (parcial)
- Las URLs deben comenzar con `http://` o `https://`
- El servidor se recarga automáticamente cuando cambias el JSON
