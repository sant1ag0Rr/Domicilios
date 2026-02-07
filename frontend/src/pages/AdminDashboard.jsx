import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, Users, ShoppingBag, Store } from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/delivery/admin/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="container">Cargando métricas...</div>;
  if (!stats) return <div className="container">Error al cargar datos</div>;

  return (
    <div className="container">
      <h2 style={{ color: 'var(--primary-color)', marginBottom: '2rem' }}>🛡️ Panel de Administrador</h2>

      <div className="features" style={{ marginBottom: '3rem' }}>
        <div className="feature-card">
          <ShoppingBag size={40} color="#D4AF37" />
          <h3>{stats.total_orders}</h3>
          <p>Pedidos Totales</p>
        </div>
        <div className="feature-card">
          <TrendingUp size={40} color="#D4AF37" />
          <h3>${stats.total_sales.toLocaleString()}</h3>
          <p>Ventas Totales</p>
        </div>
        <div className="feature-card">
          <Users size={40} color="#D4AF37" />
          <h3>{stats.total_users}</h3>
          <p>Usuarios Registrados</p>
        </div>
        <div className="feature-card">
          <Store size={40} color="#D4AF37" />
          <h3>{stats.total_businesses}</h3>
          <p>Negocios Activos</p>
        </div>
      </div>

      <h3 style={{ marginBottom: '1rem' }}>Pedidos Recientes</h3>
      <div className="orders-list">
        {stats.recent_orders.map(order => (
          <div key={order.id} className="order-card">
             <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span><strong>#{order.id}</strong> - {order.customer_name}</span>
                <span>${order.total.toLocaleString()}</span>
                <span>{order.status}</span>
             </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard;
