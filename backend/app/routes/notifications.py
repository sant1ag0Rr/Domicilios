"""
Sistema de notificaciones para pedidos
Simula el envío de notificaciones SMS cuando cambia el estado de un pedido
"""

from fastapi import APIRouter, HTTPException
from app.utils import load_json, save_json
from datetime import datetime

router = APIRouter()


@router.post("/send-sms")
async def send_sms_notification(notification_data: dict):
    """
    Simula el envío de una notificación SMS
    
    En producción, aquí se integraría con un servicio como Twilio, AWS SNS, etc.
    """
    phone = notification_data.get("phone")
    message = notification_data.get("message")
    order_id = notification_data.get("order_id")
    
    if not phone or not message:
        raise HTTPException(status_code=400, detail="Teléfono y mensaje son requeridos")
    
    # Simular envío de SMS
    # En producción, aquí harías:
    # twilio_client.messages.create(
    #     body=message,
    #     from_='+1234567890',
    #     to=phone
    # )
    
    print(f"📱 [SMS SIMULADO] Enviado a {phone}: {message}")
    
    return {
        "success": True,
        "message": "Notificación SMS enviada (simulado)",
        "phone": phone,
        "order_id": order_id,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/notify-order-status/{order_id}")
async def notify_order_status_change(order_id: int):
    """
    Envía notificación cuando cambia el estado de un pedido
    """
    orders = load_json("orders.json")
    order = next((o for o in orders if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    status_messages = {
        "pendiente": f"Tu pedido #{order_id} ha sido recibido y está siendo procesado.",
        "preparando": f"Tu pedido #{order_id} está siendo preparado por {order['business_name']}.",
        "en_camino": f"¡Tu pedido #{order_id} está en camino! Repartidor: {order.get('delivery_person', 'Asignado')}",
        "entregado": f"✅ Tu pedido #{order_id} ha sido entregado exitosamente. ¡Gracias por tu compra!",
        "cancelado": f"Tu pedido #{order_id} ha sido cancelado."
    }
    
    message = status_messages.get(order["status"], f"El estado de tu pedido #{order_id} ha cambiado.")
    
    # Simular envío de SMS
    notification_data = {
        "phone": order["customer_phone"],
        "message": f"🎉 MVP Delivery\n\n{message}\n\nRastrea tu pedido: [URL]/tracking?phone={order['customer_phone']}",
        "order_id": order_id
    }
    
    # En producción, aquí llamarías a send_sms_notification o directamente al servicio SMS
    print(f"📱 [NOTIFICACIÓN] Pedido #{order_id} - Estado: {order['status']}")
    print(f"   Mensaje: {message}")
    print(f"   Teléfono: {order['customer_phone']}")
    
    return {
        "success": True,
        "order_id": order_id,
        "status": order["status"],
        "message": message,
        "notification_sent": True
    }
