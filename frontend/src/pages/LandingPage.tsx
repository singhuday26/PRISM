import React, { useEffect, useState, useRef, useCallback } from 'react';
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

                    {/* PRISM Intelligence Visualization */}
                    <div className="mt-20 relative mx-auto max-w-5xl">
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/20 to-slate-950 pointer-events-none z-10" />
                        <div className="relative rounded-2xl border border-indigo-500/20 bg-slate-900/50 backdrop-blur-sm p-2 shadow-2xl shadow-indigo-500/10">
                            <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-indigo-400/80 to-transparent" />
                            <div className="rounded-xl overflow-hidden border border-slate-800 bg-[#0a0f1e]">
                                <PRISMVisualization />
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

// ─── PRISM Live Intelligence Visualization ────────────────────────────────────

const VIZ_NODES = [
    { id: 'DEL', label: 'Delhi', x: 310, y: 95, risk: 'high', cases: 4821 },
    { id: 'MUM', label: 'Mumbai', x: 185, y: 255, risk: 'high', cases: 3934 },
    { id: 'CHE', label: 'Chennai', x: 290, y: 370, risk: 'medium', cases: 2104 },
    { id: 'KOL', label: 'Kolkata', x: 460, y: 205, risk: 'medium', cases: 1876 },
    { id: 'BLR', label: 'Bangalore', x: 245, y: 330, risk: 'low', cases: 943 },
    { id: 'HYD', label: 'Hyderabad', x: 265, y: 295, risk: 'medium', cases: 1543 },
    { id: 'PUN', label: 'Pune', x: 198, y: 290, risk: 'low', cases: 712 },
    { id: 'JAI', label: 'Jaipur', x: 245, y: 138, risk: 'medium', cases: 1102 },
    { id: 'LUC', label: 'Lucknow', x: 370, y: 150, risk: 'high', cases: 2870 },
    { id: 'AHM', label: 'Ahmedabad', x: 152, y: 200, risk: 'low', cases: 631 },
    { id: 'BPH', label: 'Bhopal', x: 298, y: 218, risk: 'medium', cases: 1288 },
    { id: 'PAT', label: 'Patna', x: 420, y: 172, risk: 'high', cases: 2450 },
];

const VIZ_EDGES = [
    ['DEL', 'LUC'], ['DEL', 'JAI'], ['DEL', 'BPH'],
    ['LUC', 'PAT'], ['LUC', 'KOL'], ['PAT', 'KOL'],
    ['JAI', 'AHM'], ['JAI', 'MUM'], ['AHM', 'MUM'],
    ['MUM', 'PUN'], ['MUM', 'HYD'], ['PUN', 'BLR'],
    ['HYD', 'CHE'], ['HYD', 'BLR'], ['BPH', 'HYD'],
    ['BPH', 'LUC'],
];

const RISK_COL: Record<string, string> = { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' };
const RISK_GLOW: Record<string, string> = { high: 'rgba(239,68,68,0.45)', medium: 'rgba(245,158,11,0.35)', low: 'rgba(34,197,94,0.35)' };
const ALERT_COL: Record<string, string> = { HIGH: '#ef4444', MED: '#f59e0b', LOW: '#22c55e' };
const FORECAST_PTS = [30, 42, 38, 55, 62, 71, 68, 80, 88, 76, 90, 95];

function getVizNode(id: string) { return VIZ_NODES.find(n => n.id === id)!; }

function VizEdge({ fromId, toId }: { fromId: string; toId: string }) {
    const a = getVizNode(fromId), b = getVizNode(toId);
    if (!a || !b) return null;
    const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 18 };
    const gid = `eg-${fromId}-${toId}`;
    return (
        <g>
            <defs>
                <linearGradient id={gid} x1={a.x} y1={a.y} x2={b.x} y2={b.y} gradientUnits="userSpaceOnUse">
                    <stop offset="0%" stopColor={RISK_COL[a.risk]} stopOpacity="0.55" />
                    <stop offset="100%" stopColor={RISK_COL[b.risk]} stopOpacity="0.55" />
                </linearGradient>
            </defs>
            <path d={`M${a.x},${a.y} Q${mid.x},${mid.y} ${b.x},${b.y}`} stroke={`url(#${gid})`} strokeWidth="1" fill="none" opacity="0.35" />
        </g>
    );
}

function VizParticle({ fromId, toId, delay }: { fromId: string; toId: string; delay: number }) {
    const a = getVizNode(fromId), b = getVizNode(toId);
    if (!a || !b) return null;
    const mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 18 };
    const kfId = `kf-${fromId}-${toId}-${Math.round(delay * 10)}`;
    return (
        <g>
            <defs>
                <style>{`@keyframes ${kfId}{0%{offset-distance:0%;opacity:0}10%{opacity:1}90%{opacity:1}100%{offset-distance:100%;opacity:0}}`}</style>
            </defs>
            <circle r="2.5" fill={RISK_COL[a.risk]}
                style={{
                    offsetPath: `path("M${a.x},${a.y} Q${mid.x},${mid.y} ${b.x},${b.y}")`,
                    animation: `${kfId} 3s ${delay}s infinite ease-in-out`,
                    filter: `drop-shadow(0 0 4px ${RISK_COL[a.risk]})`,
                } as React.CSSProperties}
            />
        </g>
    );
}

const VIZ_ALERTS = [
    { city: 'Delhi', risk: 'HIGH', disease: 'Dengue', trend: '↑ 23%' },
    { city: 'Lucknow', risk: 'HIGH', disease: 'Malaria', trend: '↑ 18%' },
    { city: 'Patna', risk: 'HIGH', disease: 'Cholera', trend: '↑ 15%' },
    { city: 'Mumbai', risk: 'HIGH', disease: 'Influenza', trend: '↑ 11%' },
    { city: 'Bhopal', risk: 'MED', disease: 'Typhoid', trend: '↑ 7%' },
];

function PRISMVisualization(): React.ReactNode {
    const [time, setTime] = useState('');
    const updateTime = useCallback(() => {
        setTime(new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
    }, []);
    useEffect(() => {
        updateTime();
        const t = setInterval(updateTime, 1000);
        return () => clearInterval(t);
    }, [updateTime]);

    const maxF = Math.max(...FORECAST_PTS);
    const fW = 130, fH = 50;

    return (
        <div style={{ background: '#080d1a', fontFamily: "'Courier New', monospace", fontSize: 11, color: '#94a3b8', userSelect: 'none' }}>
            <style>{`
                @keyframes pv-pulse{0%,100%{opacity:.7;transform:scale(1)}50%{opacity:1;transform:scale(1.12)}}
                @keyframes pv-ping{0%{transform:scale(1);opacity:.8}100%{transform:scale(3.2);opacity:0}}
                @keyframes pv-blink{0%,100%{opacity:1}50%{opacity:.25}}
                @keyframes pv-scan{0%{transform:translateY(-100%);opacity:.12}100%{transform:translateY(200%);opacity:0}}
            `}</style>

            {/* Header Bar */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '9px 16px', borderBottom: '1px solid rgba(99,102,241,0.2)', background: 'rgba(10,16,36,0.9)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.35)', borderRadius: 20, padding: '3px 10px', color: '#818cf8', fontWeight: 700, letterSpacing: 2, fontSize: 9 }}>
                        <span style={{ width: 6, height: 6, background: '#4ade80', borderRadius: '50%', display: 'inline-block', animation: 'pv-pulse 2s infinite', transformOrigin: 'center', transformBox: 'fill-box' }} />
                        PRISM LIVE
                    </span>
                    <span style={{ color: '#64748b', fontSize: 10 }}>|</span>
                    <span style={{ color: '#ef4444', fontSize: 10, fontWeight: 600 }}>⬡ 4 ACTIVE THREATS</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 10, color: '#475569' }}>
                    <span>IST {time}</span>
                    <span style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.28)', borderRadius: 4, padding: '2px 8px', color: '#f87171', animation: 'pv-blink 3s infinite' }}>⚠ HIGH ALERT ZONE</span>
                </div>
            </div>

            {/* Main Content */}
            <div style={{ display: 'flex', height: 358 }}>

                {/* === SVG Network Map === */}
                <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
                    {/* Scanline overlay */}
                    <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 2 }}>
                        <div style={{ width: '100%', height: '35%', background: 'linear-gradient(to bottom, transparent, rgba(99,102,241,0.06), transparent)', animation: 'pv-scan 5s linear infinite' }} />
                    </div>
                    <svg viewBox="0 0 590 360" width="100%" height="100%" style={{ display: 'block' }}>
                        {/* Subtle grid */}
                        {[1, 2, 3, 4].map(i => <line key={`h${i}`} x1="0" y1={i * 72} x2="590" y2={i * 72} stroke="rgba(99,102,241,0.05)" strokeWidth="0.5" />)}
                        {[1, 2, 3, 4, 5, 6, 7].map(i => <line key={`v${i}`} x1={i * 74} y1="0" x2={i * 74} y2="360" stroke="rgba(99,102,241,0.05)" strokeWidth="0.5" />)}

                        {/* Corner brackets */}
                        {[{ x: 8, y: 8, sx: 1, sy: 1 }, { x: 582, y: 8, sx: -1, sy: 1 }, { x: 8, y: 352, sx: 1, sy: -1 }, { x: 582, y: 352, sx: -1, sy: -1 }].map((p, i) => (
                            <g key={i}>
                                <line x1={p.x} y1={p.y} x2={p.x + p.sx * 14} y2={p.y} stroke="#6366f1" strokeWidth="1.2" opacity="0.5" />
                                <line x1={p.x} y1={p.y} x2={p.x} y2={p.y + p.sy * 14} stroke="#6366f1" strokeWidth="1.2" opacity="0.5" />
                            </g>
                        ))}

                        {/* Map title */}
                        <text x="16" y="22" fill="#475569" fontSize="8" letterSpacing="2" fontWeight="700">INDIA SURVEILLANCE NETWORK</text>

                        {/* Edges */}
                        {VIZ_EDGES.map(([f, t], i) => <VizEdge key={i} fromId={f} toId={t} />)}

                        {/* Flow particles */}
                        {VIZ_EDGES.map(([f, t], i) => <VizParticle key={i} fromId={f} toId={t} delay={i * 0.38} />)}

                        {/* Nodes */}
                        {VIZ_NODES.map(node => (
                            <g key={node.id} transform={`translate(${node.x},${node.y})`}>
                                {node.risk === 'high' && [0, 0.8].map((d, i) => (
                                    <circle key={i} r="13" fill="none" stroke={RISK_COL[node.risk]} strokeWidth="1"
                                        style={{ animation: `pv-ping 2.2s ${d}s infinite`, transformOrigin: '0 0', transformBox: 'fill-box' }} />
                                ))}
                                <circle r="14" fill={RISK_GLOW[node.risk]} />
                                <circle r="8" fill={RISK_COL[node.risk]}
                                    style={{ animation: 'pv-pulse 2.5s infinite', transformOrigin: '0 0', transformBox: 'fill-box' }} />
                                <circle r="3" fill="white" opacity="0.9" />
                                <text x="0" y="27" textAnchor="middle" fill="#cbd5e1" fontSize="8.5" fontWeight="700" letterSpacing="0.5">{node.id}</text>
                                <text x="0" y="37" textAnchor="middle" fill="#475569" fontSize="7.5">{node.cases.toLocaleString()}</text>
                            </g>
                        ))}

                        {/* Risk legend */}
                        <g transform="translate(14,336)">
                            {[{ l: 'HIGH', r: 'high' }, { l: 'MED', r: 'medium' }, { l: 'LOW', r: 'low' }].map((item, i) => (
                                <g key={item.l} transform={`translate(${i * 72},0)`}>
                                    <circle cx="5" cy="5" r="4" fill={RISK_COL[item.r]} opacity="0.85" />
                                    <text x="13" y="9" fill="#475569" fontSize="8">{item.l} RISK</text>
                                </g>
                            ))}
                        </g>
                    </svg>
                </div>

                {/* === Right Panel === */}
                <div style={{ width: 182, borderLeft: '1px solid rgba(99,102,241,0.15)', display: 'flex', flexDirection: 'column' }}>

                    {/* Active Alerts */}
                    <div style={{ flex: 1, padding: '10px 11px', borderBottom: '1px solid rgba(99,102,241,0.12)', overflowY: 'auto' }}>
                        <div style={{ color: '#818cf8', fontWeight: 700, letterSpacing: 1.5, fontSize: 8.5, marginBottom: 7 }}>ACTIVE ALERTS</div>
                        {VIZ_ALERTS.map((a, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '5px 0', borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                                <span style={{ width: 6, height: 6, borderRadius: '50%', background: ALERT_COL[a.risk], flexShrink: 0, boxShadow: `0 0 5px ${ALERT_COL[a.risk]}` }} />
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{ color: '#e2e8f0', fontWeight: 700, fontSize: 10, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.city}</div>
                                    <div style={{ color: '#475569', fontSize: 8.5 }}>{a.disease}</div>
                                </div>
                                <span style={{ color: ALERT_COL[a.risk], fontSize: 9, fontWeight: 700, flexShrink: 0 }}>{a.trend}</span>
                            </div>
                        ))}
                    </div>

                    {/* Forecast Sparkline */}
                    <div style={{ padding: '9px 11px', borderBottom: '1px solid rgba(99,102,241,0.12)' }}>
                        <div style={{ color: '#818cf8', fontWeight: 700, letterSpacing: 1.5, fontSize: 8.5, marginBottom: 5 }}>7-DAY CASE FORECAST</div>
                        <svg viewBox={`0 0 ${fW} ${fH}`} width="100%" height={fH} style={{ overflow: 'visible' }}>
                            <defs>
                                <linearGradient id="fg" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="0%" stopColor="#818cf8" stopOpacity="0.35" />
                                    <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
                                </linearGradient>
                            </defs>
                            <path
                                d={`M0,${fH} ` + FORECAST_PTS.map((v, i) => `L${(i / (FORECAST_PTS.length - 1)) * fW},${fH - (v / maxF) * (fH - 4)}`).join(' ') + ` L${fW},${fH} Z`}
                                fill="url(#fg)"
                            />
                            <polyline
                                points={FORECAST_PTS.map((v, i) => `${(i / (FORECAST_PTS.length - 1)) * fW},${fH - (v / maxF) * (fH - 4)}`).join(' ')}
                                fill="none" stroke="#818cf8" strokeWidth="1.5"
                            />
                            <circle cx={fW} cy={fH - (FORECAST_PTS[FORECAST_PTS.length - 1] / maxF) * (fH - 4)} r="3" fill="#4ade80" style={{ filter: 'drop-shadow(0 0 4px #4ade80)' }} />
                        </svg>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3 }}>
                            <span style={{ fontSize: 8, color: '#475569' }}>Today</span>
                            <span style={{ fontSize: 8, color: '#4ade80', fontWeight: 700 }}>+7d ↑95</span>
                        </div>
                    </div>

                    {/* System Status */}
                    <div style={{ padding: '9px 11px' }}>
                        <div style={{ color: '#818cf8', fontWeight: 700, letterSpacing: 1.5, fontSize: 8.5, marginBottom: 6 }}>SYSTEM STATUS</div>
                        {[
                            { label: 'Data Pipeline', ok: true },
                            { label: 'ARIMA Engine', ok: true },
                            { label: 'Alert Daemon', ok: true },
                            { label: 'Report Gen.', ok: true },
                        ].map((s, i) => (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                <span style={{ fontSize: 8.5, color: '#64748b' }}>{s.label}</span>
                                <span style={{ fontSize: 8, color: '#4ade80', fontWeight: 700 }}>● ONLINE</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Bottom Metrics Bar */}
            <div style={{ display: 'flex', borderTop: '1px solid rgba(99,102,241,0.15)', background: 'rgba(10,16,36,0.7)' }}>
                {[
                    { label: 'NEW CASES TODAY', value: '14,580', sub: '↑23%', color: '#ef4444' },
                    { label: 'RESOURCES DEPLOYED', value: '6,420', sub: 'units', color: '#818cf8' },
                    { label: 'AVG RISK SCORE', value: '74/100', sub: 'HIGH', color: '#f59e0b' },
                    { label: 'STATES MONITORED', value: '28', sub: 'LIVE', color: '#4ade80' },
                ].map((m, i) => (
                    <div key={i} style={{ flex: 1, padding: '9px 13px', borderRight: i < 3 ? '1px solid rgba(99,102,241,0.12)' : 'none' }}>
                        <div style={{ color: '#475569', fontSize: 7.5, letterSpacing: 1, marginBottom: 2 }}>{m.label}</div>
                        <div style={{ color: '#e2e8f0', fontSize: 13, fontWeight: 700 }}>{m.value}</div>
                        <div style={{ color: m.color, fontSize: 8.5, fontWeight: 700 }}>{m.sub}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
