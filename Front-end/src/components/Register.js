// src/components/Register.js
import React, { useState } from 'react';
import { registerUser } from '../api';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: '',
        user_type: 'buyer',  // Default to 'buyer'
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await registerUser(formData);
            alert("Registration successful! You can now log in.");
        } catch (error) {
            console.error("Registration error:", error);
            alert("Registration failed.");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input name="username" onChange={handleChange} placeholder="Username" required />
            <input type="password" name="password" onChange={handleChange} placeholder="Password" required />
            <input name="email" onChange={handleChange} placeholder="Email" required />
            <select name="user_type" onChange={handleChange}>
                <option value="buyer">Buyer</option>
                <option value="seller">Seller</option>
            </select>
            <button type="submit">Register</button>
        </form>
    );
};

export default Register;
