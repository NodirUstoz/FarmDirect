import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { FiShoppingCart, FiMenu, FiX, FiUser } from "react-icons/fi";
import useAuth from "../../hooks/useAuth";
import { selectCartItemCount } from "../../store/cartSlice";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { isAuthenticated, isFarmer, user, doLogout } = useAuth();
  const cartCount = useSelector(selectCartItemCount);
  const navigate = useNavigate();

  const handleLogout = () => {
    doLogout();
    navigate("/");
  };

  return (
    <header className="header">
      <div className="header__inner container">
        {/* Logo */}
        <Link to="/" className="header__logo">
          <span className="header__logo-icon">F</span>
          <span className="header__logo-text">FarmDirect</span>
        </Link>

        {/* Desktop nav */}
        <nav className={`header__nav ${menuOpen ? "header__nav--open" : ""}`}>
          <Link to="/market" className="header__link" onClick={() => setMenuOpen(false)}>
            Marketplace
          </Link>
          <Link to="/subscriptions" className="header__link" onClick={() => setMenuOpen(false)}>
            Subscriptions
          </Link>
          {isAuthenticated && isFarmer && (
            <Link to="/dashboard" className="header__link" onClick={() => setMenuOpen(false)}>
              Dashboard
            </Link>
          )}
        </nav>

        {/* Actions */}
        <div className="header__actions">
          <Link to="/cart" className="header__cart-btn" aria-label="Shopping cart">
            <FiShoppingCart size={22} />
            {cartCount > 0 && <span className="header__cart-badge">{cartCount}</span>}
          </Link>

          {isAuthenticated ? (
            <div className="header__user-menu">
              <Link to="/profile" className="header__user-btn" aria-label="Profile">
                <FiUser size={22} />
                {user && <span className="header__username">{user.first_name}</span>}
              </Link>
              <button className="btn btn--sm btn--outline" onClick={handleLogout}>
                Logout
              </button>
            </div>
          ) : (
            <div className="header__auth-links">
              <Link to="/login" className="btn btn--sm btn--outline">
                Log In
              </Link>
              <Link to="/register" className="btn btn--sm btn--primary">
                Sign Up
              </Link>
            </div>
          )}

          <button
            className="header__hamburger"
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label="Toggle menu"
          >
            {menuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
          </button>
        </div>
      </div>
    </header>
  );
}
