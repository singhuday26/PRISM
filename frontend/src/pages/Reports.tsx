import { useState, useEffect } from 'react';
import { FileText, Download, RefreshCw, Plus, Clock, AlertCircle } from 'lucide-react';
import { listReports, generateReport, type ReportItem } from '../lib/api';

export function Reports() {
    const [reports, setReports] = useState<ReportItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const [newReportType, setNewReportType] = useState('weekly_summary');
    const [newReportDisease, setNewReportDisease] = useState('DENGUE');

    const fetchReports = async () => {
        setLoading(true);
        try {
            const data = await listReports(undefined, undefined, 50);
            setReports(data.reports);
            setError(null);
        } catch (err) {
            setError("Failed to load reports");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
    }, []);

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await generateReport(
                newReportType as any,
                undefined, // specific region not implemented in simple UI yet
                newReportDisease
            );
            // Poll for update or just reload after a delay
            setTimeout(fetchReports, 2000);
        } catch (err: any) {
            setError(err.message || "Failed to generate report");
        } finally {
            setGenerating(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ready': return 'text-emerald-400 bg-emerald-400/10';
            case 'generating': return 'text-blue-400 bg-blue-400/10';
            case 'failed': return 'text-red-400 bg-red-400/10';
            default: return 'text-gray-400 bg-gray-400/10';
        }
    };

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Reports</h1>
                    <p className="text-gray-400">Automated situation reports and summaries.</p>
                </div>
                <button
                    onClick={fetchReports}
                    className="p-2 bg-white/5 rounded hover:bg-white/10 transition-colors"
                >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Generator */}
            <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Generate New Report</h3>
                <div className="flex flex-wrap gap-4 items-end">
                    <div className="space-y-1">
                        <label className="text-xs text-gray-400 uppercase">Type</label>
                        <select
                            value={newReportType}
                            onChange={(e) => setNewReportType(e.target.value)}
                            className="block w-48 bg-black/30 border border-white/10 rounded px-3 py-2 text-white"
                        >
                            <option value="weekly_summary">Weekly Summary</option>
                            <option value="disease_overview">Disease Overview</option>
                        </select>
                    </div>
                    <div className="space-y-1">
                        <label className="text-xs text-gray-400 uppercase">Disease</label>
                        <select
                            value={newReportDisease}
                            onChange={(e) => setNewReportDisease(e.target.value)}
                            className="block w-48 bg-black/30 border border-white/10 rounded px-3 py-2 text-white"
                        >
                            <option value="DENGUE">Dengue</option>
                            <option value="MALARIA">Malaria</option>
                            <option value="CHIKUNGUNYA">Chikungunya</option>
                        </select>
                    </div>
                    <button
                        onClick={handleGenerate}
                        disabled={generating}
                        className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded text-white font-medium transition-colors"
                    >
                        {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                        Generate
                    </button>
                </div>
                {error && (
                    <div className="mt-4 text-sm text-red-400 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4" />
                        {error}
                    </div>
                )}
            </div>

            {/* Report List */}
            <div className="glass-card p-0 overflow-hidden">
                <div className="p-4 border-b border-white/10 bg-white/5">
                    <h3 className="font-semibold text-white">Recent Reports</h3>
                </div>
                <div className="divide-y divide-white/5">
                    {reports.length === 0 && !loading ? (
                        <div className="p-8 text-center text-gray-500">
                            No reports found. Generate one to get started.
                        </div>
                    ) : (
                        reports.map((report) => (
                            <div key={report.report_id} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors">
                                <div className="flex items-start gap-3">
                                    <div className={`p-2 rounded-lg ${getStatusColor(report.status)}`}>
                                        <FileText className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="font-medium text-white capitalize">
                                            {report.type.replace('_', ' ')}
                                        </div>
                                        <div className="text-sm text-gray-400 flex items-center gap-2">
                                            <span>{report.disease}</span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Clock className="w-3 h-3" />
                                                {new Date(report.generated_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {report.status === 'ready' && (
                                    <a
                                        href={`/api/reports/${report.report_id}/download`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        download
                                        className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full transition-colors"
                                        title="Download PDF"
                                    >
                                        <Download className="w-5 h-5" />
                                    </a>
                                )}
                                {report.status === 'generating' && (
                                    <div className="px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 animate-pulse">
                                        Generating...
                                    </div>
                                )}
                                {report.status === 'failed' && (
                                    <div className="px-3 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400">
                                        Failed
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
