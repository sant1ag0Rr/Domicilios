import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package, Clock, CheckCircle, Truck, XCircle } from 'lucide-react';

const SellerDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get('/api/delivery/seller/orders');
      setOrders(response.data.orders);
    } catch (error) {
      console.error('Error fetching seller orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (orderId, newStatus) => {
    try {
      await axios.patch(`/api/delivery/orders/${orderId}/status`, { status: newStatus });
      fetchOrders(); // Recargar lista
    } catch (error) {
      alert('Error actualizando estado');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pendiente: '#FFA500',
      preparando: '#FFD700',
      en_camino: '#1E90FF',
      entregado: '#32CD32',
      cancelado: '#FF4500'
    };
    return (
      <span className="badge" style={{ backgroundColor: colors[status], color: 'black' }}>
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="container">
      <h2 style={{ color: 'var(--primary-color)', marginBottom: '2rem' }}>📊 Panel de Vendedor</h2>
      
      {loading ? <p>Cargando pedidos...</p> : (
        <div className="orders-grid" style={{ display: 'grid', gap: '1.5rem' }}>
          {orders.length === 0 ? <p>No tienes pedidos activos.</p> : orders.map(order => (
            <div key={order.id} className="order-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                <h3>Pedido #{order.id}</h3>
                {getStatusBadge(order.status)}
              </div>
              
              <div>
                <p><strong>Cliente:</strong> {order.customer_name}</p>
                <p><strong>Total:</strong> ${order.total.toLocaleString()}</p>
                <p><strong>Items:</strong> {order.products.length}</p>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                {order.status === 'pendiente' && (
                  <button onClick={() => updateStatus(order.id, 'preparando')} className="btn btn-primary">
                    <Clock size={16} /> Aceptar y Preparar
                  </button>
                )}
                {order.status === 'preparando' && (
                  <button onClick={() => updateStatus(order.id, 'en_camino')} className="btn btn-primary">
                    <Truck size={16} /> Enviar (Repartidor)
                  </button>
                )}
                {order.status === 'en_camino' && (
                  <button onClick={() => updateStatus(order.id, 'entregado')} className="btn" style={{ background: 'var(--success-color)', color: 'black' }}>
                    <CheckCircle size={16} /> Marcar Entregado
                  </button>
                )}
                {order.status !== 'entregado' && order.status !== 'cancelado' && (
                  <button onClick={() => updateStatus(order.id, 'cancelado')} className="btn" style={{ border: '1px solid var(--danger-color)', color: 'var(--danger-color)' }}>
                    <XCircle size={16} /> Cancelar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SellerDashboard;
