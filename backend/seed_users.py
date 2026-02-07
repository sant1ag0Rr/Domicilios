from app.database import SessionLocal, engine, Base
from app.models import User, Business
from app.auth_utils import get_password_hash

def seed_users():
    # Asegurar que las tablas existan
    print("🛠️  Verificando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    users = [
        {
            "email": "admin@delivery.com",
            "password": "admin123",
            "full_name": "Administrador Principal",
            "role": "admin"
        },
        {
            "email": "vendedor@delivery.com",
            "password": "seller123",
            "full_name": "Vendedor Estrella",
            "role": "seller"
        },
        {
            "email": "cliente@delivery.com",
            "password": "client123",
            "full_name": "Cliente Feliz",
            "role": "buyer"
        }
    ]

    print("🌱 Sembrando usuarios...")

    for user_data in users:
        # Verificar si existe
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"⚠️  Usuario {user_data['email']} ya existe.")
            continue

        hashed_pw = get_password_hash(user_data["password"])
        new_user = User(
            email=user_data["email"],
            hashed_password=hashed_pw,
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Si es vendedor, crearle un negocio
        if user_data["role"] == "seller":
            new_business = Business(
                name=f"Restaurante de {new_user.full_name}",
                category="Comida Rápida",
                address="Av. Siempre Viva 123",
                latitude=6.24,
                longitude=-75.56,
                phone="3001234567",
                owner=new_user
            )
            db.add(new_business)
            db.commit()
            
            # Vincular ID
            new_user.business_id = new_business.id
            db.commit()
            print(f"   🏪 Negocio creado para {user_data['email']}")

        print(f"✅ Usuario creado: {user_data['email']} ({user_data['role']})")

    db.close()
    print("\n✨ ¡Proceso completado!")

if __name__ == "__main__":
    seed_users()
