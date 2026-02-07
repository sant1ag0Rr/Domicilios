import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MapPin, Search, Star, Clock, Heart, ArrowRight, Utensils, ShoppingCart, Pill, Coffee } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const CategoryCircle = ({ icon: Icon, label, color, onClick }) => (
  <div className="category-circle" onClick={onClick}>
    <div className="circle-icon" style={{ backgroundColor: color }}>
      <Icon size={24} color="white" />
    </div>
    <span>{label}</span>
  </div>
);

const StoreCardMini = ({ business, isFavorite, toggleFavorite }) => (
  <Link to={`/store/${business.id}`} className="store-card-mini">
    <div className="mini-card-img">
        <span className="mini-initial">{business.name.charAt(0)}</span>
        <button 
            className={`btn-fav-mini ${isFavorite ? 'active' : ''}`}
            onClick={(e) => {
                e.preventDefault();
                toggleFavorite(business);
            }}
        >
            <Heart size={14} fill={isFavorite ? "currentColor" : "none"} />
        </button>
    </div>
    <div className="mini-card-info">
      <h4>{business.name}</h4>
      <div className="mini-meta">
        <span className="rating"><Star size={10} fill="currentColor" /> {business.rating}</span>
        <span className="time">{business.delivery_time} min</span>
      </div>
    </div>
  </Link>
);

const Home = () => {
  const navigate = useNavigate();
  const { user, favorites, toggleFavorite } = useAuth();
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinesses();
  }, []);

  const fetchBusinesses = async () => {
    try {
      const response = await axios.get('/api/delivery/businesses');
      setBusinesses(response.data.businesses);
    } catch (error) {
      console.error('Error fetching businesses:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { label: 'Restaurante', icon: Utensils, color: '#FF5722' },
    { label: 'Supermercado', icon: ShoppingCart, color: '#4CAF50' },
    { label: 'Farmacia', icon: Pill, color: '#2196F3' },
    { label: 'Cafetería', icon: Coffee, color: '#795548' },
  ];

  const featuredStores = businesses
    .sort((a, b) => b.rating - a.rating)
    .slice(0, 4);

  return (
    <div className="home-dashboard">
      {/* Search Header */}
      <div className="home-header">
        <div className="location-pill">
          <MapPin size={16} />
          <span>Medellín, Antioquia</span>
        </div>
        <div className="home-search-container" onClick={() => navigate('/stores')}>
            <Search size={18} className="search-icon" />
            <input type="text" placeholder="¿Qué se te antoja hoy?" readOnly />
        </div>
      </div>

      {/* Categories Grid */}
      <div className="section-container">
        <div className="categories-grid">
            {categories.map((cat, idx) => (
                <CategoryCircle 
                    key={idx} 
                    icon={cat.icon} 
                    label={cat.label} 
                    color={cat.color}
                    onClick={() => navigate(`/stores?category=${cat.label}`)}
                />
            ))}
        </div>
      </div>

      {/* Favorites Section */}
      {favorites.length > 0 && (
          <div className="section-container">
            <div className="section-header">
                <h3>Tus Favoritos ❤️</h3>
            </div>
            <div className="horizontal-scroll">
                {favorites.map(biz => (
                    <StoreCardMini 
                        key={biz.id} 
                        business={biz} 
                        isFavorite={true} 
                        toggleFavorite={toggleFavorite} 
                    />
                ))}
            </div>
          </div>
      )}

      {/* Featured Stores */}
      <div className="section-container">
        <div className="section-header">
            <h3>Lo mejor calificado ⭐</h3>
            <Link to="/stores">Ver todo <ArrowRight size={16}/></Link>
        </div>
        
        {loading ? (
            <div className="loading-row">Cargando...</div>
        ) : (
            <div className="horizontal-scroll">
                {featuredStores.map(biz => (
                    <StoreCardMini 
                        key={biz.id} 
                        business={biz} 
                        isFavorite={favorites.some(f => f.id === biz.id)} 
                        toggleFavorite={toggleFavorite} 
                    />
                ))}
            </div>
        )}
      </div>

      {/* Promo Banner */}
      <div className="container promo-banner-section">
        <div className="promo-banner">
            <div className="promo-text">
                <h3>Envío GRATIS</h3>
                <p>En tu primer pedido mayor a $20.000</p>
            </div>
            <div className="promo-img">🛵</div>
        </div>
      </div>
    </div>
  );
};

export default Home;
