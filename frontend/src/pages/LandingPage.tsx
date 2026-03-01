import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Activity, Globe, ArrowRight, Command, Server, Cpu, Layers, Database, Zap, BarChart3 } from 'lucide-react';

// Animated counter hook
function useCounter(target: number, duration = 2000, startOnView = true) {
    const [count, setCount] = useState(0);
    const [hasStarted, setHasStarted] = useState(!startOnView);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!startOnView || !ref.current) return;
        const observer = new IntersectionObserver(
            ([entry]) => { if (entry.isIntersecting) setHasStarted(true); },
            { threshold: 0.3 }
        );
        observer.observe(ref.current);
        return () => observer.disconnect();
    }, [startOnView]);

    useEffect(() => {
        if (!hasStarted) return;
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                setCount(target);
                clearInterval(timer);
            } else {
                setCount(Math.floor(start));
            }
        }, 16);
        return () => clearInterval(timer);
    }, [hasStarted, target, duration]);

    return [count, ref] as const;
}

export function LandingPage() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 50);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const smoothScroll = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
        e.preventDefault();
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    };

    // Counters
    const [diseasesCount, diseasesRef] = useCounter(10);
    const [statesCount, statesRef] = useCounter(28);
    const [endpointsCount, endpointsRef] = useCounter(20);
    const [uptimeCount, uptimeRef] = useCounter(99);

    return (
        <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-indigo-500/30 scroll-smooth">
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
                        <a href="#features" onClick={(e) => smoothScroll(e, 'features')} className="hidden sm:inline text-sm font-medium text-slate-400 hover:text-white transition-colors">Features</a>
                        <a href="#how-it-works" onClick={(e) => smoothScroll(e, 'how-it-works')} className="hidden sm:inline text-sm font-medium text-slate-400 hover:text-white transition-colors">How It Works</a>
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
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700/50 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-8">
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
                            <a href="#features" onClick={(e) => smoothScroll(e, 'features')} className="w-full sm:w-auto px-8 py-4 bg-slate-800/50 hover:bg-slate-800 text-white rounded-full font-semibold text-lg border border-slate-700 transition-all flex items-center justify-center">
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
                                <Globe className="w-24 h-24 text-indigo-500/20 absolute" strokeWidth={1} />
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Stats Section */}
            <section className="py-16 border-t border-b border-slate-800/50 bg-slate-900/30">
                <div className="max-w-7xl mx-auto px-6 md:px-12">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        <div ref={diseasesRef} className="space-y-2">
                            <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
                                {diseasesCount}+
                            </div>
                            <p className="text-sm text-slate-400 uppercase tracking-wider font-medium">Diseases Tracked</p>
                        </div>
                        <div ref={statesRef} className="space-y-2">
                            <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                                {statesCount}
                            </div>
                            <p className="text-sm text-slate-400 uppercase tracking-wider font-medium">States Monitored</p>
                        </div>
                        <div ref={endpointsRef} className="space-y-2">
                            <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-green-400">
                                {endpointsCount}+
                            </div>
                            <p className="text-sm text-slate-400 uppercase tracking-wider font-medium">API Endpoints</p>
                        </div>
                        <div ref={uptimeRef} className="space-y-2">
                            <div className="text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-orange-400">
                                {uptimeCount}%
                            </div>
                            <p className="text-sm text-slate-400 uppercase tracking-wider font-medium">Uptime SLA</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works Section */}
            <section id="how-it-works" className="py-24 relative z-10">
                <div className="max-w-7xl mx-auto px-6 md:px-12">
                    <div className="text-center mb-16 max-w-2xl mx-auto">
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">How PRISM Works</h2>
                        <p className="text-slate-400">From raw data to actionable intelligence in three steps.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8 relative">
                        {/* Connector line */}
                        <div className="hidden md:block absolute top-12 left-[17%] right-[17%] h-px bg-gradient-to-r from-indigo-500/50 via-purple-500/50 to-emerald-500/50" />

                        <StepCard
                            step={1}
                            icon={<Database className="w-6 h-6 text-indigo-400" />}
                            title="Data Ingestion"
                            description="Epidemiological case data flows in from CSV imports, automated feeds, and news intelligence — processed and stored in MongoDB."
                            color="from-indigo-500 to-blue-500"
                        />
                        <StepCard
                            step={2}
                            icon={<Zap className="w-6 h-6 text-purple-400" />}
                            title="Risk Analysis"
                            description="ARIMA/SARIMA models compute forecasts, risk scores factor in growth rates, volatility, and climate patterns to generate real-time alerts."
                            color="from-purple-500 to-pink-500"
                        />
                        <StepCard
                            step={3}
                            icon={<BarChart3 className="w-6 h-6 text-emerald-400" />}
                            title="Actionable Intelligence"
                            description="Decision-makers view heatmaps, resource predictions, and automated reports — enabling proactive public health responses."
                            color="from-emerald-500 to-green-500"
                        />
                    </div>
                </div>
            </section>

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
                            description="Utilize ARIMA/SARIMA models to predict outbreak trajectories days in advance, allowing for proactive measures."
                        />
                        <FeatureCard
                            icon={<Shield className="w-6 h-6 text-emerald-400" />}
                            title="Resource Optimization"
                            description="Predictive allocation of beds, ICU, nurses, and oxygen across regions based on anticipated surge mapping."
                        />
                        <FeatureCard
                            icon={<Globe className="w-6 h-6 text-blue-400" />}
                            title="Real-time Operational Map"
                            description="Live geospatial intelligence visualizing active threats, regional vulnerabilities, and deployment statuses."
                        />
                        <FeatureCard
                            icon={<Server className="w-6 h-6 text-purple-400" />}
                            title="Data Ingestion Engine"
                            description="Automated processing of structured and unstructured health data from global and regional sources."
                        />
                        <FeatureCard
                            icon={<Cpu className="w-6 h-6 text-rose-400" />}
                            title="Automated Reports"
                            description="Generate comprehensive PDF briefings instantaneously with synthesis of current metrics and forecasts."
                        />
                        <FeatureCard
                            icon={<Layers className="w-6 h-6 text-amber-400" />}
                            title="Multi-Disease Support"
                            description="Track 10+ diseases simultaneously with disease-isolated data pipelines and configurable risk thresholds."
                        />
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/10 via-purple-600/5 to-blue-600/10" />
                <div className="max-w-4xl mx-auto px-6 md:px-12 text-center relative z-10">
                    <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Deploy Intelligence?</h2>
                    <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
                        Join the next generation of public health command centers. Start monitoring, forecasting, and responding today.
                    </p>
                    <Link to="/login" className="inline-flex items-center gap-2 px-10 py-5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full font-semibold text-lg transition-all shadow-[0_0_30px_rgba(99,102,241,0.3)] hover:shadow-[0_0_40px_rgba(99,102,241,0.5)] group">
                        Launch PRISM Command
                        <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-slate-800 py-12">
                <div className="max-w-7xl mx-auto px-6 md:px-12">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-2">
                            <Command className="w-5 h-5 text-indigo-500" />
                            <span className="font-semibold text-slate-300">PRISM</span>
                        </div>
                        <div className="flex items-center gap-8 text-sm text-slate-500">
                            <a href="#features" onClick={(e) => smoothScroll(e, 'features')} className="hover:text-slate-300 transition-colors">Features</a>
                            <a href="#how-it-works" onClick={(e) => smoothScroll(e, 'how-it-works')} className="hover:text-slate-300 transition-colors">How It Works</a>
                            <a href="https://github.com/singhuday26/PRISM" target="_blank" rel="noopener noreferrer" className="hover:text-slate-300 transition-colors">GitHub</a>
                        </div>
                        <p className="text-sm text-slate-500">© {new Date().getFullYear()} PRISM Command Platform</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}

function StepCard({ step, icon, title, description, color }: { step: number; icon: React.ReactNode; title: string; description: string; color: string }) {
    return (
        <div className="relative text-center group">
            <div className={`w-24 h-24 rounded-2xl bg-gradient-to-br ${color} p-[1px] mx-auto mb-6 group-hover:scale-105 transition-transform`}>
                <div className="w-full h-full rounded-2xl bg-slate-950 flex flex-col items-center justify-center gap-1">
                    {icon}
                    <span className="text-xs font-bold text-slate-500">STEP {step}</span>
                </div>
            </div>
            <h3 className="text-xl font-semibold mb-3 text-slate-200">{title}</h3>
            <p className="text-slate-400 leading-relaxed text-sm">{description}</p>
        </div>
    );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
    return (
        <div className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 hover:border-slate-700 transition-all hover:translate-y-[-2px] group">
            <div className="w-12 h-12 rounded-lg bg-slate-800 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-3 text-slate-200">{title}</h3>
            <p className="text-slate-400 leading-relaxed">{description}</p>
        </div>
    );
}
