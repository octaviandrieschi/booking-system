// Componenta principală a aplicației
// Gestionează rutarea și protecția rutelor

import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./components/Home";
import Login from "./components/Login";
import Register from "./components/Register";
import BookingForm from "./components/BookingForm";
import Receipt from "./components/Receipt";
import Appointments from "./components/Appointments";
import AdminDashboard from "./components/AdminDashboard";
import AdminBookings from './components/AdminBookings';
import "./App.css";

function App() {
  // State pentru starea de autentificare și rolul utilizatorului
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));
  const userRole = localStorage.getItem("userRole");

  // Componenta pentru protejarea rutelor administrative
  const AdminRoute = ({ children }) => {
    return userRole === "admin" ? children : <Navigate to="/" />;
  };

  // Componenta pentru protejarea rutelor utilizatorilor normali
  const UserRoute = ({ children }) => {
    return isLoggedIn ? children : <Navigate to="/login" />;
  };

  // Componenta pentru rutele publice (doar pentru vizitatori neautentificați)
  const PublicRoute = ({ children }) => {
    return !isLoggedIn ? children : <Navigate to="/" />;
  };

  return (
    <Router>
      <div className="App">
        <Navbar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />
        <Routes>
          {/* Redirecționare implicită către login pentru utilizatori neautentificați */}
          <Route path="/" element={
            isLoggedIn ? (
              <UserRoute>
                <Home />
              </UserRoute>
            ) : (
              <Navigate to="/login" />
            )
          } />

          {/* Rute publice - accesibile doar utilizatorilor neautentificați */}
          <Route path="/login" element={
            <PublicRoute>
              <Login setIsLoggedIn={setIsLoggedIn} />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />

          {/* Rute protejate pentru admin */}
          <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
          <Route path="/admin/bookings" element={<AdminRoute><AdminBookings /></AdminRoute>} />

          {/* Rute protejate pentru utilizatori */}
          <Route path="/book" element={<UserRoute><BookingForm /></UserRoute>} />
          <Route path="/receipt/:id" element={<UserRoute><Receipt /></UserRoute>} />
          <Route path="/appointments" element={<UserRoute><Appointments /></UserRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
