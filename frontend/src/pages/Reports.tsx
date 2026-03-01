import { useState, useEffect, useCallback } from "react";
import {
  FileText,
  Download,
  RefreshCw,
  Plus,
  Clock,
  AlertCircle,
  BarChart2
} from "lucide-react";
import {
  listReports,
  generateReport,
  fetchDiseases,
  type ReportItem,
  type DiseaseInfo,
} from "../lib/api";
import { useToast } from "../context/ToastContext";
import { Skeleton } from "../components/ui/Skeleton";

export function Reports() {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const [newReportType, setNewReportType] = useState("weekly_summary");
  const [newReportDisease, setNewReportDisease] = useState("DENGUE");
  const [diseases, setDiseases] = useState<DiseaseInfo[]>([]);
  const { error, success, info } = useToast();

  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listReports(undefined, undefined, 50);
      setReports(data.reports);
    } catch {
      error("Failed to load reports. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [error]);

  useEffect(() => {
    fetchReports();
    fetchDiseases()
      .then((d) => setDiseases(d.diseases))
      .catch((err) => {
        console.error(err);
        error("Failed to load diseases for report generator.");
      });
  }, [error, fetchReports]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generateReport(
        newReportType as
        | "weekly_summary"
        | "region_detail"
        | "disease_overview",
        undefined, // specific region not implemented in simple UI yet
        newReportDisease,
      );
      success("Report generation started successfully!");
      // Poll for update or just reload after a delay
      setTimeout(fetchReports, 2000);
    } catch (err: unknown) {
      error(
        err instanceof Error ? err.message : "Failed to generate report",
      );
    } finally {
      setGenerating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "ready":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "generating":
        return "text-blue-400 bg-blue-500/10 border-blue-500/20";
      case "failed":
        return "text-red-400 bg-red-500/10 border-red-500/20";
      default:
        return "text-gray-400 bg-gray-500/10 border-gray-500/20";
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Reports</h1>
          <p className="text-gray-400">
            Automated situation reports and summaries.
          </p>
        </div>
        <button
          onClick={fetchReports}
          disabled={loading}
          className="flex items-center gap-2 p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors disabled:opacity-50 text-gray-300"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span className="text-sm font-medium">Refresh List</span>
        </button>
      </div>

      {/* Generator */}
      <div className="glass-card p-6 border border-white/5 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <BarChart2 className="w-5 h-5 text-purple-400" />
          Generate New Report
        </h3>
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="space-y-2 flex-1 sm:flex-none">
            <label className="text-xs text-gray-400 uppercase font-medium">Report Type</label>
            <select
              value={newReportType}
              onChange={(e) => setNewReportType(e.target.value)}
              className="block w-full sm:w-64 bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500/40 focus:outline-none transition-shadow"
            >
              <option value="weekly_summary">Weekly Summary</option>
              <option value="disease_overview">Disease Overview</option>
            </select>
          </div>
          <div className="space-y-2 flex-1 sm:flex-none">
            <label className="text-xs text-gray-400 uppercase font-medium">Target Disease</label>
            <select
              value={newReportDisease}
              onChange={(e) => setNewReportDisease(e.target.value)}
              className="block w-full sm:w-64 bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white focus:ring-2 focus:ring-blue-500/40 focus:outline-none transition-shadow"
            >
              {diseases.map((d) => (
                <option key={d.disease_id} value={d.disease_id} className="bg-gray-900">
                  {d.name}
                </option>
              ))}
              {diseases.length === 0 && (
                <option value="DENGUE" className="bg-gray-900">Dengue Fever</option>
              )}
            </select>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors"
          >
            {generating ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            Generate Report
          </button>
        </div>
      </div>

      {/* Report List */}
      <div className="glass-card overflow-hidden border border-white/5 rounded-xl">
        <div className="p-4 border-b border-white/10 bg-white/[0.02]">
          <h3 className="font-semibold text-white">Report Archives</h3>
        </div>

        {loading && reports.length === 0 ? (
          <div className="p-4 space-y-4">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center text-gray-500 flex flex-col items-center">
            <FileText className="w-12 h-12 text-gray-600 mb-4 opacity-50" />
            <p className="font-medium text-gray-400">No reports found.</p>
            <p className="text-sm mt-1">Generate a new report using the form above.</p>
          </div>
        ) : (
          <div className="divide-y divide-white/5">
            {reports.map((report) => (
              <div
                key={report.report_id}
                className="p-4 flex items-center justify-between hover:bg-white/[0.02] transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2.5 rounded-lg border ${getStatusColor(report.status)}`}>
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-medium text-white capitalize">
                      {report.type.replaceAll("_", " ")}
                    </div>
                    <div className="text-xs text-gray-400 flex items-center gap-2 mt-1">
                      <span className="uppercase tracking-wider font-semibold text-indigo-300">{report.disease}</span>
                      <span className="text-gray-600">•</span>
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        {new Date(report.generated_at).toLocaleString(undefined, {
                          dateStyle: 'medium',
                          timeStyle: 'short'
                        })}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  {report.status === "ready" && (
                    <a
                      href={`/api/reports/${report.report_id}/download`}
                      target="_blank"
                      rel="noopener noreferrer"
                      download
                      className="p-2.5 text-blue-400 hover:text-white bg-blue-500/10 hover:bg-blue-500 border border-blue-500/20 rounded-lg transition-all shadow-sm"
                      title="Download PDF"
                      onClick={() => info(`Downloading ${report.type} report...`)}
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  )}
                  {report.status === "generating" && (
                    <div className="px-3 py-1.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-2 shadow-inner">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
                      Generating
                    </div>
                  )}
                  {report.status === "failed" && (
                    <div className="px-3 py-1.5 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20 flex items-center gap-1.5 shadow-inner">
                      <AlertCircle className="w-3.5 h-3.5" />
                      Failed
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
