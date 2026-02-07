import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, MapPin, Star, Clock, Heart } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Stores = () => {
  const [businesses, setBusinesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchParams] = useSearchParams();
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const { favorites, toggleFavorite } = useAuth();

  useEffect(() => {
    const cat = searchParams.get('category');
    if (cat) setSelectedCategory(cat);
  }, [searchParams]);

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

  const categories = [...new Set(businesses.map(b => b.category))];

  const filteredBusinesses = businesses.filter(b => {
    const matchesSearch = b.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          b.category.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory ? b.category === selectedCategory : true;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="container">
      <div className="stores-header">
        <h2>🏪 Tiendas y Restaurantes</h2>
        <p>Explora los mejores negocios de tu zona</p>
      </div>

      <div className="filters-section">
        <div className="search-bar">
          <Search size={20} className="search-icon" />
          <input 
            type="text" 
            placeholder="Buscar restaurantes, farmacias..." 
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="categories-pills">
          <button 
            className={`category-pill ${selectedCategory === '' ? 'active' : ''}`}
            onClick={() => setSelectedCategory('')}
          >
            Todas
          </button>
          {categories.map(cat => (
            <button 
              key={cat} 
              className={`category-pill ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="loading-grid">
          {[1,2,3,4].map(i => <div key={i} className="skeleton-card"></div>)}
        </div>
      ) : (
        <div className="stores-grid">
          {filteredBusinesses.map(business => {
            const isFavorite = favorites.some(f => f.id === business.id);
            return (
            <Link to={`/store/${business.id}`} key={business.id} className="store-card" style={{position: 'relative'}}>
              <div className="store-image-placeholder">
                <span className="store-initial">{business.name.charAt(0)}</span>
                <button 
                    className={`btn-fav-mini ${isFavorite ? 'active' : ''}`}
                    onClick={(e) => {
                        e.preventDefault();
                        toggleFavorite(business);
                    }}
                    style={{top: '10px', right: '10px'}}
                >
                    <Heart size={16} fill={isFavorite ? "currentColor" : "none"} />
                </button>
              </div>
              <div className="store-info">
                <div className="store-header-row">
                    <h3>{business.name}</h3>
                    <span className="rating"><Star size={14} fill="currentColor" /> {business.rating}</span>
                </div>
                <p className="category-text">{business.category}</p>
                
                <div className="store-meta">
                  <span><Clock size={14} /> {business.delivery_time} min</span>
                  <span><MapPin size={14} /> {business.address}</span>
                </div>
                
                <div className="store-status">
                    {business.is_open ? 
                        <span className="status-open">Abierto</span> : 
                        <span className="status-closed">Cerrado</span>
                    }
                </div>
              </div>
            </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Stores;
