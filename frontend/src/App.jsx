import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { ShoppingCart, MapPin, Store, Home as HomeIcon, Clock, User, LogOut, BarChart } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Delivery from './pages/Delivery';
import Stores from './pages/Stores';
import Orders from './pages/Orders';
import Tracking from './pages/Tracking';
import Login from './pages/Login';
import Register from './pages/Register';
import SellerDashboard from './pages/SellerDashboard';
import AdminDashboard from './pages/AdminDashboard';

const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="container">
        <Link to="/" className="brand">
          <h1>🚚 Delivery Local</h1>
        </Link>
        <div className="nav-links">
          <Link to="/"><HomeIcon size={18} /> Inicio</Link>
          
          {/* Enlaces comunes */}
          <Link to="/stores"><Store size={18} /> Tiendas</Link>

          {/* Enlaces según rol */}
          {user ? (
            <>
              {user.role === 'buyer' && (
                <Link to="/orders"><Clock size={18} /> Mis Pedidos</Link>
              )}
              {user.role === 'seller' && (
                <Link to="/seller"><Store size={18} /> Gestión Pedidos</Link>
              )}
              {user.role === 'admin' && (
                <Link to="/admin"><BarChart size={18} /> Panel Admin</Link>
              )}
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginLeft: '1rem', borderLeft: '1px solid #333', paddingLeft: '1rem' }}>
                <span style={{ color: 'var(--primary-color)' }}>{user.full_name}</span>
                <button onClick={logout} className="btn-outline" style={{ border: 'none', padding: '0.5rem' }}>
                  <LogOut size={18} />
                </button>
              </div>
            </>
          ) : (
            <Link to="/login" className="btn-primary" style={{ padding: '0.5rem 1rem', textDecoration: 'none' }}>
              <User size={18} /> Ingresar
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <div>Cargando...</div>;
  if (!user) return <Navigate to="/login" />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" />;
  
  return children;
};

import StoreDetails from './pages/StoreDetails';
import Checkout from './pages/Checkout';

// ... (previous imports)

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            <Routes>
              {/* Rutas Públicas */}
              <Route path="/" element={<Home />} />
              <Route path="/delivery" element={<Delivery />} />
              <Route path="/stores" element={<Stores />} />
              <Route path="/store/:id" element={<StoreDetails />} />
              <Route path="/checkout" element={<Checkout />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Rutas Protegidas - Comprador */}
              <Route path="/orders" element={
                <ProtectedRoute allowedRoles={['buyer', 'admin']}>
                  <Orders />
                </ProtectedRoute>
              } />
              <Route path="/tracking/:id" element={
                <ProtectedRoute allowedRoles={['buyer', 'admin']}>
                  <Tracking />
                </ProtectedRoute>
              } />

              {/* ... (rest of routes) */}
              <Route path="/seller" element={
                <ProtectedRoute allowedRoles={['seller', 'admin']}>
                  <SellerDashboard />
                </ProtectedRoute>
              } />

              {/* Rutas Protegidas - Admin */}
              <Route path="/admin" element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
