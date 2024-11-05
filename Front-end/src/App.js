// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import BuyerProfile from './components/BuyerProfile';
import SellerProfile from './components/SellerProfile';

function App() {
    const userType = localStorage.getItem("userType"); // Get userType from localStorage

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                {userType === "buyer" && <Route path="/profile" element={<BuyerProfile />} />}
                {userType === "seller" && <Route path="/profile" element={<SellerProfile />} />}
                <Route path="*" element={<Navigate to="/login" />} />
            </Routes>
        </Router>
    );
}

export default App;
