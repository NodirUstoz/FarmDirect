import React from "react";
import { Routes, Route } from "react-router-dom";

import Header from "./components/layout/Header";
import Footer from "./components/layout/Footer";
import HomePage from "./pages/HomePage";
import MarketPage from "./pages/MarketPage";
import FarmPage from "./pages/FarmPage";
import ProductPage from "./pages/ProductPage";
import SubscriptionPage from "./pages/SubscriptionPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";
import FarmerDashboard from "./pages/FarmerDashboard";
import ProfilePage from "./pages/ProfilePage";
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";

function App() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/market" element={<MarketPage />} />
          <Route path="/farms/:slug" element={<FarmPage />} />
          <Route path="/products/:id" element={<ProductPage />} />
          <Route path="/subscriptions" element={<SubscriptionPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/dashboard" element={<FarmerDashboard />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
