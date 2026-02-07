from app.database import SessionLocal, engine, Base
from app.models import Business, Product, Courier, Order, User
from sqlalchemy import text

def reset_db():
    session = SessionLocal()
    try:
        print("🧹 Limpiando base de datos...")
        # Borrar datos en orden de dependencias
        session.query(Order).delete()
        session.query(Product).delete()
        session.query(Business).delete()
        session.query(Courier).delete()
        session.query(User).delete()
        session.commit()
        print("✅ Base de datos limpia.")
    except Exception as e:
        print(f"❌ Error limpiando DB: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    reset_db()
