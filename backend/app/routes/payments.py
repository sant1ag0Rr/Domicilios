"""
Rutas para el módulo de pagos
Sistema de pago simulado (efectivo y tarjeta)
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.utils import load_json, save_json, get_current_timestamp

router = APIRouter()


@router.post("/process")
async def process_payment(payment_data: dict):
    """
    Procesa un pago simulado
    {
        "order_id": 1,
        "payment_method": "efectivo" | "tarjeta",
        "card_number": "1234 5678 9012 3456" (solo si es tarjeta),
        "card_holder": "Juan Pérez" (solo si es tarjeta),
        "cvv": "123" (solo si es tarjeta)
    }
    """
    orders = load_json("orders.json")
    order = next((o for o in orders if o["id"] == payment_data["order_id"]), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order["payment_status"] == "pagado":
        raise HTTPException(status_code=400, detail="El pedido ya está pagado")
    
    payment_method = payment_data.get("payment_method", "efectivo")
    
    # Validar método de pago
    valid_payment_methods = ["efectivo", "tarjeta"]
    if payment_method not in valid_payment_methods:
        raise HTTPException(
            status_code=400, 
            detail=f"Método de pago inválido. Válidos: {', '.join(valid_payment_methods)}"
        )
    
    # Simular procesamiento de pago
    if payment_method == "tarjeta":
        # Validación básica simulada de datos de tarjeta
        card_number = payment_data.get("card_number", "").replace(" ", "").replace("-", "")
        
        if not card_number or len(card_number) < 13 or len(card_number) > 19:
            raise HTTPException(
                status_code=400, 
                detail="Número de tarjeta inválido. Debe tener entre 13 y 19 dígitos"
            )
        
        # Validar que solo contiene números
        if not card_number.isdigit():
            raise HTTPException(status_code=400, detail="El número de tarjeta solo puede contener dígitos")
        
        if not payment_data.get("card_holder") or len(payment_data["card_holder"].strip()) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Nombre del titular requerido (mínimo 3 caracteres)"
            )
        
        cvv = payment_data.get("cvv", "")
        if not cvv or len(cvv) != 3 or not cvv.isdigit():
            raise HTTPException(status_code=400, detail="CVV inválido. Debe ser un número de 3 dígitos")
        
        # Simular aprobación (en producción aquí iría la pasarela real)
        payment_status = "pagado"
        payment_message = "Pago con tarjeta procesado exitosamente"
    
    else:  # efectivo
        payment_status = "pendiente"  # Efectivo se paga al recibir
        payment_message = "Pago en efectivo registrado. Se cobrará al momento de la entrega."
    
    # Actualizar pedido
    order["payment_method"] = payment_method
    order["payment_status"] = payment_status
    
    # Guardar transacción de pago
    payments = load_json("payments.json")
    payment_record = {
        "id": len(payments) + 1,
        "order_id": order["id"],
        "amount": order["total"],
        "payment_method": payment_method,
        "status": payment_status,
        "created_at": get_current_timestamp()
    }
    payments.append(payment_record)
    save_json("payments.json", payments)
    save_json("orders.json", orders)
    
    return {
        "payment": payment_record,
        "message": payment_message,
        "order": order
    }


@router.get("/history")
async def get_payment_history():
    """Obtiene historial de pagos"""
    payments = load_json("payments.json")
    return {"payments": payments}


@router.get("/orders/{order_id}/payment")
async def get_order_payment(order_id: int):
    """Obtiene información de pago de un pedido"""
    orders = load_json("orders.json")
    order = next((o for o in orders if o["id"] == order_id), None)
    
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    payments = load_json("payments.json")
    payment = next((p for p in payments if p["order_id"] == order_id), None)
    
    return {
        "order_id": order_id,
        "total": order["total"],
        "payment_method": order.get("payment_method", "efectivo"),
        "payment_status": order.get("payment_status", "pendiente"),
        "payment_record": payment
    }
