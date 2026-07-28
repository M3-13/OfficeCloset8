import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import "./Layout.css";

const NAV_ITEMS = [
  { to: "/wardrobe", label: "Garderobe" },
  { to: "/create", label: "Outfit-Creator" },
  { to: "/outfits", label: "Gespeicherte Outfits" },
  { to: "/account", label: "Konto" },
  { to: "/login", label: "Login" },
  { to: "/register", label: "Registrierung" },
];

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      <nav className="nav">
        <NavLink to="/" className="nav-logo">
          OfficeCloset8
        </NavLink>
        <ul className="nav-links">
          {NAV_ITEMS.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) => (isActive ? "active" : "")}
              >
                {item.label}
              </NavLink>
            </li>
          ))}
        </ul>
        <button
          className={`hamburger${menuOpen ? " open" : ""}`}
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="Menü"
        >
          <span />
          <span />
          <span />
        </button>
      </nav>

      <ul className={`mobile-menu${menuOpen ? " open" : ""}`}>
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) => (isActive ? "active" : "")}
              onClick={() => setMenuOpen(false)}
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>

      <Outlet />
    </>
  );
}
