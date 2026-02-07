import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package, Clock, ArrowRight, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Orders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [phone, setPhone] = useState('');
  const [searched, setSearched] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchMyOrders();
    } else {
      setLoading(false);
    }
  }, [user]);

  const fetchMyOrders = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/delivery/orders/mine');
      setOrders(response.data.orders);
      setSearched(true);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrdersByPhone = async () => {
    if (!phone) return;
    setLoading(true);
    try {
      const response = await axios.get(`/api/delivery/orders/user/history?phone=${phone}`);
      setOrders(response.data.orders);
      setSearched(true);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'entregado': return 'var(--success-color)';
      case 'en_camino': return 'var(--primary-color)';
      case 'preparando': return 'var(--warning-color)';
      case 'pendiente': return 'var(--text-muted)';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="orders-page container">
      <div className="orders-header">
        <h2>📜 Mis Pedidos</h2>
        <p>Historial de tus antojos recientes</p>
      </div>

      {!user && (
        <div className="search-box">
            <input
            type="tel"
            placeholder="Buscar por teléfono (invitado)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchOrdersByPhone()}
            />
            <button onClick={fetchOrdersByPhone} className="btn btn-primary">
            <Search size={18} />
            </button>
        </div>
      )}

      <div className="orders-list">
        {loading ? (
          <div className="loading-grid">
             {[1,2,3].map(i => <div key={i} className="skeleton-card" style={{height: '150px'}}></div>)}
          </div>
        ) : orders.length === 0 && searched ? (
          <div className="no-orders" style={{textAlign: 'center', padding: '2rem'}}>
            <Package size={48} color="var(--text-muted)" />
            <p>No tienes pedidos aún.</p>
            <button onClick={() => navigate('/stores')} className="btn btn-primary" style={{marginTop: '1rem'}}>
                Ir a pedir comida
            </button>
          </div>
        ) : (
          orders.map(order => (
            <div key={order.id} className="order-card" style={{marginBottom: '1rem'}}>
              <div className="order-card-header">
                <div>
                  <h3>Pedido #{order.id}</h3>
                  <span className="order-date">
                    {new Date(order.created_at).toLocaleDateString()} • {new Date(order.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </span>
                </div>
                <span 
                  className="order-status badge"
                  style={{ 
                      backgroundColor: getStatusColor(order.status), 
                      color: 'white',
                      padding: '0.3rem 0.8rem',
                      borderRadius: '20px',
                      fontSize: '0.8rem',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                  }}
                >
                  {order.status.replace('_', ' ')}
                </span>
              </div>
              
              <div className="order-details">
                <p><strong>Negocio:</strong> {order.business_name}</p>
                <p><strong>Total:</strong> ${order.total.toLocaleString()}</p>
                <p><strong>Productos:</strong> {order.products.length} items</p>
              </div>

              <div className="order-actions">
                <button 
                  className="btn btn-outline"
                  onClick={() => navigate(`/tracking/${order.id}`)}
                  style={{width: '100%', justifyContent: 'center'}}
                >
                  Ver Estado / Rastrear <ArrowRight size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Orders;
