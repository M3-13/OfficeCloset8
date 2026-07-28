import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';

const NAV_LINKS = [
  { to: '/login', label: 'Login' },
  { to: '/register', label: 'Registrierung' },
  { to: '/wardrobe', label: 'Garderobe' },
  { to: '/outfit-creator', label: 'Outfit-Creator' },
  { to: '/saved-outfits', label: 'Gespeicherte Outfits' },
  { to: '/account', label: 'Konto' },
];

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);

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
            {NAV_LINKS.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
                onClick={() => setMenuOpen(false)}
              >
                {link.label}
              </NavLink>
            ))}
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
