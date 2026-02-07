import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'buyer'
  });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register(formData);
      navigate('/');
    } catch (err) {
      setError('Error al registrarse. El email podría estar en uso.');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '4rem' }}>
      <div className="feature-card" style={{ textAlign: 'left' }}>
        <h2 style={{ textAlign: 'center', color: 'var(--primary-color)' }}>Crear Cuenta</h2>
        {error && <p style={{ color: 'var(--danger-color)', textAlign: 'center' }}>{error}</p>}
        
        <form onSubmit={handleSubmit} className="checkout-form">
          <div>
            <label>Nombre Completo</label>
            <input 
              type="text" 
              value={formData.full_name} 
              onChange={(e) => setFormData({...formData, full_name: e.target.value})} 
              required 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label>Email</label>
            <input 
              type="email" 
              value={formData.email} 
              onChange={(e) => setFormData({...formData, email: e.target.value})} 
              required 
              style={{ width: '100%' }}
            />
          </div>
          
          <div>
            <label>Contraseña</label>
            <input 
              type="password" 
              value={formData.password} 
              onChange={(e) => setFormData({...formData, password: e.target.value})} 
              required 
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label>Quiero ser:</label>
            <select 
              value={formData.role}
              onChange={(e) => setFormData({...formData, role: e.target.value})}
              style={{ width: '100%', padding: '0.8rem', borderRadius: '6px', background: 'var(--darker-card)', color: 'white', border: '1px solid var(--border-color)' }}
            >
              <option value="buyer">Comprador (Cliente)</option>
              <option value="seller">Vendedor (Negocio)</option>
            </select>
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', border: 'none', padding: '1rem', marginTop: '1rem' }}>
            Registrarse
          </button>
        </form>
        
        <p style={{ marginTop: '1rem', textAlign: 'center' }}>
          ¿Ya tienes cuenta? <Link to="/login" style={{ color: 'var(--primary-color)' }}>Inicia Sesión</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
