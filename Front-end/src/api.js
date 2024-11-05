// src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/users';

// Helper to set up API instance with base URL
const api = axios.create({
    baseURL: API_URL,
});

// Register a new user
export const registerUser = async (userData) => {
    const response = await api.post('/register/', userData);
    return response.data;
};

// Log in and store the JWT token and userType
export const loginUser = async (credentials) => {
    const response = await api.post('/login/', credentials);
    localStorage.setItem("token", response.data.access);
    localStorage.setItem("userType", response.data.user_type); // Save userType to localStorage
    return response.data;
};

// Get profile based on userType
export const getProfile = async (userType) => {
    const endpoint = userType === "buyer" ? "/buyer/profile/" : "/seller/profile/";
    const response = await api.get(endpoint, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    return response.data;
};
