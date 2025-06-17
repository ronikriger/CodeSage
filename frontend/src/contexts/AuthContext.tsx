import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface User {
    id: number;
    email: string;
    username: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (username: string, password: string) => Promise<void>;
    register: (email: string, username: string, password: string) => Promise<void>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

    useEffect(() => {
        if (token) {
            localStorage.setItem('token', token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    const login = async (username: string, password: string) => {
        try {
            const response = await axios.post('http://localhost:8000/api/auth/login', {
                username,
                password,
            });
            const { access_token } = response.data;
            setToken(access_token);

            // Fetch user data
            const userResponse = await axios.get('http://localhost:8000/api/auth/me');
            setUser(userResponse.data);
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    const register = async (email: string, username: string, password: string) => {
        try {
            const response = await axios.post('http://localhost:8000/api/auth/register', {
                email,
                username,
                password,
            });
            const { access_token } = response.data;
            setToken(access_token);

            // Fetch user data
            const userResponse = await axios.get('http://localhost:8000/api/auth/me');
            setUser(userResponse.data);
        } catch (error) {
            console.error('Registration failed:', error);
            throw error;
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                login,
                register,
                logout,
                isAuthenticated: !!token,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}; 