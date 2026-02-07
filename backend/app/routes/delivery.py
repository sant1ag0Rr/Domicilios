"""
Rutas para el módulo de delivery local
Maneja negocios, productos y pedidos
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Business, Product, Order, Courier, Coupon, Review
from app.utils import calculate_distance, get_current_timestamp, validate_coordinates
from datetime import datetime

router = APIRouter()

@router.get("/businesses")
async def get_businesses(db: Session = Depends(get_db)):
    """Obtiene todos los negocios"""
    businesses = db.query(Business).all()
    return {"businesses": businesses}

@router.get("/businesses/{business_id}")
async def get_business(business_id: int, db: Session = Depends(get_db)):
    """Obtiene un negocio por ID"""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    return business

@router.get("/businesses/{business_id}/products")
async def get_business_products(business_id: int, db: Session = Depends(get_db)):
    """Obtiene productos de un negocio"""
    products = db.query(Product).filter(Product.business_id == business_id, Product.available == True).all()
    return {"products": products}

@router.get("/products")
async def get_all_products(category: str = None, db: Session = Depends(get_db)):
    """Obtiene todos los productos"""
    query = db.query(Product).filter(Product.source == "Local") # Solo productos de negocios reales
    if category:
        # Búsqueda case-insensitive simple
        products = query.all()
        products = [p for p in products if p.category and p.category.lower() == category.lower()]
    else:
        products = query.all()
    
    return {
        "products": products, 
        "count": len(products),
        "category": category
    }

from app.services.email import EmailService
from app.routes.auth import get_current_user
from app.models import User

# ... imports anteriores ...

@router.post("/orders")
async def create_order(
    order_data: dict, 
    background_tasks: BackgroundTasks, # Inyectar BackgroundTasks
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Requiere autenticación
):
    """Crea un nuevo pedido (Autenticado)"""
    # Validar negocio
    business = db.query(Business).filter(Business.id == order_data["business_id"]).first()
    if not business:
        raise HTTPException(status_code=404, detail="Negocio no encontrado")
    
    # Validar productos y calcular total
    total = 0
    order_products = []
    
    for item in order_data["products"]:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            continue
            
        quantity = item.get("quantity", 1)
        subtotal = product.price * quantity
        total += subtotal
        
        order_products.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": quantity,
            "unit_price": product.price,
            "subtotal": subtotal,
            "image": product.image
        })
    
    if not order_products:
        raise HTTPException(status_code=400, detail="El pedido debe contener productos válidos")

    # Calcular distancia
    distance = calculate_distance(
        business.latitude, business.longitude,
        order_data["customer_lat"], order_data["customer_lng"]
    )
    estimated_time = int(business.delivery_time + (distance * 2)) if business.delivery_time else 30
    
    # Crear orden vinculada al usuario
    new_order = Order(
        user_id=current_user.id,
        customer_name=order_data["customer_name"],
        customer_email=current_user.email,
        customer_phone=order_data["customer_phone"],
        customer_address=order_data["customer_address"],
        customer_lat=order_data["customer_lat"],
        customer_lng=order_data["customer_lng"],
        business_id=business.id,
        business_name=business.name,
        business_lat=business.latitude,
        business_lng=business.longitude,
        products=order_products,
        total=total,
        distance_km=round(distance, 2),
        estimated_time=estimated_time,
        payment_method=order_data.get("payment_method", "efectivo"),
        status="pendiente",
        status_history=[{
            "status": "pendiente",
            "timestamp": datetime.now().isoformat()
        }],
        courier_phone=None # Añadimos esto para evitar error si el modelo lo espera
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Enviar email de confirmación
    EmailService.send_order_confirmation(current_user.email, new_order.id, total)
    
    # -------------------------------------------------------------------------
    # AUTOMATIZACIÓN DE DEMOSTRACIÓN
    # Para que el usuario vea cambios en el tracking sin esperar a un "vendedor"
    # -------------------------------------------------------------------------
    async def demo_order_progression(order_id: int):
        import asyncio
        # Esperar 5 segundos y pasar a PREPARANDO
        await asyncio.sleep(5)
        # Necesitamos una nueva sesión de DB porque esto corre en background
        from app.database import SessionLocal
        db_bg = SessionLocal()
        try:
            order = db_bg.query(Order).filter(Order.id == order_id).first()
            if order and order.status == "pendiente":
                order.status = "preparando"
                # Notificar WS
                await manager.broadcast(order_id, {
                    "type": "status_update", 
                    "status": "preparando", 
                    "message": "El restaurante está preparando tu pedido 🍳"
                })
                EmailService.send_status_update(order.customer_email, order.id, "preparando")
                db_bg.commit()
                
                # Esperar 8 segundos más y pasar a EN CAMINO (Inicia simulación)
                await asyncio.sleep(8)
                order = db_bg.query(Order).filter(Order.id == order_id).first()
                if order and order.status == "preparando":
                    order.status = "en_camino"
                    
                    # Asignar repartidor
                    courier = db_bg.query(Courier).filter(Courier.available == True).first()
                    if courier:
                        order.delivery_person_id = courier.id
                        order.delivery_person_name = courier.name
                        order.courier_phone = courier.phone
                    
                    # Notificar WS
                    await manager.broadcast(order_id, {
                        "type": "status_update", 
                        "status": "en_camino", 
                        "message": "¡Tu pedido va en camino! 🛵"
                    })
                    EmailService.send_status_update(order.customer_email, order.id, "en_camino")
                    db_bg.commit()
                    
                    # Iniciar simulación de movimiento
                    await simulation_service.start_simulation(
                        order_id=order.id,
                        start_lat=order.business_lat,
                        start_lng=order.business_lng,
                        end_lat=order.customer_lat,
                        end_lng=order.customer_lng,
                        duration_seconds=60 # Viaje rápido de 1 min para demo
                    )
        except Exception as e:
            print(f"❌ Error en demo automática: {e}")
        finally:
            db_bg.close()

    # Agregar tarea en segundo plano
    background_tasks.add_task(demo_order_progression, new_order.id)

    return {"order": new_order, "message": "Pedido creado exitosamente", "id": new_order.id}

from app.websockets import manager
from app.services.simulation import simulation_service
from fastapi import BackgroundTasks

# ... imports anteriores ...

@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int, 
    status_data: dict, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualiza el estado de un pedido (Solo Vendedores o Admin)"""
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    # Validar permisos: Solo el dueño del negocio o un admin puede cambiar estado
    if current_user.role != "admin":
        # Si es vendedor, verificar que el pedido sea de su negocio
        if current_user.role == "seller":
            if not current_user.business_id or current_user.business_id != order.business_id:
                raise HTTPException(status_code=403, detail="No tienes permiso para gestionar este pedido")
        else:
             raise HTTPException(status_code=403, detail="No tienes permisos de vendedor")

    old_status = order.status
    new_status = status_data.get("status")
    valid_statuses = ["pendiente", "preparando", "en_camino", "entregado", "cancelado"]
    
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Estado inválido. Válidos: {valid_statuses}")
    
    order.status = new_status
    
    # Logica de repartidor (simplificada)
    if new_status == "en_camino" and not order.delivery_person_id:
        courier = db.query(Courier).filter(Courier.available == True).first()
        if courier:
            order.delivery_person_id = courier.id
            order.delivery_person_name = courier.name
            order.courier_phone = courier.phone
            
            # Iniciar simulación de movimiento
            background_tasks.add_task(
                simulation_service.start_simulation,
                order_id=order.id,
                start_lat=order.business_lat,
                start_lng=order.business_lng,
                end_lat=order.customer_lat,
                end_lng=order.customer_lng
            )
    elif new_status == "entregado":
        simulation_service.stop_simulation(order.id)
    
    # Actualizar historial
    if not order.status_history:
        order.status_history = []
    
    history = list(order.status_history)
    history.append({
        "status": new_status,
        "timestamp": datetime.now().isoformat(),
        "updated_by": current_user.email
    })
    order.status_history = history
    order.updated_at = datetime.now()
    
    db.commit()
    
    # Notificar via WebSocket
    await manager.broadcast(order.id, {
        "type": "status_update",
        "status": new_status,
        "message": f"El pedido está {new_status.replace('_', ' ')}"
    })
    
    # Enviar notificación de cambio de estado
    if order.customer_email:
        EmailService.send_status_update(order.customer_email, order.id, new_status)
    
    return {"order": order, "message": f"Estado actualizado de '{old_status}' a '{new_status}'"}

@router.get("/seller/orders")
async def get_seller_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtiene los pedidos del negocio del vendedor actual"""
    if current_user.role != "seller" or not current_user.business_id:
        raise HTTPException(status_code=403, detail="No eres vendedor o no tienes negocio asignado")
        
    orders = db.query(Order).filter(Order.business_id == current_user.business_id).order_by(Order.created_at.desc()).all()
    return {"orders": orders}

@router.get("/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Métricas globales para el admin"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
        
    total_orders = db.query(Order).count()
    total_sales = db.query(func.sum(Order.total)).scalar() or 0
    total_users = db.query(User).count()
    total_businesses = db.query(Business).count()
    
    recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
    
    return {
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_users": total_users,
        "total_businesses": total_businesses,
        "recent_orders": recent_orders
    }

@router.get("/orders/mine")
async def get_my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Obtiene el historial de pedidos del usuario autenticado"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return {"orders": orders}

@router.get("/orders/user/history")
async def get_user_orders(phone: str, db: Session = Depends(get_db)):
    """Historial de pedidos por teléfono (simulación de usuario)"""
    # Normalizar
    clean_phone = phone.replace(" ", "").replace("-", "").replace("+", "")
    # Buscamos coincidencias aproximadas o exactas
    orders = db.query(Order).filter(Order.customer_phone.contains(phone[-7:])).order_by(Order.created_at.desc()).all()
    return {"orders": orders}

@router.post("/reviews")
async def create_review(review_data: dict, db: Session = Depends(get_db)):
    """Crear una reseña para un pedido"""
    order = db.query(Order).filter(Order.id == review_data["order_id"]).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    review = Review(
        order_id=review_data["order_id"],
        business_id=order.business_id,
        rating=review_data["rating"],
        comment=review_data.get("comment", "")
    )
    db.add(review)
    
    # Actualizar rating del negocio (promedio simple)
    business = db.query(Business).filter(Business.id == order.business_id).first()
    reviews = db.query(Review).filter(Review.business_id == order.business_id).all()
    if reviews:
        total_rating = sum([r.rating for r in reviews]) + review_data["rating"]
        business.rating = round(total_rating / (len(reviews) + 1), 1)
    
    db.commit()
    return {"message": "Reseña guardada"}

@router.post("/coupons/validate")
async def validate_coupon(code: str, db: Session = Depends(get_db)):
    """Validar un cupón"""
    coupon = db.query(Coupon).filter(Coupon.code == code, Coupon.active == True).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupón inválido o expirado")
    return {"coupon": coupon}

# Endpoints de carrito (simulados, el estado real está en frontend)
@router.get("/cart")
async def get_cart():
    return {"items": []}
