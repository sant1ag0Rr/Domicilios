import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      // Redirigir según el rol del usuario (esto se puede mejorar en el context)
      // Por ahora vamos al home, y el Navbar mostrará los enlaces correctos
      navigate('/stores');
    } catch (err) {
      setError('Credenciales inválidas. Inténtalo de nuevo.');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '4rem' }}>
      <div className="feature-card" style={{ textAlign: 'left' }}>
        <h2 style={{ textAlign: 'center', color: 'var(--primary-color)' }}>Iniciar Sesión</h2>
        {error && <p style={{ color: 'var(--danger-color)', textAlign: 'center' }}>{error}</p>}
        
        <form onSubmit={handleSubmit} className="checkout-form">
          <div>
            <label>Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
              style={{ width: '100%' }}
            />
          </div>
          
          <div>
            <label>Contraseña</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              required 
              style={{ width: '100%' }}
            />
          </div>

          <button type="submit" className="btn-primary" style={{ width: '100%', border: 'none', padding: '1rem', marginTop: '1rem' }}>
            Entrar
          </button>
        </form>
        
        <p style={{ marginTop: '1rem', textAlign: 'center' }}>
          ¿No tienes cuenta? <Link to="/register" style={{ color: 'var(--primary-color)' }}>Regístrate</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
