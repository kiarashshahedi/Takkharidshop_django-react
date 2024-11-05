// src/context/AuthContext.js
import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, getProfile } from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const profile = await getProfile();
                setUser(profile);
            } catch {
                setUser(null);
            }
        };
        fetchProfile();
    }, []);

    const login = async (credentials) => {
        const data = await loginUser(credentials);
        localStorage.setItem('accessToken', data.access);
        setUser(await getProfile());
    };

    const logout = () => {
        localStorage.removeItem('accessToken');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
