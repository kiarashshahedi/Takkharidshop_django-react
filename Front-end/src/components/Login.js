// src/components/Login.js
import React, { useState } from 'react';
import { loginUser } from '../api';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [credentials, setCredentials] = useState({ username: '', password: '' });
    const navigate = useNavigate();

    const handleChange = (e) => {
        setCredentials({ ...credentials, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await loginUser(credentials);
            const userType = localStorage.getItem("userType");
            navigate(userType === "buyer" ? "/profile" : "/profile");
        } catch (error) {
            console.error("Login error:", error);
            alert("Login failed.");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input name="username" onChange={handleChange} placeholder="Username" required />
            <input type="password" name="password" onChange={handleChange} placeholder="Password" required />
            <button type="submit">Login</button>
        </form>
    );
};

export default Login;
