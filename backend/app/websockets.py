from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps order_id to list of active websockets
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, order_id: int):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)
        print(f"🔌 Cliente conectado a la orden #{order_id}")

    def disconnect(self, websocket: WebSocket, order_id: int):
        if order_id in self.active_connections:
            if websocket in self.active_connections[order_id]:
                self.active_connections[order_id].remove(websocket)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]
        print(f"🔌 Cliente desconectado de la orden #{order_id}")

    async def broadcast(self, order_id: int, message: dict):
        if order_id in self.active_connections:
            for connection in self.active_connections[order_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error enviando mensaje WS: {e}")
                    # Podríamos desconectar aquí si falla repetidamente

manager = ConnectionManager()
