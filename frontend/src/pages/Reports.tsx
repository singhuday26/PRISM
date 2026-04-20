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
  buildApiPath,
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
        return "text-emerald-600 bg-emerald-50 border-emerald-100";
      case "generating":
        return "text-blue-600 bg-blue-50 border-blue-100";
      case "failed":
        return "text-red-600 bg-red-50 border-red-100";
      default:
        return "text-slate-500 bg-slate-50 border-slate-200";
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-800 mb-2">Reports</h1>
          <p className="text-slate-500">
            Automated situation reports and summaries.
          </p>
        </div>
        <button
          onClick={fetchReports}
          disabled={loading}
          className="flex items-center gap-2 p-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50 text-slate-600 shadow-sm"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          <span className="text-sm font-medium">Refresh List</span>
        </button>
      </div>

      {/* Generator */}
      <div className="bg-white/60 backdrop-blur-md p-6 border border-slate-200 rounded-xl shadow-sm">
        <h3 className="text-lg font-serif font-bold text-slate-800 mb-6 flex items-center gap-2">
          <BarChart2 className="w-5 h-5 text-purple-500" />
          Generate New Report
        </h3>
        <div className="flex flex-col sm:flex-row gap-4 items-end">
          <div className="space-y-2 flex-1 sm:flex-none">
            <label className="text-xs text-slate-500 uppercase font-medium tracking-wider">Report Type</label>
            <select
              value={newReportType}
              onChange={(e) => setNewReportType(e.target.value)}
              className="block w-full sm:w-64 bg-white border border-slate-200 rounded-lg px-3 py-2.5 text-slate-800 focus:ring-2 focus:ring-[#E07A5F]/40 focus:outline-none transition-shadow shadow-sm"
            >
              <option value="weekly_summary">Weekly Summary</option>
              <option value="disease_overview">Disease Overview</option>
            </select>
          </div>
          <div className="space-y-2 flex-1 sm:flex-none">
            <label className="text-xs text-slate-500 uppercase font-medium tracking-wider">Target Disease</label>
            <select
              value={newReportDisease}
              onChange={(e) => setNewReportDisease(e.target.value)}
              className="block w-full sm:w-64 bg-white border border-slate-200 rounded-lg px-3 py-2.5 text-slate-800 focus:ring-2 focus:ring-[#E07A5F]/40 focus:outline-none transition-shadow shadow-sm"
            >
              {diseases.map((d) => (
                <option key={d.disease_id} value={d.disease_id}>
                  {d.name}
                </option>
              ))}
              {diseases.length === 0 && (
                <option value="DENGUE">Dengue Fever</option>
              )}
            </select>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-2.5 bg-[#E07A5F] hover:bg-[#D9664A] disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-colors shadow-sm"
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
      <div className="bg-white/60 backdrop-blur-md overflow-hidden border border-slate-200 rounded-xl shadow-sm">
        <div className="p-4 border-b border-slate-200 bg-[#FAFAFA]">
          <h3 className="font-semibold text-slate-800">Report Archives</h3>
        </div>

        {loading && reports.length === 0 ? (
          <div className="p-4 space-y-4">
            <Skeleton className="h-16 w-full bg-slate-100" />
            <Skeleton className="h-16 w-full bg-slate-100" />
            <Skeleton className="h-16 w-full bg-slate-100" />
          </div>
        ) : reports.length === 0 ? (
          <div className="p-12 text-center text-slate-500 flex flex-col items-center">
            <FileText className="w-12 h-12 text-slate-300 mb-4" />
            <p className="font-medium text-slate-500">No reports found.</p>
            <p className="text-sm mt-1 text-slate-400">Generate a new report using the form above.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {reports.map((report) => (
              <div
                key={report.report_id}
                className="p-4 flex items-center justify-between hover:bg-slate-50 transition-colors bg-white"
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2.5 rounded-lg border ${getStatusColor(report.status)}`}>
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-800 capitalize">
                      {report.type.replaceAll("_", " ")}
                    </div>
                    <div className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                      <span className="uppercase tracking-wider font-semibold text-indigo-600">{report.disease}</span>
                      <span className="text-slate-300">•</span>
                      <span className="flex items-center gap-1.5 font-mono">
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
                      href={buildApiPath(`/reports/${report.report_id}/download`)}
                      target="_blank"
                      rel="noopener noreferrer"
                      download
                      className="p-2.5 text-blue-600 hover:text-white bg-blue-50 hover:bg-blue-600 border border-blue-200 rounded-lg transition-all shadow-sm"
                      title="Download PDF"
                      onClick={() => info(`Downloading ${report.type} report...`)}
                    >
                      <Download className="w-4 h-4" />
                    </a>
                  )}
                  {report.status === "generating" && (
                    <div className="px-3 py-1.5 rounded-full text-xs font-medium bg-blue-50 text-blue-600 border border-blue-100 flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                      Generating
                    </div>
                  )}
                  {report.status === "failed" && (
                    <div className="px-3 py-1.5 rounded-full text-xs font-medium bg-red-50 text-red-600 border border-red-100 flex items-center gap-1.5">
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
