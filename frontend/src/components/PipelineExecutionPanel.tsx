import { useState, useEffect, useRef, useCallback } from "react";
import {
    Play,
    RefreshCw,
    CheckCircle2,
    XCircle,
    SkipForward,
    Clock,
    ChevronDown,
    ChevronUp,
    Shield,
    Bell,
    TrendingUp,
    Trash2,
    Database,
} from "lucide-react";
import {
    runPipeline as apiRunPipeline,
    type PipelineRunResponse,
    type PipelineStepResult,
} from "../lib/api";

/* ─── Step metadata ───────────────────────────────────────────────────── */

const STEP_META: Record<
    string,
    { label: string; icon: React.ReactNode; description: string }
> = {
    reset: {
        label: "Reset Data",
        icon: <Trash2 className="w-4 h-4" />,
        description: "Clear existing derived data for this disease",
    },
    risk_scores: {
        label: "Risk Scores",
        icon: <Shield className="w-4 h-4" />,
        description: "Compute risk scores across all monitored regions",
    },
    alerts: {
        label: "Alert Generation",
        icon: <Bell className="w-4 h-4" />,
        description: "Generate alerts for regions exceeding risk thresholds",
    },
    forecasts: {
        label: "ARIMA Forecasting",
        icon: <TrendingUp className="w-4 h-4" />,
        description: "Fit ARIMA models and produce multi-day forecasts",
    },
};

const STEP_ORDER = ["reset", "risk_scores", "alerts", "forecasts"];

/* ─── Types ───────────────────────────────────────────────────────────── */

type PanelState = "idle" | "running" | "done" | "error";

interface StepDisplay {
    name: string;
    uiState: "pending" | "running" | "success" | "error" | "skipped";
    result?: PipelineStepResult;
}

/* ─── Component ───────────────────────────────────────────────────────── */

interface PipelineExecutionPanelProps {
    disease: string;
    onComplete?: () => void;
}

export default function PipelineExecutionPanel({
    disease,
    onComplete,
}: PipelineExecutionPanelProps) {
    const [panelState, setPanelState] = useState<PanelState>("idle");
    const [expanded, setExpanded] = useState(false);
    const [response, setResponse] = useState<PipelineRunResponse | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const [steps, setSteps] = useState<StepDisplay[]>([]);
    const [currentStepIdx, setCurrentStepIdx] = useState(-1);
    const collapseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    /* Auto-collapse after 20s of done/idle */
    useEffect(() => {
        if (panelState === "done") {
            collapseTimer.current = setTimeout(() => setExpanded(false), 20_000);
        }
        return () => {
            if (collapseTimer.current) clearTimeout(collapseTimer.current);
        };
    }, [panelState]);

    /* Simulate step progression while waiting for the API */
    const animateSteps = useCallback(async () => {
        const initial: StepDisplay[] = STEP_ORDER.map((name) => ({
            name,
            uiState: "pending",
        }));
        setSteps(initial);

        for (let i = 0; i < STEP_ORDER.length; i++) {
            setCurrentStepIdx(i);
            setSteps((prev) =>
                prev.map((s, idx) => (idx === i ? { ...s, uiState: "running" } : s)),
            );
            // Hold each step visible for at least 600ms for UX
            await new Promise((r) => setTimeout(r, 600));
        }
    }, []);

    const execute = async () => {
        setPanelState("running");
        setExpanded(true);
        setErrorMsg(null);
        setResponse(null);
        setCurrentStepIdx(-1);

        // Start step animation (fire-and-forget — we'll reconcile with real data)
        const animationDone = animateSteps();

        try {
            const res = await apiRunPipeline(disease);
            await animationDone; // wait for animation to finish

            // Reconcile steps with real data (defensive: handle missing steps array)
            const resSteps = res.steps ?? [];
            const finalSteps: StepDisplay[] = STEP_ORDER.map((name) => {
                const real = resSteps.find((s) => s.name === name);
                return {
                    name,
                    uiState: real?.status === "success"
                        ? "success"
                        : real?.status === "skipped"
                            ? "skipped"
                            : real?.status === "error"
                                ? "error"
                                : "success",
                    result: real,
                };
            });
            setSteps(finalSteps);
            setResponse(res);
            setPanelState(res.success ? "done" : "error");
            setCurrentStepIdx(-1);
            onComplete?.();
        } catch (e: unknown) {
            await animationDone;
            setErrorMsg(e instanceof Error ? e.message : "Unknown error");
            setPanelState("error");
            // Mark remaining steps as error
            setSteps((prev) =>
                prev.map((s) =>
                    s.uiState === "running" || s.uiState === "pending"
                        ? { ...s, uiState: "error" }
                        : s,
                ),
            );
        }
    };

    /* ─── Step row rendering ─────────────────────────────────────── */

    const renderStepIcon = (state: StepDisplay["uiState"]) => {
        switch (state) {
            case "running":
                return (
                    <div className="w-5 h-5 flex items-center justify-center">
                        <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />
                    </div>
                );
            case "success":
                return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
            case "error":
                return <XCircle className="w-5 h-5 text-red-400" />;
            case "skipped":
                return <SkipForward className="w-5 h-5 text-gray-500" />;
            default:
                return (
                    <div className="w-5 h-5 rounded-full border-2 border-white/10" />
                );
        }
    };

    const formatDuration = (ms: number) => {
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    };

    return (
        <div className="space-y-3">
            {/* ── Trigger Button ───────────────────────────────────────── */}
            <div className="flex items-center gap-3">
                <button
                    onClick={execute}
                    disabled={panelState === "running"}
                    className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-all duration-200 active:scale-95"
                    title="Run analytics pipeline"
                >
                    {panelState === "running" ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                        <Play className="w-4 h-4" />
                    )}
                    <span className="hidden sm:inline">
                        {panelState === "running" ? "Running…" : "Pipeline"}
                    </span>
                </button>

                {/* Compact status badge when collapsed */}
                {!expanded && panelState === "done" && response && (
                    <button
                        onClick={() => setExpanded(true)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors cursor-pointer"
                    >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Pipeline completed in {response.duration_seconds}s
                        <ChevronDown className="w-3 h-3 ml-1" />
                    </button>
                )}

                {!expanded && panelState === "error" && (
                    <button
                        onClick={() => setExpanded(true)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors cursor-pointer"
                    >
                        <XCircle className="w-3.5 h-3.5" />
                        Pipeline had errors — click for details
                        <ChevronDown className="w-3 h-3 ml-1" />
                    </button>
                )}
            </div>

            {/* ── Expanded Panel ───────────────────────────────────────── */}
            {expanded && panelState !== "idle" && (
                <div className="glass-card rounded-xl border border-white/5 overflow-hidden animate-in slide-in-from-top-2 duration-300">
                    {/* Header */}
                    <div className="flex items-center justify-between px-5 py-3 border-b border-white/5 bg-white/[0.02]">
                        <div className="flex items-center gap-3">
                            <Database className="w-4 h-4 text-indigo-400" />
                            <span className="text-sm font-semibold text-white">
                                Pipeline Execution
                            </span>
                            <span className="text-xs text-gray-500 font-mono">
                                {disease}
                            </span>
                        </div>
                        <div className="flex items-center gap-3">
                            {response && (
                                <span className="flex items-center gap-1.5 text-xs text-gray-400">
                                    <Clock className="w-3 h-3" />
                                    {response.duration_seconds}s total
                                </span>
                            )}
                            <button
                                onClick={() => setExpanded(false)}
                                className="text-gray-500 hover:text-gray-300 transition-colors p-1 rounded-md hover:bg-white/5"
                            >
                                <ChevronUp className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Steps */}
                    <div className="divide-y divide-white/[0.03]">
                        {steps.map((step, idx) => {
                            const meta = STEP_META[step.name];
                            const isActive = idx === currentStepIdx;
                            return (
                                <div
                                    key={step.name}
                                    className={`px-5 py-3.5 flex items-center gap-4 transition-colors duration-300 ${isActive
                                        ? "bg-indigo-500/5"
                                        : step.uiState === "error"
                                            ? "bg-red-500/5"
                                            : ""
                                        }`}
                                >
                                    {/* Status icon */}
                                    <div className="flex-shrink-0">
                                        {renderStepIcon(step.uiState)}
                                    </div>

                                    {/* Step icon + label */}
                                    <div className="flex-shrink-0 p-1.5 rounded-md bg-white/5 text-gray-400">
                                        {meta?.icon}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span
                                                className={`text-sm font-medium ${step.uiState === "skipped"
                                                    ? "text-gray-500"
                                                    : "text-white"
                                                    }`}
                                            >
                                                {meta?.label ?? step.name}
                                            </span>
                                            {step.uiState === "skipped" && (
                                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-500 font-medium uppercase tracking-wide">
                                                    Skipped
                                                </span>
                                            )}
                                        </div>
                                        {step.result?.detail && (
                                            <p
                                                className={`text-xs mt-0.5 ${step.uiState === "error"
                                                    ? "text-red-400/80"
                                                    : "text-gray-500"
                                                    }`}
                                            >
                                                {step.result.detail}
                                            </p>
                                        )}
                                        {!step.result && step.uiState === "pending" && (
                                            <p className="text-xs mt-0.5 text-gray-600">
                                                {meta?.description}
                                            </p>
                                        )}
                                    </div>

                                    {/* Metrics */}
                                    <div className="flex items-center gap-3 flex-shrink-0">
                                        {step.result &&
                                            step.uiState === "success" &&
                                            step.name !== "reset" && (
                                                <span className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-mono tabular-nums">
                                                    +{step.result.records_created}
                                                </span>
                                            )}
                                        {step.result &&
                                            step.uiState === "success" &&
                                            step.result.total_records > 0 && (
                                                <span className="text-xs px-2 py-1 rounded-md bg-white/5 text-gray-400 font-mono tabular-nums">
                                                    {step.result.total_records.toLocaleString()} total
                                                </span>
                                            )}
                                        {step.result && step.result.duration_ms > 0 && (
                                            <span className="text-xs text-gray-500 font-mono tabular-nums w-14 text-right">
                                                {formatDuration(step.result.duration_ms)}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Error banner */}
                    {errorMsg && (
                        <div className="px-5 py-3 bg-red-500/10 border-t border-red-500/20">
                            <p className="text-xs text-red-400 font-medium">{errorMsg}</p>
                        </div>
                    )}

                    {/* Footer summary */}
                    {response && panelState === "done" && (
                        <div className="px-5 py-3 bg-emerald-500/[0.03] border-t border-emerald-500/10 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                Pipeline completed successfully
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-400">
                                <span>
                                    <strong className="text-white font-mono">
                                        {response.created.risk_scores}
                                    </strong>{" "}
                                    risk
                                </span>
                                <span>
                                    <strong className="text-white font-mono">
                                        {response.created.alerts}
                                    </strong>{" "}
                                    alerts
                                </span>
                                <span>
                                    <strong className="text-white font-mono">
                                        {response.created.forecasts}
                                    </strong>{" "}
                                    forecasts
                                </span>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
