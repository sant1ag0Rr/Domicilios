import asyncio
import math
from app.websockets import manager

class SimulationService:
    def __init__(self):
        self.active_simulations = {}

    async def start_simulation(self, order_id: int, start_lat: float, start_lng: float, end_lat: float, end_lng: float, duration_seconds: int = 60):
        """
        Simula el movimiento de un repartidor desde A hasta B
        """
        if order_id in self.active_simulations:
            return # Ya existe una simulación

        print(f"🚀 Iniciando simulación de entrega para Orden #{order_id}")
        self.active_simulations[order_id] = True
        
        # Ajuste de coordenadas: Usar ubicaciones de Medellín como base
        if start_lat == 0 or end_lat == 0:
            # El Poblado (Parque Lleras)
            start_lat, start_lng = 6.2092, -75.5676
            # Laureles (Segundo Parque)
            end_lat, end_lng = 6.2425, -75.5894

        # Pasos de actualización (cada 2 segundos)
        steps = duration_seconds // 2
        
        lat_step = (end_lat - start_lat) / steps
        lng_step = (end_lng - start_lng) / steps
        
        current_lat = start_lat
        current_lng = start_lng
        
        for i in range(steps):
            if order_id not in self.active_simulations:
                break # Cancelado
                
            # Agregar movimiento más "orgánico" (zig-zag leve)
            noise_lat = (math.sin(i * 0.5) * 0.00005)
            noise_lng = (math.cos(i * 0.5) * 0.00005)
            
            current_lat += lat_step + noise_lat
            current_lng += lng_step + noise_lng
            
            payload = {
                "type": "location_update",
                "lat": current_lat,
                "lng": current_lng,
                "progress": int((i / steps) * 100),
                "eta_minutes": int((steps - i) * 2 / 60) + 1
            }
            
            await manager.broadcast(order_id, payload)
            await asyncio.sleep(2)
            
        # Finalizar
        await manager.broadcast(order_id, {
            "type": "status_update",
            "status": "entregado",
            "message": "¡Tu pedido ha llegado!"
        })
        
        if order_id in self.active_simulations:
            del self.active_simulations[order_id]

    def stop_simulation(self, order_id: int):
        if order_id in self.active_simulations:
            del self.active_simulations[order_id]

simulation_service = SimulationService()
