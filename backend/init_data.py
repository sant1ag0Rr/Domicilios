"""
Script para inicializar todos los datos del proyecto
Ejecutar este script antes de iniciar el servidor
"""

import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importar módulos de scraping
from app.scraping.businesses_scraper import save_businesses
from app.scraping.products_scraper import save_products
from app.scraping.couriers_scraper import save_couriers
from app.scraping.jumbo_scraper import save_jumbo_products
from app.utils import DATA_DIR, save_json

def init_all_data():
    """Inicializa todos los datos del proyecto"""
    print("Inicializando datos del proyecto...\n")
    
    # Crear directorio data si no existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 1. Scrapear negocios
    print("[1/5] Generando datos de negocios...")
    businesses = save_businesses()
    
    # 2. Scrapear productos locales
    print("\n[2/5] Generando productos locales...")
    products = save_products(businesses)
    
    # 3. Scrapear productos de Jumbo Colombia
    print("\n[3/5] Scrapeando productos de Jumbo Colombia...")
    jumbo_products = save_jumbo_products()
    
    # 4. Generar repartidores
    print("\n[4/5] Generando repartidores...")
    couriers = save_couriers()
    
    # 5. Crear archivos JSON vacíos para órdenes y pagos
    print("\n[5/5] Creando archivos de datos...")
    
    empty_files = {
        "orders.json": [],
        "payments.json": []
    }
    
    for filename, default_data in empty_files.items():
        # Usar save_json de utils para asegurar la ruta correcta
        save_json(filename, default_data)
        print(f"  [OK] Creado {filename}")
    
    print("\n[COMPLETADO] Datos inicializados exitosamente!")
    print("\nResumen:")
    print(f"  - Negocios: {len(businesses)}")
    print(f"  - Productos locales: {len(products)}")
    print(f"  - Productos Jumbo: {len(jumbo_products)}")
    print(f"  - Repartidores: {len(couriers)}")
    print(f"  - Archivos JSON creados en data/")
    print("\nPara iniciar el servidor ejecuta:")
    print("  python -m uvicorn app.main:app --reload")

if __name__ == "__main__":
    init_all_data()
