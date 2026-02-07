from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    phone = Column(String, nullable=True)
    role = Column(String, default="buyer") # buyer, seller, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    orders = relationship("Order", back_populates="user")
    # Si es vendedor, podría tener un negocio asociado
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=True)
    business = relationship("Business", back_populates="owner")

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String)
    rating = Column(Float, default=5.0)
    is_open = Column(Boolean, default=True)
    delivery_time = Column(Integer)
    
    products = relationship("Product", back_populates="business")
    orders = relationship("Order", back_populates="business")
    owner = relationship("User", back_populates="business", uselist=False)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    category = Column(String)
    available = Column(Boolean, default=True)
    image = Column(String)
    source = Column(String, default="Local") # 'Local' o 'Jumbo'

    business = relationship("Business", back_populates="products")

class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    zone = Column(String)
    available = Column(Boolean, default=True)
    vehicle = Column(String)
    rating = Column(Float, default=5.0)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # Vinculación con usuario registrado (opcional para mantener compatibilidad, pero idealmente requerido)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    customer_name = Column(String)
    customer_email = Column(String, nullable=True) # Para notificaciones
    customer_phone = Column(String)
    customer_address = Column(String)
    customer_lat = Column(Float)
    customer_lng = Column(Float)
    
    business_id = Column(Integer, ForeignKey("businesses.id"))
    business_name = Column(String) # Desnormalizado para facilidad
    business_lat = Column(Float)
    business_lng = Column(Float)
    
    delivery_person_id = Column(Integer, ForeignKey("couriers.id"), nullable=True)
    delivery_person_name = Column(String, nullable=True)
    courier_phone = Column(String, nullable=True) # Agregado campo faltante
    
    products = Column(JSON) # Guardaremos la lista de productos como JSON por simplicidad en MVP
    total = Column(Float)
    distance_km = Column(Float)
    estimated_time = Column(Integer)
    
    payment_method = Column(String)
    payment_status = Column(String, default="pendiente")
    status = Column(String, default="pendiente") # pendiente, preparando, en_camino, entregado
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    status_history = Column(JSON, default=list) # Lista de eventos

    business = relationship("Business", back_populates="orders")
    courier = relationship("Courier")
    user = relationship("User", back_populates="orders")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    business_id = Column(Integer, ForeignKey("businesses.id"))
    rating = Column(Integer) # 1-5
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_percent = Column(Integer)
    active = Column(Boolean, default=True)
