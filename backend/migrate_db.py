import json
import os
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Business, Product, Courier, Order, Coupon

# Crear tablas
Base.metadata.create_all(bind=engine)

def migrate_data():
    db = SessionLocal()
    
    print("🚀 Migrando datos a SQLite...")
    
    # 1. Negocios
    if db.query(Business).count() == 0:
        try:
            with open("data/businesses.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    b = Business(
                        id=item["id"],
                        name=item["name"],
                        category=item["category"],
                        address=item["address"],
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        phone=item["phone"],
                        rating=item["rating"],
                        is_open=item.get("is_open", True),
                        delivery_time=item.get("delivery_time", 30)
                    )
                    db.add(b)
                print(f"✅ {len(data)} Negocios migrados.")
        except FileNotFoundError:
            print("⚠️ No se encontró businesses.json")

    # 2. Productos
    product_count = db.query(Product).count()
    print(f"📊 Productos actuales en DB: {product_count}")
    
    if product_count == 0:
        try:
            # Productos locales
            file_path = "data/products.json"
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"📦 Cargando {len(data)} productos desde {file_path}...")
                    for item in data:
                        try:
                            p = Product(
                                business_id=item["business_id"],
                                name=item["name"],
                                price=item["price"],
                                description=item["description"],
                                category=item["category"],
                                available=item.get("available", True),
                                image=item.get("image", ""),
                                source="Local"
                            )
                            db.add(p)
                        except Exception as e:
                            print(f"❌ Error agregando producto {item['name']}: {e}")
                print(f"✅ Productos migrados.")
            else:
                print(f"⚠️ Archivo no encontrado: {file_path}")
            
            # Productos Jumbo
            # ... (rest of Jumbo logic)
        except Exception as e:
            print(f"❌ Error migrando productos: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("ℹ️ Se omitió migración de productos (ya existen datos).")

    # 3. Repartidores
    if db.query(Courier).count() == 0:
        # Crear repartidores por defecto si no hay archivo
        couriers = [
            Courier(name="Juan Pérez", phone="3001234567", lat=6.24, lng=-75.56, zone="Centro", available=True, vehicle="Moto", rating=4.8),
            Courier(name="María Gómez", phone="3109876543", lat=6.25, lng=-75.57, zone="Poblado", available=True, vehicle="Bicicleta", rating=4.9),
            Courier(name="Carlos Ruiz", phone="3201112233", lat=6.23, lng=-75.58, zone="Laureles", available=True, vehicle="Moto", rating=4.7)
        ]
        db.add_all(couriers)
        print(f"✅ {len(couriers)} Repartidores creados por defecto.")

    # 4. Crear Cupones de prueba
    if db.query(Coupon).count() == 0:
        coupons = [
            Coupon(code="BIENVENIDA", discount_percent=20),
            Coupon(code="DELIVERY10", discount_percent=10),
            Coupon(code="FREESHIP", discount_percent=100) # Solo envío (simulado)
        ]
        db.add_all(coupons)
        print("✅ Cupones de prueba creados.")

    db.commit()
    db.close()
    print("✨ Migración completada exitosamente.")

if __name__ == "__main__":
    migrate_data()
