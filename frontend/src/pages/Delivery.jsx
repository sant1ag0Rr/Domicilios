import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Star, Clock, ShoppingBag, Plus, Minus, X, CreditCard, Ticket } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import L from 'leaflet';

// Fix for default marker icon in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const Delivery = () => {
  const [businesses, setBusinesses] = useState([]);
  const [selectedBusiness, setSelectedBusiness] = useState(null);
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [coupon, setCoupon] = useState('');
  const [couponApplied, setCouponApplied] = useState(null);
  const [orderForm, setOrderForm] = useState({
    name: '',
    phone: '',
    address: '',
    paymentMethod: 'efectivo',
    cardNumber: '',
    cardExpiry: '',
    cardCVC: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchBusinesses();
  }, []);

  useEffect(() => {
    if (selectedBusiness) {
      fetchProducts(selectedBusiness.id);
    }
  }, [selectedBusiness]);

  const fetchBusinesses = async () => {
    try {
      const response = await axios.get('/api/delivery/businesses');
      setBusinesses(response.data.businesses);
    } catch (error) {
      console.error('Error loading businesses:', error);
    }
  };

  const fetchProducts = async (businessId) => {
    try {
      const response = await axios.get(`/api/delivery/businesses/${businessId}/products`);
      setProducts(response.data.products);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  };

  const addToCart = (product) => {
    setCart(prev => {
      const existing = prev.find(p => p.id === product.id);
      if (existing) {
        return prev.map(p => p.id === product.id ? { ...p, quantity: p.quantity + 1 } : p);
      }
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  const removeFromCart = (productId) => {
    setCart(prev => prev.filter(p => p.id !== productId));
  };

  const updateQuantity = (productId, delta) => {
    setCart(prev => prev.map(p => {
      if (p.id === productId) {
        return { ...p, quantity: Math.max(1, p.quantity + delta) };
      }
      return p;
    }));
  };

  const validateCoupon = async () => {
    if (!coupon) return;
    try {
      const response = await axios.post(`/api/delivery/coupons/validate?code=${coupon}`);
      setCouponApplied(response.data.coupon);
      alert(`¡Cupón aplicado! Descuento: ${response.data.coupon.discount_percent}%`);
    } catch (error) {
      alert('Cupón inválido o expirado');
      setCouponApplied(null);
    }
  };

  const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const discount = couponApplied ? (subtotal * couponApplied.discount_percent / 100) : 0;
  const total = subtotal - discount;

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    if (cart.length === 0) return alert('El carrito está vacío');
    if (!selectedBusiness) return alert('Debes seleccionar un negocio');

    try {
      const orderData = {
        customer_name: orderForm.name,
        customer_phone: orderForm.phone,
        customer_address: orderForm.address,
        customer_lat: 6.2476, // Hardcoded for MVP
        customer_lng: -75.5658, // Hardcoded for MVP
        business_id: selectedBusiness.id,
        products: cart.map(p => ({ product_id: p.id, quantity: p.quantity })),
        payment_method: orderForm.paymentMethod
      };

      const response = await axios.post('/api/delivery/orders', orderData);
      const orderId = response.data.id;
      
      alert('¡Pedido creado exitosamente!');
      setCart([]);
      setIsCartOpen(false);
      setOrderForm({ name: '', phone: '', address: '', paymentMethod: 'efectivo', cardNumber: '', cardExpiry: '', cardCVC: '' });
      setCouponApplied(null);
      setCoupon('');
      
      // Redirigir al tracking
      navigate(`/tracking/${orderId}`);
      
    } catch (error) {
      console.error('Error creating order:', error);
      alert('Error al crear el pedido');
    }
  };

  return (
    <div className="delivery-page container">
      <div className="content-grid">
        {/* Sidebar: Lista de Negocios */}
        <div className="sidebar">
          <h3>🏪 Negocios Disponibles</h3>
          <div className="business-list">
            {businesses.map(business => (
              <div 
                key={business.id} 
                className={`business-item ${selectedBusiness?.id === business.id ? 'active' : ''}`}
                onClick={() => setSelectedBusiness(business)}
              >
                <h4>{business.name}</h4>
                <p>{business.category}</p>
                <div className="business-meta">
                  <span><Star size={14} fill="#FFD700" color="#FFD700"/> {business.rating}</span>
                  <span><Clock size={14} /> {business.delivery_time} min</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content: Productos y Mapa */}
        <div className="main-content">
          {selectedBusiness ? (
            <div className="business-details">
              <div className="business-header">
                <h2>{selectedBusiness.name}</h2>
                <p>{selectedBusiness.address}</p>
              </div>

              <div className="products-grid">
                {products.map(product => (
                  <div key={product.id} className="product-card-modern">
                    <img src={product.image} alt={product.name} />
                    <div className="product-info">
                      <h4>{product.name}</h4>
                      <p className="price">${product.price.toLocaleString()}</p>
                      <button onClick={() => addToCart(product)} className="btn-add">
                        Agregar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="select-business-prompt">
              <h3>👈 Selecciona un negocio para ver sus productos</h3>
              <div className="map-container-wrapper">
                <MapContainer center={[6.2476, -75.5658]} zoom={13} scrollWheelZoom={false} style={{ height: '400px', width: '100%', borderRadius: '12px' }}>
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  {businesses.map(business => (
                    <Marker 
                      key={business.id} 
                      position={[business.latitude, business.longitude]}
                      eventHandlers={{
                        click: () => setSelectedBusiness(business),
                      }}
                    >
                      <Popup>
                        <b>{business.name}</b><br/>
                        {business.category}
                      </Popup>
                    </Marker>
                  ))}
                </MapContainer>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Cart Sidebar */}
      <div className={`cart-sidebar ${isCartOpen ? 'open' : ''}`}>
        <div className="cart-header">
          <h3>🛒 Tu Pedido</h3>
          <button onClick={() => setIsCartOpen(false)} className="close-btn"><X /></button>
        </div>
        
        <div className="cart-items">
          {cart.length === 0 ? (
            <p className="empty-cart">El carrito está vacío</p>
          ) : (
            cart.map(item => (
              <div key={item.id} className="cart-item">
                <div className="cart-item-info">
                  <h4>{item.name}</h4>
                  <p>${(item.price * item.quantity).toLocaleString()}</p>
                </div>
                <div className="cart-controls">
                  <button onClick={() => updateQuantity(item.id, -1)}><Minus size={14}/></button>
                  <span>{item.quantity}</span>
                  <button onClick={() => updateQuantity(item.id, 1)}><Plus size={14}/></button>
                  <button onClick={() => removeFromCart(item.id)} className="remove-btn"><X size={14}/></button>
                </div>
              </div>
            ))
          )}
        </div>

        {cart.length > 0 && (
          <div className="cart-footer">
            {/* Cupones */}
            <div className="coupon-section">
              <div className="coupon-input-group">
                <Ticket size={18} />
                <input 
                  type="text" 
                  placeholder="Código Cupón" 
                  value={coupon}
                  onChange={(e) => setCoupon(e.target.value)}
                />
                <button type="button" onClick={validateCoupon} className="btn-apply">Aplicar</button>
              </div>
              {couponApplied && <p className="coupon-success">Descuento aplicado: -${discount.toLocaleString()}</p>}
            </div>

            <div className="total">
              <span>Total:</span>
              <span>${total.toLocaleString()}</span>
            </div>
            
            <form onSubmit={handleSubmitOrder} className="checkout-form">
              <input 
                type="text" 
                placeholder="Nombre" 
                value={orderForm.name}
                onChange={e => setOrderForm({...orderForm, name: e.target.value})}
                required 
              />
              <input 
                type="tel" 
                placeholder="Teléfono" 
                value={orderForm.phone}
                onChange={e => setOrderForm({...orderForm, phone: e.target.value})}
                required 
              />
              <input 
                type="text" 
                placeholder="Dirección" 
                value={orderForm.address}
                onChange={e => setOrderForm({...orderForm, address: e.target.value})}
                required 
              />
              
              <div className="payment-method-selector">
                <label>Método de Pago</label>
                <select 
                  value={orderForm.paymentMethod}
                  onChange={e => setOrderForm({...orderForm, paymentMethod: e.target.value})}
                >
                  <option value="efectivo">Efectivo</option>
                  <option value="tarjeta">Tarjeta de Crédito/Débito</option>
                  <option value="nequi">Nequi / Daviplata</option>
                </select>
              </div>

              {/* Simulación de pago con tarjeta */}
              {orderForm.paymentMethod === 'tarjeta' && (
                <div className="card-form">
                  <div className="card-input-group">
                    <CreditCard size={18} />
                    <input 
                      type="text" 
                      placeholder="Número de Tarjeta" 
                      value={orderForm.cardNumber}
                      onChange={e => setOrderForm({...orderForm, cardNumber: e.target.value})}
                    />
                  </div>
                  <div className="card-row">
                    <input 
                      type="text" 
                      placeholder="MM/YY" 
                      value={orderForm.cardExpiry}
                      onChange={e => setOrderForm({...orderForm, cardExpiry: e.target.value})}
                    />
                    <input 
                      type="text" 
                      placeholder="CVC" 
                      value={orderForm.cardCVC}
                      onChange={e => setOrderForm({...orderForm, cardCVC: e.target.value})}
                    />
                  </div>
                </div>
              )}

              <button type="submit" className="btn-checkout">Confirmar Pedido</button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Delivery;
