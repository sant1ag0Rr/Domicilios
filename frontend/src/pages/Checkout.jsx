import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MapPin, CreditCard, Ticket, Trash2, ArrowLeft, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import L from 'leaflet';

// Icono para el pin de ubicación
const pinIcon = new L.Icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/447/447031.png',
  iconSize: [35, 35],
  iconAnchor: [17, 35],
  popupAnchor: [0, -35]
});

// Componente para manejar clics en el mapa y arrastrar marcador
const LocationMarker = ({ position, setPosition }) => {
  const map = useMapEvents({
    click(e) {
      setPosition(e.latlng);
      map.flyTo(e.latlng, map.getZoom());
    },
  });

  return position === null ? null : (
    <Marker 
      position={position} 
      icon={pinIcon}
      draggable={true}
      eventHandlers={{
        dragend: (e) => {
          setPosition(e.target.getLatLng());
        },
      }}
    />
  );
};

const Checkout = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Form State
  const [address, setAddress] = useState('Calle Falsa 123');
  const [phone, setPhone] = useState('3001234567');
  const [location, setLocation] = useState({ lat: 6.2442, lng: -75.5812 }); // Default Medellín
  const [paymentMethod, setPaymentMethod] = useState('efectivo');
  const [coupon, setCoupon] = useState('');
  const [discount, setDiscount] = useState(0);

  useEffect(() => {
    const saved = localStorage.getItem('cart');
    if (saved) setCart(JSON.parse(saved));
  }, []);

  const updateQuantity = (id, delta) => {
    setCart(prev => {
      const updated = prev.map(p => {
        if (p.id === id) return { ...p, quantity: Math.max(1, p.quantity + delta) };
        return p;
      });
      localStorage.setItem('cart', JSON.stringify(updated));
      return updated;
    });
  };

  const removeItem = (id) => {
    setCart(prev => {
      const updated = prev.filter(p => p.id !== id);
      localStorage.setItem('cart', JSON.stringify(updated));
      return updated;
    });
  };

  const subtotal = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);
  const deliveryFee = 3500;
  const total = subtotal + deliveryFee - discount;

  const handlePlaceOrder = async () => {
    if (!user) return alert('Debes iniciar sesión para pedir');
    if (cart.length === 0) return;
    
    setLoading(true);
    try {
      const businessId = cart[0].business_id;
      
      const orderData = {
        customer_name: user.full_name,
        customer_phone: phone,
        customer_address: address,
        customer_lat: 6.2425, // Laureles, Medellín
        customer_lng: -75.5894,
        business_id: businessId,
        products: cart.map(p => ({ product_id: p.id, quantity: p.quantity })),
        payment_method: paymentMethod
      };

      const response = await axios.post('/api/delivery/orders', orderData);
      
      // Limpiar carrito
      localStorage.removeItem('cart');
      setCart([]);
      
      // Simular notificación push
      // En un app real esto lo maneja el service worker
      alert(`📩 Correo enviado a ${user.email} con la confirmación.`);
      
      navigate(`/tracking/${response.data.id}`);
    } catch (error) {
      console.error('Order error:', error);
      if (error.response && error.response.status === 401) {
        alert('Tu sesión ha expirado. Por favor inicia sesión nuevamente.');
        // Opcional: logout()
        navigate('/login');
      } else {
        alert('Error al crear el pedido: ' + (error.response?.data?.detail || error.message));
      }
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="container empty-checkout">
        <h2>Tu carrito está vacío</h2>
        <button onClick={() => navigate('/stores')} className="btn-primary">Volver a Tiendas</button>
      </div>
    );
  }

  return (
    <div className="checkout-page container">
      <div className="checkout-header">
        <button onClick={() => navigate(-1)} className="btn-back"><ArrowLeft /></button>
        <h2>Finalizar Pedido</h2>
      </div>

      <div className="checkout-grid">
        {/* Left Column: Details */}
        <div className="checkout-details">
          {/* Address Section */}
          <section className="checkout-section">
            <h3><MapPin size={20} /> Dirección de Entrega</h3>
            <div className="form-group">
              <input 
                type="text" 
                value={address} 
                onChange={(e) => setAddress(e.target.value)}
                className="input-field"
              />
              <input 
                type="tel" 
                value={phone} 
                onChange={(e) => setPhone(e.target.value)}
                placeholder="Teléfono de contacto"
                className="input-field"
              />
            </div>
            <div className="map-mini-preview">
              {/* Placeholder for map preview */}
              <div className="map-placeholder">📍 Ubicación en mapa</div>
            </div>
          </section>

          {/* Payment Section */}
          <section className="checkout-section">
            <h3><CreditCard size={20} /> Método de Pago</h3>
            <div className="payment-options">
              <label className={`payment-option ${paymentMethod === 'efectivo' ? 'active' : ''}`}>
                <input 
                  type="radio" 
                  name="payment" 
                  value="efectivo" 
                  checked={paymentMethod === 'efectivo'} 
                  onChange={() => setPaymentMethod('efectivo')}
                />
                <span>💵 Efectivo</span>
              </label>
              <label className={`payment-option ${paymentMethod === 'tarjeta' ? 'active' : ''}`}>
                <input 
                  type="radio" 
                  name="payment" 
                  value="tarjeta" 
                  checked={paymentMethod === 'tarjeta'} 
                  onChange={() => setPaymentMethod('tarjeta')}
                />
                <span>💳 Tarjeta</span>
              </label>
            </div>
          </section>

          {/* Items Section */}
          <section className="checkout-section">
            <h3>Resumen de Productos</h3>
            <div className="checkout-items">
              {cart.map(item => (
                <div key={item.id} className="checkout-item">
                  <div className="qty-controls">
                    <button onClick={() => updateQuantity(item.id, -1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, 1)}>+</button>
                  </div>
                  <div className="item-info">
                    <h4>{item.name}</h4>
                    <p>${(item.price * item.quantity).toLocaleString()}</p>
                  </div>
                  <button onClick={() => removeItem(item.id)} className="btn-remove"><Trash2 size={16}/></button>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Right Column: Summary */}
        <div className="checkout-summary">
          <div className="summary-card">
            <h3>Resumen de Pago</h3>
            <div className="summary-row">
              <span>Subtotal</span>
              <span>${subtotal.toLocaleString()}</span>
            </div>
            <div className="summary-row">
              <span>Costo de envío</span>
              <span>${deliveryFee.toLocaleString()}</span>
            </div>
            {discount > 0 && (
              <div className="summary-row discount">
                <span>Descuento</span>
                <span>-${discount.toLocaleString()}</span>
              </div>
            )}
            <div className="divider"></div>
            <div className="summary-row total">
              <span>Total</span>
              <span>${total.toLocaleString()}</span>
            </div>

            <button 
              onClick={handlePlaceOrder} 
              className="btn-place-order" 
              disabled={loading}
            >
              {loading ? 'Procesando...' : 'Hacer Pedido'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
