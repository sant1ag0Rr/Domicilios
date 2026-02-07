"""
Script rápido para verificar que la aplicación esté lista
"""

import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_structure():
    """Verifica que la estructura de archivos esté completa"""
    print("Verificando estructura del proyecto...\n")
    
    required_files = [
        "app/main.py",
        "app/routes/delivery.py",
        "app/routes/payments.py",
        "app/routes/dogs.py",
        "app/routes/matches.py",
        "templates/index.html",
        "templates/delivery.html",
        "templates/dogs.html",
        "static/style.css",
        "static/delivery.js",
        "static/dogs.js",
        "requirements.txt",
        "init_data.py"
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  [OK] {file}")
        else:
            print(f"  [FALTA] {file}")
            missing.append(file)
    
    # Verificar directorios
    required_dirs = ["data", "app", "templates", "static", "app/routes", "app/scraping"]
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  [OK] directorio: {dir_path}/")
        else:
            print(f"  [FALTA] directorio: {dir_path}/")
            missing.append(dir_path)
    
    if missing:
        print(f"\n[ADVERTENCIA] Faltan {len(missing)} archivos/directorios")
        return False
    else:
        print("\n[OK] Estructura completa")
        return True

def check_data_files():
    """Verifica que los archivos JSON existan"""
    print("\nVerificando archivos de datos...\n")
    
    data_files = [
        "data/businesses.json",
        "data/products.json",
        "data/dogs.json",
        "data/breeds.json",
        "data/orders.json",
        "data/payments.json",
        "data/contacts.json"
    ]
    
    all_exist = True
    for file in data_files:
        if os.path.exists(file):
            # Verificar que no esté vacío (excepto orders, payments, contacts)
            if file in ["data/orders.json", "data/payments.json", "data/contacts.json"]:
                print(f"  [OK] {file} (puede estar vacio)")
            else:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content != "[]":
                        print(f"  [OK] {file} (con datos)")
                    else:
                        print(f"  [VACIO] {file} (ejecuta init_data.py)")
                        all_exist = False
        else:
            print(f"  [FALTA] {file}")
            all_exist = False
    
    return all_exist

def check_imports():
    """Verifica que los imports funcionen"""
    print("\nVerificando imports...\n")
    
    try:
        # Cambiar al directorio raíz
        original_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Intentar importar módulos principales
        sys.path.insert(0, '.')
        
        try:
            from app.routes import delivery, payments, dogs, matches
            print("  [OK] Imports de rutas funcionan")
        except Exception as e:
            print(f"  [ERROR] Error en imports de rutas: {e}")
            return False
        
        try:
            from app.scraping import businesses_scraper, products_scraper, dog_breeds_scraper
            print("  [OK] Imports de scraping funcionan")
        except Exception as e:
            print(f"  [ADVERTENCIA] Error en imports de scraping (puede faltar bs4): {e}")
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"  [ERROR] Error verificando imports: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  VERIFICACION DE LA APLICACION MVP")
    print("=" * 50)
    print()
    
    structure_ok = check_structure()
    data_ok = check_data_files()
    imports_ok = check_imports()
    
    print("\n" + "=" * 50)
    print("  RESUMEN")
    print("=" * 50)
    
    if structure_ok and imports_ok:
        print("\n[OK] La aplicacion esta lista para ejecutarse")
        if not data_ok:
            print("\n[IMPORTANTE] Ejecuta 'python init_data.py' para poblar los datos")
        print("\nPara iniciar el servidor:")
        print("   uvicorn app.main:app --reload")
        print("\n   O usa: python -m app.main")
    else:
        print("\n[ERROR] Hay problemas que deben resolverse antes de ejecutar")
    
    print()
