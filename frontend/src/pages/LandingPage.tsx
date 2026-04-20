import React, { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import {
  Shield,
  Activity,
  Globe,
  ArrowRight,
  Server,
  Cpu,
  Layers,
} from "lucide-react";

// Animated counter hook
function useCounter(target: number, duration = 2000, startOnView = true) {
  const [count, setCount] = useState(0);
  const [hasStarted, setHasStarted] = useState(!startOnView);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!startOnView || !ref.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setHasStarted(true);
      },
      { threshold: 0.3 },
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

function useRevealOnScroll(threshold = 0.25) {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || visible) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold },
    );

    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [threshold, visible]);

  return { ref, visible } as const;
}

const REVEAL_DELAY_CLASSES = [
  "delay-0",
  "delay-100",
  "delay-200",
  "delay-300",
  "delay-500",
  "delay-700",
];

function getRevealDelayClass(index: number) {
  return REVEAL_DELAY_CLASSES[
    Math.max(0, Math.min(index, REVEAL_DELAY_CLASSES.length - 1))
  ];
}

export function LandingPage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const smoothScroll = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  // Counters
  const [diseasesCount, diseasesRef] = useCounter(10);
  const [statesCount, statesRef] = useCounter(28);
  const [endpointsCount, endpointsRef] = useCounter(20);
  const [uptimeCount, uptimeRef] = useCounter(99);

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-slate-800 font-sans selection:bg-[#E07A5F]/20 scroll-smooth">
      {/* Navigation */}
      <nav
        className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${scrolled ? "bg-[#FAFAFA]/90 backdrop-blur-md border-b border-slate-200 py-4" : "bg-transparent py-6"}`}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src="/prism-logo.png"
              alt="PRISM Logo"
              className="h-8 md:h-10 w-auto object-contain"
            />
            <span className="font-serif text-xl md:text-2xl font-bold tracking-tight text-slate-900">
              PRISM
            </span>
          </div>
          <div className="flex items-center gap-6">
            <a
              href="#features"
              onClick={(e) => smoothScroll(e, "features")}
              className="hidden sm:inline text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              Features
            </a>
            <a
              href="#how-it-works"
              onClick={(e) => smoothScroll(e, "how-it-works")}
              className="hidden sm:inline text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              How It Works
            </a>
            <a
              href="https://github.com/singhuday26/PRISM"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              GitHub
            </a>
            <Link
              to="/app"
              className="inline-flex items-center justify-center px-6 py-2 text-sm font-medium text-white bg-slate-800 rounded-md transition-colors hover:bg-slate-700"
            >
              Enter Command
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative pt-32 pb-20 md:pt-48 md:pb-32 bg-[#FAFAFA]">
        <div className="max-w-7xl mx-auto px-6 md:px-12 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="font-serif text-5xl md:text-7xl font-bold tracking-tight text-slate-900 mb-8 leading-[1.1]">
              Predictive Intelligence <br /> for Global Health.
            </h1>

            <p className="text-lg md:text-xl text-slate-600 mb-12 max-w-2xl mx-auto leading-relaxed font-sans">
              Advanced forecasting, resource allocation, and real-time
              operational mapping for public health command centers. Anticipate
              threats before they emerge.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/app"
                className="w-full sm:w-auto px-8 py-3 bg-[#E07A5F] text-white rounded-md font-medium text-lg hover:bg-[#D9664A] transition-colors flex items-center justify-center gap-2"
              >
                Explore Live Demo
                <ArrowRight className="w-5 h-5" />
              </Link>
              <a
                href="#features"
                onClick={(e) => smoothScroll(e, "features")}
                className="w-full sm:w-auto px-8 py-3 border border-slate-300 bg-white/50 hover:bg-slate-50 text-slate-800 rounded-md font-medium text-lg transition-colors flex items-center justify-center text-center"
              >
                Review Infrastructure
              </a>
            </div>
          </div>

          {/* PRISM Intelligence Visualization - Light Clinical Version */}
          <div className="mt-24 relative mx-auto max-w-5xl">
            <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden p-2">
              <div className="rounded-md border border-slate-100 bg-[#FAFAFA] overflow-hidden">
                <PRISMVisualization />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Stats Section */}
      <section className="py-16 border-t border-slate-200 bg-[#FAFAFA]">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div
              ref={diseasesRef}
              className="group space-y-2 rounded-xl border border-slate-200 bg-white/70 backdrop-blur-sm p-5 transition-all duration-500 hover:-translate-y-1.5 hover:border-[#E07A5F]/35 hover:shadow-[0_16px_40px_-22px_rgba(44,62,80,0.45)]"
            >
              <div className="font-serif text-4xl md:text-5xl font-bold text-slate-900">
                {diseasesCount}+
              </div>
              <p className="text-xs text-slate-500 uppercase tracking-widest font-medium font-sans">
                Diseases Tracked
              </p>
              <div className="mx-auto h-px w-0 bg-[#E07A5F]/50 transition-all duration-500 group-hover:w-2/3" />
            </div>
            <div
              ref={statesRef}
              className="group space-y-2 rounded-xl border border-slate-200 bg-white/70 backdrop-blur-sm p-5 transition-all duration-500 hover:-translate-y-1.5 hover:border-[#E07A5F]/35 hover:shadow-[0_16px_40px_-22px_rgba(44,62,80,0.45)]"
            >
              <div className="font-serif text-4xl md:text-5xl font-bold text-slate-900">
                {statesCount}
              </div>
              <p className="text-xs text-slate-500 uppercase tracking-widest font-medium font-sans">
                States Monitored
              </p>
              <div className="mx-auto h-px w-0 bg-[#E07A5F]/50 transition-all duration-500 group-hover:w-2/3" />
            </div>
            <div
              ref={endpointsRef}
              className="group space-y-2 rounded-xl border border-slate-200 bg-white/70 backdrop-blur-sm p-5 transition-all duration-500 hover:-translate-y-1.5 hover:border-[#E07A5F]/35 hover:shadow-[0_16px_40px_-22px_rgba(44,62,80,0.45)]"
            >
              <div className="font-serif text-4xl md:text-5xl font-bold text-slate-900">
                {endpointsCount}+
              </div>
              <p className="text-xs text-slate-500 uppercase tracking-widest font-medium font-sans">
                API Endpoints
              </p>
              <div className="mx-auto h-px w-0 bg-[#E07A5F]/50 transition-all duration-500 group-hover:w-2/3" />
            </div>
            <div
              ref={uptimeRef}
              className="group space-y-2 rounded-xl border border-slate-200 bg-white/70 backdrop-blur-sm p-5 transition-all duration-500 hover:-translate-y-1.5 hover:border-[#E07A5F]/35 hover:shadow-[0_16px_40px_-22px_rgba(44,62,80,0.45)]"
            >
              <div className="font-serif text-4xl md:text-5xl font-bold text-slate-900">
                {uptimeCount}%
              </div>
              <p className="text-xs text-slate-500 uppercase tracking-widest font-medium font-sans">
                Uptime SLA
              </p>
              <div className="mx-auto h-px w-0 bg-[#E07A5F]/50 transition-all duration-500 group-hover:w-2/3" />
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section
        id="how-it-works"
        className="py-24 relative border-t border-slate-200 bg-[#FAFAFA]"
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center mb-16 max-w-2xl mx-auto">
            <h2 className="font-serif text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Operational Architecture
            </h2>
            <p className="text-slate-600 font-sans">
              Streamlined intelligence from raw ingestion to actionable public
              health directives.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 relative">
            <StepCard
              index={0}
              step="01"
              title="Data Ingestion"
              description="Epidemiological case data flows via secure pipelines into our central repository."
            />
            <StepCard
              index={1}
              step="02"
              title="Risk Analysis"
              description="Computational modeling derives forecasts and multi-variable risk assessments."
            />
            <StepCard
              index={2}
              step="03"
              title="Actionable Intelligence"
              description="Command interfaces surface regional priorities, deploying resources where critical."
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section
        id="features"
        className="py-24 relative border-t border-slate-200 bg-[#FAFAFA]"
      >
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="text-center mb-16 max-w-2xl mx-auto">
            <h2 className="font-serif text-3xl md:text-4xl font-bold text-slate-900 mb-4">
              Institute Infrastructure
            </h2>
            <p className="text-slate-600 font-sans">
              Designed for strict compliance and continuous epidemiological
              threat monitoring.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              index={0}
              icon={<Activity className="w-5 h-5 text-slate-700" />}
              title="Predictive Forecasting"
              description="Ensemble predictive models mapping disease trajectories with advanced statistical backing."
            />
            <FeatureCard
              index={1}
              icon={<Shield className="w-5 h-5 text-slate-700" />}
              title="Resource Optimization"
              description="Algorithmic allocation matching impending regional strains with medical logistics."
            />
            <FeatureCard
              index={2}
              icon={<Globe className="w-5 h-5 text-slate-700" />}
              title="Operational Geolocation"
              description="Precise macro-level mapping of biological threats overlaid on infrastructure data."
            />
            <FeatureCard
              index={3}
              icon={<Server className="w-5 h-5 text-slate-700" />}
              title="High-Volume Ingestion"
              description="Aggregating clinical records and syndromic indicators across disparate networks."
            />
            <FeatureCard
              index={4}
              icon={<Cpu className="w-5 h-5 text-slate-700" />}
              title="Synthesis Briefings"
              description="Automated clinical reports aggregating key indicators for rapid decision-making."
            />
            <FeatureCard
              index={5}
              icon={<Layers className="w-5 h-5 text-slate-700" />}
              title="Concurrent Pathology"
              description="Isolated pipelines analyzing overlapping regional outbreaks without cross-interference."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 relative border-t border-slate-200 bg-[#FAFAFA]">
        <div className="max-w-4xl mx-auto px-6 md:px-12 text-center">
          <h2 className="font-serif text-3xl md:text-5xl font-bold text-slate-900 mb-6">
            Ready to Deploy Intelligence?
          </h2>
          <p className="text-lg text-slate-600 mb-10 max-w-2xl mx-auto font-sans">
            Adopt the clinical standard for public health surveillance and
            proactive disaster management.
          </p>
          <Link
            to="/app"
            className="inline-flex items-center gap-2 px-8 py-3 bg-[#E07A5F] hover:bg-[#D9664A] text-white rounded-md font-medium text-lg transition-colors"
          >
            Launch Command Interface
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-12 bg-white">
        <div className="max-w-7xl mx-auto px-6 md:px-12">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <span className="font-serif text-lg font-bold text-slate-900">
                PRISM
              </span>
            </div>
            <div className="flex items-center gap-8 text-sm text-slate-500 font-sans">
              <a
                href="#features"
                onClick={(e) => smoothScroll(e, "features")}
                className="hover:text-slate-800 transition-colors"
              >
                Features
              </a>
              <a
                href="#how-it-works"
                onClick={(e) => smoothScroll(e, "how-it-works")}
                className="hover:text-slate-800 transition-colors"
              >
                Architecture
              </a>
              <a
                href="https://github.com/singhuday26/PRISM"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-slate-800 transition-colors"
              >
                Source
              </a>
            </div>
            <p className="text-sm text-slate-400 font-sans">
              © {new Date().getFullYear()} Institute for Global Health
              Intelligence
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function StepCard({
  step,
  title,
  description,
  index = 0,
}: {
  step: string;
  title: string;
  description: string;
  index?: number;
}) {
  const { ref, visible } = useRevealOnScroll();
  const delayClass = getRevealDelayClass(index);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      } ${delayClass}`}
    >
      <div className="lp-card group relative overflow-hidden rounded-lg border border-slate-200 bg-white/80 p-8 text-left backdrop-blur-sm hover:-translate-y-2 hover:border-[#E07A5F]/45 hover:shadow-[0_26px_56px_-32px_rgba(44,62,80,0.45)]">
        <div className="pointer-events-none absolute -right-12 -top-12 h-32 w-32 rounded-full bg-[radial-gradient(circle,rgba(224,122,95,0.24),transparent_70%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
        <div className="pointer-events-none absolute inset-0 rounded-lg">
          <div className="lp-card-sheen" />
        </div>
        <div className="relative z-10">
          <div className="font-serif text-2xl text-slate-300 font-bold mb-4 transition-colors duration-300 group-hover:text-[#E07A5F]/60">
            {step}
          </div>
          <h3 className="font-serif text-xl font-bold mb-2 text-slate-900">
            {title}
          </h3>
          <p className="text-slate-600 leading-relaxed text-sm font-sans">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
  index = 0,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  index?: number;
}) {
  const { ref, visible } = useRevealOnScroll();
  const delayClass = getRevealDelayClass(index);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      } ${delayClass}`}
    >
      <div className="lp-card group relative overflow-hidden rounded-lg border border-slate-200 bg-white/80 p-8 flex flex-col gap-4 backdrop-blur-sm hover:-translate-y-2 hover:border-[#E07A5F]/45 hover:shadow-[0_26px_56px_-32px_rgba(44,62,80,0.45)]">
        <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full bg-[radial-gradient(circle,rgba(224,122,95,0.2),transparent_70%)] opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
        <div className="pointer-events-none absolute inset-0 rounded-lg">
          <div className="lp-card-sheen" />
        </div>
        <div className="relative z-10 w-10 h-10 rounded-md bg-slate-100 flex items-center justify-center border border-slate-200 transition-all duration-300 group-hover:border-[#E07A5F]/30 group-hover:bg-[#FDF3F1] lp-icon-float">
          {icon}
        </div>
        <h3 className="relative z-10 font-serif text-xl font-bold text-slate-900">
          {title}
        </h3>
        <p className="relative z-10 text-slate-600 leading-relaxed font-sans">
          {description}
        </p>
      </div>
    </div>
  );
}

// ─── PRISM Clinical Intelligence Visualization ─────────────────────────────

const VIZ_NODES = [
  { id: "DEL", label: "Delhi", x: 310, y: 95, risk: "high", cases: 4821 },
  { id: "MUM", label: "Mumbai", x: 185, y: 255, risk: "high", cases: 3934 },
  { id: "CHE", label: "Chennai", x: 290, y: 370, risk: "medium", cases: 2104 },
  { id: "KOL", label: "Kolkata", x: 460, y: 205, risk: "medium", cases: 1876 },
  { id: "BLR", label: "Bangalore", x: 245, y: 330, risk: "low", cases: 943 },
  {
    id: "HYD",
    label: "Hyderabad",
    x: 265,
    y: 295,
    risk: "medium",
    cases: 1543,
  },
  { id: "PUN", label: "Pune", x: 198, y: 290, risk: "low", cases: 712 },
  { id: "JAI", label: "Jaipur", x: 245, y: 138, risk: "medium", cases: 1102 },
  { id: "LUC", label: "Lucknow", x: 370, y: 150, risk: "high", cases: 2870 },
  { id: "AHM", label: "Ahmedabad", x: 152, y: 200, risk: "low", cases: 631 },
  { id: "BPH", label: "Bhopal", x: 298, y: 218, risk: "medium", cases: 1288 },
  { id: "PAT", label: "Patna", x: 420, y: 172, risk: "high", cases: 2450 },
];

const VIZ_EDGES = [
  ["DEL", "LUC"],
  ["DEL", "JAI"],
  ["DEL", "BPH"],
  ["LUC", "PAT"],
  ["LUC", "KOL"],
  ["PAT", "KOL"],
  ["JAI", "AHM"],
  ["JAI", "MUM"],
  ["AHM", "MUM"],
  ["MUM", "PUN"],
  ["MUM", "HYD"],
  ["PUN", "BLR"],
  ["HYD", "CHE"],
  ["HYD", "BLR"],
  ["BPH", "HYD"],
  ["BPH", "LUC"],
];

const RISK_COL: Record<string, string> = {
  high: "#E07A5F",
  medium: "#F4A261",
  low: "#2C3E50",
};
const RISK_GLOW: Record<string, string> = {
  high: "rgba(224,122,95,0.1)",
  medium: "rgba(244,162,97,0.1)",
  low: "rgba(44,62,80,0.05)",
};
const ALERT_COL: Record<string, string> = {
  HIGH: "#E07A5F",
  MED: "#F4A261",
  LOW: "#2C3E50",
};

function getVizNode(id: string) {
  return VIZ_NODES.find((n) => n.id === id)!;
}

function VizEdge({ fromId, toId }: { fromId: string; toId: string }) {
  const a = getVizNode(fromId),
    b = getVizNode(toId);
  if (!a || !b) return null;
  return (
    <path
      d={`M${a.x},${a.y} L${b.x},${b.y}`}
      stroke="#E2E8F0"
      strokeWidth="1"
      fill="none"
      opacity="0.8"
    />
  );
}

const VIZ_ALERTS = [
  { city: "Delhi", risk: "HIGH", disease: "Dengue", trend: "↑ 23%" },
  { city: "Lucknow", risk: "HIGH", disease: "Malaria", trend: "↑ 18%" },
  { city: "Patna", risk: "HIGH", disease: "Cholera", trend: "↑ 15%" },
  { city: "Mumbai", risk: "HIGH", disease: "Influenza", trend: "↑ 11%" },
  { city: "Bhopal", risk: "MED", disease: "Typhoid", trend: "↑ 7%" },
];

function PRISMVisualization(): React.ReactNode {
  const [time, setTime] = useState(() =>
    new Date().toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
    }),
  );
  useEffect(() => {
    const t = setInterval(() => {
      setTime(
        new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        }),
      );
    }, 60000);
    return () => clearInterval(t);
  }, []);

  return (
    <div
      style={{
        background: "#FAFAFA",
        fontFamily: "'Inter', sans-serif",
        fontSize: 11,
        color: "#475569",
        userSelect: "none",
      }}
    >
      {/* Header Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 16px",
          borderBottom: "1px solid #E2E8F0",
          background: "#FFFFFF",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            style={{
              color: "#0F172A",
              fontWeight: 600,
              letterSpacing: 0.5,
              fontSize: 12,
            }}
          >
            PRISM LIVE DASHBOARD
          </span>
          <span style={{ color: "#CBD5E1", fontSize: 12 }}>|</span>
          <span style={{ color: "#E07A5F", fontSize: 11, fontWeight: 500 }}>
            4 CRITICAL REPORTS
          </span>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            fontSize: 11,
            color: "#64748B",
          }}
        >
          <span style={{ fontFamily: "'Courier New', monospace" }}>
            {time} GMT
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ display: "flex", height: 358 }}>
        {/* === SVG Network Map === */}
        <div
          style={{
            flex: 1,
            position: "relative",
            overflow: "hidden",
            background: "#FAFAFA",
          }}
        >
          <svg
            viewBox="0 0 590 360"
            width="100%"
            height="100%"
            style={{ display: "block" }}
          >
            {/* Grid */}
            {[1, 2, 3, 4].map((i) => (
              <line
                key={`h${i}`}
                x1="0"
                y1={i * 72}
                x2="590"
                y2={i * 72}
                stroke="#F1F5F9"
                strokeWidth="1"
              />
            ))}
            {[1, 2, 3, 4, 5, 6, 7].map((i) => (
              <line
                key={`v${i}`}
                x1={i * 74}
                y1="0"
                x2={i * 74}
                y2="360"
                stroke="#F1F5F9"
                strokeWidth="1"
              />
            ))}

            <text
              x="16"
              y="24"
              fill="#94A3B8"
              fontSize="10"
              letterSpacing="1"
              fontWeight="500"
            >
              OPERATIONAL SECTOR 04
            </text>

            {/* Edges */}
            {VIZ_EDGES.map(([f, t], i) => (
              <VizEdge key={i} fromId={f} toId={t} />
            ))}

            {/* Nodes */}
            {VIZ_NODES.map((node) => (
              <g key={node.id} transform={`translate(${node.x},${node.y})`}>
                <circle r="16" fill={RISK_GLOW[node.risk]} />
                <circle r="6" fill={RISK_COL[node.risk]} />
                <circle r="2" fill="#FFFFFF" />
                <rect
                  x="-18"
                  y="14"
                  width="36"
                  height="14"
                  rx="2"
                  fill="#FFFFFF"
                  stroke="#E2E8F0"
                  strokeWidth="1"
                />
                <text
                  x="0"
                  y="24"
                  textAnchor="middle"
                  fill="#334155"
                  fontSize="8"
                  fontWeight="600"
                >
                  {node.id}
                </text>
              </g>
            ))}
          </svg>
        </div>

        {/* === Right Panel === */}
        <div
          style={{
            width: 200,
            borderLeft: "1px solid #E2E8F0",
            background: "#FFFFFF",
            display: "flex",
            flexDirection: "column",
          }}
        >
          {/* Active Alerts */}
          <div
            style={{
              flex: 1,
              padding: "16px",
              borderBottom: "1px solid #E2E8F0",
              overflowY: "auto",
            }}
          >
            <div
              style={{
                color: "#0F172A",
                fontWeight: 600,
                fontSize: 10,
                marginBottom: 12,
              }}
            >
              RECENT ALERTS
            </div>
            {VIZ_ALERTS.map((a, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  padding: "6px 0",
                  borderBottom: "1px solid #F1F5F9",
                }}
              >
                <span
                  style={{
                    width: 6,
                    height: 6,
                    borderRadius: "2px",
                    background: ALERT_COL[a.risk],
                    flexShrink: 0,
                  }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{ color: "#334155", fontWeight: 600, fontSize: 11 }}
                  >
                    {a.city}
                  </div>
                  <div style={{ color: "#64748B", fontSize: 10 }}>
                    {a.disease}
                  </div>
                </div>
                <span
                  style={{ color: "#0F172A", fontSize: 10, fontWeight: 500 }}
                >
                  {a.trend}
                </span>
              </div>
            ))}
          </div>

          {/* System Status */}
          <div style={{ padding: "16px" }}>
            <div
              style={{
                color: "#0F172A",
                fontWeight: 600,
                fontSize: 10,
                marginBottom: 10,
              }}
            >
              SYSTEM STATUS
            </div>
            {[
              { label: "Data Ingestion", ok: true },
              { label: "ARIMA Modeling", ok: true },
              { label: "Report Generation", ok: true },
            ].map((s, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 6,
                }}
              >
                <span style={{ fontSize: 11, color: "#64748B" }}>
                  {s.label}
                </span>
                <span
                  style={{ fontSize: 10, color: "#0F172A", fontWeight: 500 }}
                >
                  ACTIVE
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Metrics Bar */}
      <div
        style={{
          display: "flex",
          borderTop: "1px solid #E2E8F0",
          background: "#FFFFFF",
        }}
      >
        {[
          { label: "DAILY INTAKE", value: "14,580", sub: "+2% wk" },
          { label: "STATION DEPLOYMENT", value: "420", sub: "active units" },
          { label: "RISK INDEX", value: "7.4", sub: "ELEVATED" },
          { label: "SECTOR COVERAGE", value: "100%", sub: "NOMINAL" },
        ].map((m, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRight: i < 3 ? "1px solid #E2E8F0" : "none",
            }}
          >
            <div
              style={{
                color: "#64748B",
                fontSize: 9,
                fontWeight: 500,
                marginBottom: 4,
              }}
            >
              {m.label}
            </div>
            <div
              style={{
                color: "#0F172A",
                fontSize: 16,
                borderBottom: "1px solid transparent",
                fontFamily: "'Courier New', monospace",
              }}
            >
              {m.value}
            </div>
            <div style={{ color: "#94A3B8", fontSize: 10 }}>{m.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
