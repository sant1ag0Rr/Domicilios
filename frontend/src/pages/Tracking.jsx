import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { CheckCircle, Clock, Truck, Home } from 'lucide-react';
import L from 'leaflet';

// Icono personalizado para el repartidor (moto)
const courierIcon = new L.Icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/713/713311.png', // Moto icon
  iconSize: [40, 40],
  iconAnchor: [20, 20],
  popupAnchor: [0, -20]
});

// Icono para el destino (casa)
const homeIcon = new L.Icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/25/25694.png',
  iconSize: [30, 30],
  iconAnchor: [15, 15]
});

const Tracking = () => {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [courierLocation, setCourierLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [eta, setEta] = useState(null);
  const ws = useRef(null);

  // 1. Cargar datos iniciales
  useEffect(() => {
    const fetchOrder = async () => {
      try {
        const response = await axios.get(`/api/delivery/orders/${id}`);
        setOrder(response.data.order);
        setEta(response.data.order.estimated_time);
        
        // Si ya tiene repartidor y ubicación inicial (opcional)
        if (response.data.order.status === 'en_camino') {
            setCourierLocation({
                lat: response.data.order.business_lat, // Inicio
                lng: response.data.order.business_lng
            });
        }
      } catch (error) {
        console.error('Error fetching order:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [id]);

  // 2. Conectar WebSocket
  useEffect(() => {
    if (!order) return;

    // Crear conexión WS
    // Nota: En producción usar wss://
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Asumimos que el backend está en el mismo host pero puerto 8000, o usar proxy
    // Vite proxy reenvía /ws, pero para WS directo a veces es mejor full URL
    const wsUrl = `ws://localhost:8000/ws/orders/${id}`;
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('🟢 WS Conectado');
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📩 Mensaje WS:', data);

      if (data.type === 'status_update') {
        setOrder(prev => ({ ...prev, status: data.status }));
      } else if (data.type === 'location_update') {
        setCourierLocation({ lat: data.lat, lng: data.lng });
        if (data.eta_minutes) setEta(data.eta_minutes);
      }
    };

    ws.current.onclose = () => console.log('🔴 WS Desconectado');

    return () => {
      if (ws.current) ws.current.close();
    };
  }, [id, order?.id]); // Reconectar si cambia el ID (aunque id de URL es estable)

  if (loading) return <div className="container loading-state">Cargando tracking...</div>;
  if (!order) return (
    <div className="container error-state" style={{textAlign: 'center', marginTop: '4rem'}}>
        <h2>Pedido no encontrado 😕</h2>
        <p>Parece que este pedido no existe o fue eliminado.</p>
        <button onClick={() => window.location.href = '/stores'} className="btn btn-primary" style={{marginTop: '1rem'}}>
            Ir a Tiendas
        </button>
    </div>
  );

  const steps = [
    { status: 'pendiente', label: 'Confirmado', icon: CheckCircle },
    { status: 'preparando', label: 'Preparando', icon: Clock },
    { status: 'en_camino', label: 'En Camino', icon: Truck },
    { status: 'entregado', label: 'Entregado', icon: Home },
  ];

  const currentStepIndex = steps.findIndex(s => s.status === order.status);

  // Coordenadas seguras
  const businessPos = [
    parseFloat(order.business_lat) || 6.2442, 
    parseFloat(order.business_lng) || -75.5812
  ];
  const customerPos = [
    parseFloat(order.customer_lat) || 6.2442, 
    parseFloat(order.customer_lng) || -75.5812
  ];

  return (
    <div className="tracking-page container">
      <div className="tracking-header">
        <h2>📍 Seguimiento de Pedido #{order.id}</h2>
        <p className="eta">Tiempo estimado: {eta} min</p>
      </div>

      {/* Progress Bar */}
      <div className="tracking-progress">
        {steps.map((step, index) => {
          const Icon = step.icon;
          const isActive = index <= currentStepIndex;
          return (
            <div key={step.status} className={`step ${isActive ? 'active' : ''}`}>
              <div className="step-icon">
                <Icon size={20} />
              </div>
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>

      <div className="tracking-content">
        {/* Mapa */}
        <div className="tracking-map">
          <MapContainer 
            center={customerPos} // Centrar en el cliente
            zoom={14} 
            style={{ height: '400px', width: '100%', borderRadius: '12px', zIndex: 0 }}
            scrollWheelZoom={false}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            
            {/* Ruta */}
            <Polyline positions={[businessPos, customerPos]} color="#FF5722" weight={4} dashArray="10, 10" opacity={0.6} />

            {/* Negocio */}
            <Marker position={businessPos}>
              <Popup>
                <b>{order.business_name}</b><br/>
                Restaurante
              </Popup>
            </Marker>

            {/* Cliente */}
            <Marker position={customerPos} icon={homeIcon}>
              <Popup>Tu Ubicación</Popup>
            </Marker>

            {/* Repartidor (Dinámico) */}
            {order.status === 'en_camino' && courierLocation && (
              <Marker position={[parseFloat(courierLocation.lat), parseFloat(courierLocation.lng)]} icon={courierIcon}>
                <Popup>Repartidor: {order.delivery_person_name}</Popup>
              </Marker>
            )}
          </MapContainer>
        </div>

        {/* Info Repartidor */}
        {order.status === 'en_camino' && (
            <div className="courier-info-card">
                <div className="courier-avatar">🛵</div>
                <div>
                    <h4>{order.delivery_person_name}</h4>
                    <p>Repartidor Asignado</p>
                    <a href={`tel:${order.courier_phone}`} className="btn-call">Llamar</a>
                </div>
            </div>
        )}
      </div>
    </div>
  );
};

export default Tracking;
