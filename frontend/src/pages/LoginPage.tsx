import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { login } from '../lib/api';
import { Lock, User, AlertCircle, Shield } from 'lucide-react';

export function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const { user, refreshUser } = useAuth();
    const navigate = useNavigate();

    if (user) {
        return <Navigate to="/app" replace />;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSubmitting(true);

        try {
            await login(username, password);
            await refreshUser();
            navigate('/app');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Login failed. Please check your credentials.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-4 font-sans">
            <div className="max-w-md w-full">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center p-3 bg-blue-500/10 rounded-2xl mb-4 border border-blue-500/20">
                        <Shield className="w-10 h-10 text-blue-500" />
                    </div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">PRISM Command</h1>
                    <p className="text-slate-400">Secure access to epidemic intelligence</p>
                </div>

                <div className="bg-[#1e293b] border border-slate-700/60 rounded-2xl p-8 shadow-2xl relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 opacity-50"></div>

                    <form onSubmit={handleSubmit} className="space-y-6 relative z-10">
                        {error && (
                            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400 text-sm animate-in fade-in slide-in-from-top-2 duration-300">
                                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 ml-1">
                                Username
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                                    <User className="w-5 h-5" />
                                </div>
                                <input
                                    type="text"
                                    required
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="block w-full bg-[#0f172a]/50 border border-slate-700 text-white rounded-xl pl-12 pr-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all placeholder:text-slate-600"
                                    placeholder="Enter your username"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 ml-1">
                                Password
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                                    <Lock className="w-5 h-5" />
                                </div>
                                <input
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="block w-full bg-[#0f172a]/50 border border-slate-700 text-white rounded-xl pl-12 pr-4 py-3.5 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all placeholder:text-slate-600"
                                    placeholder="••••••••"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={submitting}
                            className="w-full bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:opacity-50 text-white font-semibold py-3.5 rounded-xl transition-all shadow-lg shadow-blue-500/20 active:scale-[0.98] mt-2 flex items-center justify-center gap-2"
                        >
                            {submitting ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                                    Authenticating...
                                </>
                            ) : 'Sign In'}
                        </button>
                    </form>

                    {/* Background Decoration */}
                    <div className="absolute -bottom-20 -right-20 w-40 h-40 bg-blue-500/5 rounded-full blur-3xl pointer-events-none group-hover:bg-blue-500/10 transition-colors duration-500"></div>
                </div>

                <p className="mt-8 text-center text-slate-500 text-sm">
                    Protected by PRISM Security Layer.
                    <br />
                    Contact administrator for access.
                </p>
            </div>
        </div>
    );
}
