import React, { createContext, useContext, useState, useEffect } from 'react';
import { type User, fetchMe } from '../lib/api';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = async () => {
        const token = localStorage.getItem('prism_token');
        if (!token) {
            setUser(null);
            setLoading(false);
            return;
        }
        try {
            const userData = await fetchMe();
            setUser(userData);
        } catch (err) {
            console.error('Failed to refresh user:', err);
            localStorage.removeItem('prism_token');
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refreshUser();
    }, []);

    const logout = () => {
        localStorage.removeItem('prism_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, logout, refreshUser }}>
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
