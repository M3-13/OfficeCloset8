import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PROTECTED_LINKS = [
  { to: '/wardrobe', label: 'Garderobe' },
  { to: '/outfit-creator', label: 'Outfit-Creator' },
  { to: '/saved-outfits', label: 'Gespeicherte Outfits' },
  { to: '/account', label: 'Konto' },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    setMenuOpen(false);
    navigate('/login');
  }

  const navLinks = user
    ? PROTECTED_LINKS
    : [
        { to: '/login', label: 'Login' },
        { to: '/register', label: 'Registrierung' },
      ];

  return (
    <>
      <nav className="navbar">
        <div className="navbar-inner">
          <div className="navbar-brand">OfficeCloset8</div>
          <button
            className="hamburger"
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label="Menü öffnen"
          >
            <span className={`hamburger-bar ${menuOpen ? 'open' : ''}`} />
            <span className={`hamburger-bar ${menuOpen ? 'open' : ''}`} />
            <span className={`hamburger-bar ${menuOpen ? 'open' : ''}`} />
          </button>
          <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </NavLink>
            ))}
            {user && (
              <>
                <span className="navbar-email">{user.email}</span>
                <button className="nav-link nav-link-btn" onClick={handleLogout}>
                  Abmelden
                </button>
              </>
            )}
          </div>
        </div>
      </nav>
      <main className="main-content">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </>
  );
}
