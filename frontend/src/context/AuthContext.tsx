/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { type User, fetchMe } from '../lib/api';

/** Demo mode: allow unauthenticated visitors to explore the dashboard */
const DEMO_MODE = true;

const DEMO_USER: User = {
    id: 'demo',
    username: 'Demo Viewer',
    email: 'demo@prism-command.dev',
    role: 'viewer',
};

interface AuthContextType {
    user: User | null;
    loading: boolean;
    logout: () => void;
    refreshUser: () => Promise<void>;
    isDemo: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [isDemo, setIsDemo] = useState(false);

    const refreshUser = async () => {
        const token = localStorage.getItem('prism_token');
        if (!token) {
            if (DEMO_MODE) {
                setUser(DEMO_USER);
                setIsDemo(true);
            } else {
                setUser(null);
            }
            setLoading(false);
            return;
        }
        try {
            const userData = await fetchMe();
            setUser(userData);
            setIsDemo(false);
        } catch (err) {
            console.error('Failed to refresh user:', err);
            localStorage.removeItem('prism_token');
            if (DEMO_MODE) {
                setUser(DEMO_USER);
                setIsDemo(true);
            } else {
                setUser(null);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        refreshUser();
    }, []);

    const logout = () => {
        localStorage.removeItem('prism_token');
        if (DEMO_MODE) {
            setUser(DEMO_USER);
            setIsDemo(true);
        } else {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, logout, refreshUser, isDemo }}>
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
