import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Activity, Globe, ArrowRight, Command, Server, Cpu, Layers } from 'lucide-react';

export function LandingPage() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-indigo-500/30">
            {/* Navigation */}
            <nav className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${scrolled ? 'bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50 py-4' : 'bg-transparent py-6'}`}>
                <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/20">
                            <Command className="w-6 h-6 text-white" />
                        </div>
                        <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                            PRISM
                        </span>
                    </div>
                    <div className="flex items-center gap-6">
                        <Link to="/login" className="text-sm font-medium text-slate-300 hover:text-white transition-colors">
                            Sign In
                        </Link>
                        <Link to="/login" className="group relative inline-flex items-center justify-center gap-2 px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 rounded-full overflow-hidden transition-all hover:bg-indigo-500 hover:shadow-[0_0_20px_rgba(99,102,241,0.4)] focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-slate-950">
                            <span className="relative z-10 flex items-center gap-2">
                                Launch Command <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                            </span>
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
                {/* Background Effects */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-600/20 rounded-full blur-[120px] opacity-50 pointer-events-none" />
                <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px] opacity-50 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[120px] opacity-50 pointer-events-none" />

                <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
                    <div className="text-center max-w-4xl mx-auto">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700/50 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-8 animate-fade-in-up">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                            </span>
                            System Operational
                        </div>

                        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 leading-[1.1]">
                            Next-Generation <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-blue-400">
                                Epidemic Intelligence
                            </span>
                        </h1>

                        <p className="text-lg md:text-xl text-slate-400 mb-12 max-w-2xl mx-auto leading-relaxed">
                            Advanced forecasting, resource allocation, and real-time operational mapping for public health command centers. Anticipate threats before they emerge.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link to="/login" className="w-full sm:w-auto px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full font-semibold text-lg transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_30px_rgba(99,102,241,0.5)] flex items-center justify-center gap-2 group">
                                Access Platform
                                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                            </Link>
                            <a href="#features" className="w-full sm:w-auto px-8 py-4 bg-slate-800/50 hover:bg-slate-800 text-white rounded-full font-semibold text-lg border border-slate-700 transition-all flex items-center justify-center">
                                Explore Features
                            </a>
                        </div>
                    </div>

                    {/* Abstract Dashboard Preview */}
                    <div className="mt-20 relative mx-auto max-w-5xl">
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950 pointer-events-none z-10" />
                        <div className="relative rounded-2xl border border-slate-800/60 bg-slate-900/50 backdrop-blur-sm p-2 shadow-2xl">
                            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
                            <div className="rounded-xl overflow-hidden border border-slate-800 bg-[#0f172a] aspect-[16/9] flex items-center justify-center relative">
                                {/* Decorative mock UI elements */}
                                <div className="absolute inset-0 p-8 grid grid-cols-3 gap-6 opacity-40">
                                    <div className="col-span-2 space-y-6">
                                        <div className="h-48 rounded-lg bg-slate-800/50 border border-slate-700/50 flex items-end p-4 gap-2">
                                            {[40, 70, 45, 90, 65, 85, 110, 80, 100].map((h, i) => (
                                                <div key={i} className="flex-1 rounded-t-sm bg-indigo-500/50" style={{ height: `${h}%` }}></div>
                                            ))}
                                        </div>
                                        <div className="grid grid-cols-2 gap-6">
                                            <div className="h-32 rounded-lg bg-slate-800/50 border border-slate-700/50 p-4">
                                                <div className="h-4 w-1/3 bg-slate-700 rounded mb-4" />
                                                <div className="h-8 w-1/2 bg-slate-600 rounded" />
                                            </div>
                                            <div className="h-32 rounded-lg bg-slate-800/50 border border-slate-700/50 p-4">
                                                <div className="h-4 w-1/3 bg-slate-700 rounded mb-4" />
                                                <div className="h-8 w-1/2 bg-indigo-500/50 rounded" />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="col-span-1 border border-slate-700/50 bg-slate-800/50 rounded-lg p-4 space-y-4">
                                        <div className="h-4 w-1/2 bg-slate-700 rounded" />
                                        <div className="space-y-2">
                                            {[1, 2, 3, 4, 5].map(i => (
                                                <div key={i} className="h-10 bg-slate-700/50 rounded" />
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                {/* Center generic globe logo to imply maps */}
                                <Globe className="w-24 h-24 text-indigo-500/20 absolute" strokeWidth={1} />
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Features Section */}
            <section id="features" className="py-24 relative z-10 border-t border-slate-800/50 bg-slate-950/50">
                <div className="max-w-7xl mx-auto px-6 md:px-12">
                    <div className="text-center mb-16 max-w-2xl mx-auto">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">Command Center Capabilities</h2>
                        <p className="text-slate-400">A unified platform designed for rapid response, predictive modeling, and strategic resource deployment.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        <FeatureCard
                            icon={<Activity className="w-6 h-6 text-indigo-400" />}
                            title="Predictive Forecasting"
                            description="Utilize advanced ML models to predict outbreak trajectories days in advance, allowing for proactive rather than reactive measures."
                        />
                        <FeatureCard
                            icon={<Shield className="w-6 h-6 text-emerald-400" />}
                            title="Resource Optimization"
                            description="Predictive allocation of beds, ventilators, and medical personnel across regions based on anticipated surge mapping."
                        />
                        <FeatureCard
                            icon={<Globe className="w-6 h-6 text-blue-400" />}
                            title="Real-time Operational Map"
                            description="Live geospatial intelligence visualizing active threats, regional vulnerabilities, and current deployment statuses."
                        />
                        <FeatureCard
                            icon={<Server className="w-6 h-6 text-purple-400" />}
                            title="Data Ingestion Engine"
                            description="Automated scraping and processing of structured and unstructured health data from global and regional sources."
                        />
                        <FeatureCard
                            icon={<Cpu className="w-6 h-6 text-rose-400" />}
                            title="AI-Powered Reports"
                            description="Generate comprehensive, actionable PDF briefings instantaneously using LLM-assisted synthesis of current metrics."
                        />
                        <FeatureCard
                            icon={<Layers className="w-6 h-6 text-amber-400" />}
                            title="Unified Architecture"
                            description="Secure, scalable infrastructure handling everything from raw data pipelines to high-performance frontend visualization."
                        />
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-slate-800 py-12 text-center text-slate-500">
                <div className="flex items-center justify-center gap-2 mb-4">
                    <Command className="w-5 h-5 text-indigo-500" />
                    <span className="font-semibold text-slate-300">PRISM</span>
                </div>
                <p>© {new Date().getFullYear()} PRISM Command Platform. All rights reserved.</p>
            </footer>
        </div>
    );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
    return (
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-colors group">
            <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-3 text-slate-200">{title}</h3>
            <p className="text-slate-400 leading-relaxed">{description}</p>
        </div>
    );
}
