"""
Rutas para el módulo de repartidores
Sistema de gestión de repartidores simulados
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from app.utils import load_json, save_json, calculate_distance

router = APIRouter()


@router.get("/")
async def get_couriers():
    """
    Obtiene todos los repartidores disponibles
    """
    couriers = load_json("couriers.json")
    return {"couriers": couriers}


@router.get("/available")
async def get_available_couriers():
    """
    Obtiene solo los repartidores disponibles (no ocupados)
    """
    couriers = load_json("couriers.json")
    available = [c for c in couriers if c.get("available", True)]
    return {"couriers": available, "count": len(available)}


@router.get("/{courier_id}")
async def get_courier(courier_id: int):
    """
    Obtiene un repartidor por ID
    """
    couriers = load_json("couriers.json")
    courier = next((c for c in couriers if c["id"] == courier_id), None)
    if not courier:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    return courier


@router.post("/{courier_id}/assign-order/{order_id}")
async def assign_order_to_courier(courier_id: int, order_id: int):
    """
    Asigna un pedido a un repartidor
    
    Args:
        courier_id: ID del repartidor
        order_id: ID del pedido a asignar
    """
    couriers = load_json("couriers.json")
    orders = load_json("orders.json")
    
    # Buscar repartidor
    courier = next((c for c in couriers if c["id"] == courier_id), None)
    if not courier:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    
    if not courier.get("available", True):
        raise HTTPException(status_code=400, detail="El repartidor no está disponible")
    
    # Buscar pedido
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order.get("status") not in ["pendiente", "preparando"]:
        raise HTTPException(
            status_code=400, 
            detail=f"El pedido no puede ser asignado. Estado actual: {order.get('status')}"
        )
    
    # Asignar pedido
    order["courier_id"] = courier_id
    order["courier_name"] = courier["name"]
    order["courier_phone"] = courier["phone"]
    order["status"] = "en_camino"
    
    # Marcar repartidor como ocupado
    courier["available"] = False
    courier["current_order_id"] = order_id
    
    save_json("orders.json", orders)
    save_json("couriers.json", couriers)
    
    return {
        "message": f"Pedido {order_id} asignado a {courier['name']}",
        "order": order,
        "courier": courier
    }


@router.post("/{courier_id}/complete-order/{order_id}")
async def complete_order(courier_id: int, order_id: int):
    """
    Marca un pedido como entregado y libera al repartidor
    """
    couriers = load_json("couriers.json")
    orders = load_json("orders.json")
    
    # Buscar repartidor
    courier = next((c for c in couriers if c["id"] == courier_id), None)
    if not courier:
        raise HTTPException(status_code=404, detail="Repartidor no encontrado")
    
    # Buscar pedido
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order.get("courier_id") != courier_id:
        raise HTTPException(status_code=400, detail="Este pedido no está asignado a este repartidor")
    
    # Marcar pedido como entregado
    order["status"] = "entregado"
    
    # Liberar repartidor
    courier["available"] = True
    courier["current_order_id"] = None
    
    save_json("orders.json", orders)
    save_json("couriers.json", couriers)
    
    return {
        "message": f"Pedido {order_id} marcado como entregado",
        "order": order,
        "courier": courier
    }


@router.get("/nearby/{lat}/{lng}")
async def get_nearby_couriers(lat: float, lng: float, max_distance: float = 5.0):
    """
    Obtiene repartidores cercanos a una ubicación
    
    Args:
        lat: Latitud de la ubicación
        lng: Longitud de la ubicación
        max_distance: Distancia máxima en kilómetros (default: 5.0)
    """
    couriers = load_json("couriers.json")
    available_couriers = [c for c in couriers if c.get("available", True)]
    
    nearby = []
    for courier in available_couriers:
        distance = calculate_distance(lat, lng, courier["lat"], courier["lng"])
        if distance <= max_distance:
            courier_copy = courier.copy()
            courier_copy["distance_km"] = round(distance, 2)
            nearby.append(courier_copy)
    
    # Ordenar por distancia
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "couriers": nearby,
        "count": len(nearby),
        "location": {"lat": lat, "lng": lng},
        "max_distance_km": max_distance
    }
