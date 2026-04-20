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
    fetchTaskStatus,
    type PipelineTaskStatus,
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
    const [taskStatus, setTaskStatus] = useState<PipelineTaskStatus | null>(null);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);
    const [steps, setSteps] = useState<StepDisplay[]>([]);
    const pollingInterval = useRef<ReturnType<typeof setInterval> | null>(null);
    const collapseTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    /* Auto-collapse after 20s of done/idle */
    useEffect(() => {
        if (panelState === "done") {
            collapseTimer.current = setTimeout(() => setExpanded(false), 20_000);
        }
        return () => {
            if (collapseTimer.current) clearTimeout(collapseTimer.current);
            if (pollingInterval.current) clearInterval(pollingInterval.current);
        };
    }, [panelState]);

    const pollStatus = useCallback(async (taskId: string) => {
        try {
            const status = await fetchTaskStatus(taskId);
            setTaskStatus(status);

            // Reconcile steps
            const resSteps = status.steps ?? [];
            const updatedSteps: StepDisplay[] = STEP_ORDER.map((name) => {
                const real = resSteps.find((s) => s.name === name);
                
                let uiState: StepDisplay["uiState"] = "pending";
                if (real) {
                    if (real.status === "success") uiState = "success";
                    else if (real.status === "skipped") uiState = "skipped";
                    else if (real.status === "error") uiState = "error";
                } else if (status.status === "processing") {
                    // If this is the next step after the last success, mark as running
                    const lastSuccessIdx = resSteps.length - 1;
                    const currentStepIdx = STEP_ORDER.indexOf(name);
                    if (currentStepIdx === lastSuccessIdx + 1) {
                        uiState = "running";
                    }
                }

                return { name, uiState, result: real };
            });
            setSteps(updatedSteps);

            if (status.status === "completed") {
                if (pollingInterval.current) clearInterval(pollingInterval.current);
                setPanelState("done");
                onComplete?.();
            } else if (status.status === "failed") {
                if (pollingInterval.current) clearInterval(pollingInterval.current);
                setPanelState("error");
                setErrorMsg(status.error || "Background task failed");
            }
        } catch (e) {
            console.error("Polling error:", e);
            // We don't stop polling on a single fetch error (transient network issue)
        }
    }, [onComplete]);

    const execute = async () => {
        setPanelState("running");
        setExpanded(true);
        setErrorMsg(null);
        setTaskStatus(null);
        
        const initialSteps: StepDisplay[] = STEP_ORDER.map((name) => ({
            name,
            uiState: "pending",
        }));
        setSteps(initialSteps);

        try {
            const { task_id } = await apiRunPipeline(disease);
            
            // Start polling
            if (pollingInterval.current) clearInterval(pollingInterval.current);
            pollingInterval.current = setInterval(() => pollStatus(task_id), 1500);
            
            // Initial poll immediately
            pollStatus(task_id);
        } catch (e: unknown) {
            setErrorMsg(e instanceof Error ? e.message : "Failed to start pipeline");
            setPanelState("error");
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
                    <div className="w-5 h-5 rounded-full border-2 border-slate-200" />
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
                    className="flex items-center gap-2 px-4 py-2 bg-[#E07A5F] hover:bg-[#D9664A] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-all duration-200 active:scale-95"
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
                {!expanded && panelState === "done" && taskStatus && (
                    <button
                        onClick={() => setExpanded(true)}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors cursor-pointer"
                    >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Pipeline completed in {taskStatus.duration_seconds}s
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
                <div className="bg-white/60 backdrop-blur-md rounded-xl border border-slate-200 overflow-hidden animate-in slide-in-from-top-2 duration-300">
                    {/* Header */}
                    <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200 bg-[#FAFAFA]">
                        <div className="flex items-center gap-3">
                            <Database className="w-4 h-4 text-slate-700" />
                            <span className="text-sm font-semibold text-slate-900">
                                Pipeline Execution
                            </span>
                            <span className="text-xs text-gray-500 font-mono">
                                {disease}
                            </span>
                        </div>
                        <div className="flex items-center gap-3">
                            {taskStatus?.duration_seconds && (
                                <span className="flex items-center gap-1.5 text-xs text-gray-400">
                                    <Clock className="w-3 h-3" />
                                    {taskStatus.duration_seconds}s total
                                </span>
                            )}
                            <button
                                onClick={() => setExpanded(false)}
                                className="text-slate-500 hover:text-slate-800 transition-colors p-1 rounded-md hover:bg-slate-100"
                            >
                                <ChevronUp className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Steps */}
                    <div className="divide-y divide-slate-100 bg-[#FAFAFA]">
                        {steps.map((step) => {
                            const meta = STEP_META[step.name];
                            return (
                                <div
                                    key={step.name}
                                    className={`px-5 py-3.5 flex items-center gap-4 transition-colors duration-300 ${step.uiState === "running"
                                        ? "bg-slate-50"
                                        : step.uiState === "error"
                                            ? "bg-red-50"
                                            : ""
                                        }`}
                                >
                                    {/* Status icon */}
                                    <div className="flex-shrink-0">
                                        {renderStepIcon(step.uiState)}
                                    </div>

                                    {/* Step icon + label */}
                                    <div className="flex-shrink-0 p-1.5 rounded-md bg-slate-200/50 text-slate-500">
                                        {meta?.icon}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span
                                                className={`text-sm font-medium ${step.uiState === "skipped"
                                                    ? "text-slate-400"
                                                    : "text-slate-900"
                                                    }`}
                                            >
                                                {meta?.label ?? step.name}
                                            </span>
                                            {step.uiState === "skipped" && (
                                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 font-medium uppercase tracking-wide">
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
                                                <span className="text-xs px-2 py-1 rounded-md bg-slate-100 text-slate-500 font-mono tabular-nums">
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
                    {taskStatus && panelState === "done" && (
                        <div className="px-5 py-3 bg-emerald-500/[0.03] border-t border-emerald-500/10 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-xs text-emerald-400 font-medium">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                Pipeline completed successfully
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-400">
                                {taskStatus.steps.map(s => {
                                    if (s.name === 'reset' || s.status !== 'success') return null;
                                    return (
                                        <span key={s.name}>
                                            <strong className="text-slate-800 font-mono">
                                                {s.records_created}
                                            </strong>{" "}
                                            {s.name.replace('_', ' ')}
                                        </span>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
