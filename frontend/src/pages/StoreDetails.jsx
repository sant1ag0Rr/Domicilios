import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Star, Clock, MapPin, Plus, ArrowLeft, ShoppingBag, Heart } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const StoreDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, favorites, toggleFavorite } = useAuth();
  const [business, setBusiness] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Estado local del carrito (podría moverse a un Context global)
  const [cart, setCart] = useState(() => {
    const saved = localStorage.getItem('cart');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    fetchData();
  }, [id]);

  useEffect(() => {
    localStorage.setItem('cart', JSON.stringify(cart));
  }, [cart]);

  const fetchData = async () => {
    try {
      const [bizRes, prodRes] = await Promise.all([
        axios.get(`/api/delivery/businesses/${id}`),
        axios.get(`/api/delivery/businesses/${id}/products`)
      ]);
      setBusiness(bizRes.data);
      setProducts(prodRes.data.products);
    } catch (error) {
      console.error('Error fetching store details:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product) => {
    setCart(prev => {
      // Verificar si hay productos de otro negocio
      if (prev.length > 0 && prev[0].business_id !== business.id) {
        if (!window.confirm('¿Quieres vaciar el carrito para agregar productos de este nuevo negocio?')) {
          return prev;
        }
        return [{ ...product, quantity: 1, business_id: business.id }];
      }

      const existing = prev.find(p => p.id === product.id);
      if (existing) {
        return prev.map(p => p.id === product.id ? { ...p, quantity: p.quantity + 1 } : p);
      }
      return [...prev, { ...product, quantity: 1, business_id: business.id }];
    });
  };

  const cartTotalItems = cart.reduce((acc, item) => acc + item.quantity, 0);
  const cartTotalPrice = cart.reduce((acc, item) => acc + (item.price * item.quantity), 0);

  if (loading) return <div className="container loading">Cargando restaurante...</div>;
  if (!business) return <div className="container error">Negocio no encontrado</div>;

  const isFavorite = favorites.some(b => b.id === business.id);

  return (
    <div className="store-details-page">
      {/* Hero Header */}
      <div className="store-hero">
        <div className="store-hero-overlay"></div>
        <div className="container store-hero-content">
          <div className="store-nav-row" style={{display: 'flex', justifyContent: 'space-between', width: '100%', position: 'absolute', top: '2rem', left: 0, padding: '0 1rem', boxSizing: 'border-box'}}>
            <Link to="/stores" className="back-link-btn" style={{color: 'white', background: 'rgba(0,0,0,0.5)', padding: '0.5rem 1rem', borderRadius: '20px', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', backdropFilter: 'blur(5px)'}}><ArrowLeft size={20} /> Volver</Link>
            <button 
                onClick={() => toggleFavorite(business)}
                style={{
                    background: 'rgba(255,255,255,0.2)', 
                    border: 'none', 
                    borderRadius: '50%', 
                    width: '40px', 
                    height: '40px', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    cursor: 'pointer',
                    backdropFilter: 'blur(5px)',
                    color: isFavorite ? '#ff4444' : 'white'
                }}
            >
                <Heart size={20} fill={isFavorite ? "currentColor" : "none"} />
            </button>
          </div>
          <div className="store-header-info">
            <h1>{business.name}</h1>
            <div className="store-badges">
              <span className="badge-rating"><Star size={16} fill="currentColor" /> {business.rating}</span>
              <span className="badge-time"><Clock size={16} /> {business.delivery_time} min</span>
              <span className="badge-category">{business.category}</span>
            </div>
            <p className="store-address"><MapPin size={16} /> {business.address}</p>
          </div>
        </div>
      </div>

      <div className="container main-content-grid">
        {/* Lista de Productos */}
        <div className="products-section">
          <h2>Menú</h2>
          <div className="products-list">
            {products.map(product => (
              <div key={product.id} className="menu-item-card">
                <div className="menu-item-info">
                  <h3>{product.name}</h3>
                  <p className="description">Delicioso producto fresco y de alta calidad.</p>
                  <p className="price">${product.price.toLocaleString()}</p>
                </div>
                <div className="menu-item-action">
                  <div className="menu-item-image">
                    <img src={product.image} alt={product.name} onError={(e) => e.target.src = 'https://via.placeholder.com/150'} />
                  </div>
                  <button onClick={() => addToCart(product)} className="btn-add-mini">
                    <Plus size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Floating Cart Button (Mobile) or Sidebar (Desktop) */}
        {cart.length > 0 && (
          <div className="floating-cart-bar">
            <div className="cart-summary-text">
              <span className="count-badge">{cartTotalItems}</span>
              <span>Ver pedido</span>
              <span className="total-price">${cartTotalPrice.toLocaleString()}</span>
            </div>
            <button onClick={() => navigate('/checkout')} className="btn-checkout-float">
              Ir a Pagar
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default StoreDetails;
