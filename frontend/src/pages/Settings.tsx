import { useState, useEffect } from "react";
import { Bell, Save, CheckCircle, AlertCircle, Mail } from "lucide-react";
import { subscribe, fetchDiseases, type DiseaseInfo } from "../lib/api";

export function Settings() {
  const [email, setEmail] = useState("");
  const [diseases, setDiseases] = useState<string[]>(["DENGUE"]);
  const [minRisk, setMinRisk] = useState("HIGH");
  const [allDiseases, setAllDiseases] = useState<DiseaseInfo[]>([]);

  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchDiseases()
      .then((d) => setAllDiseases(d.diseases))
      .catch(console.error);
  }, []);

  const handleSave = async () => {
    if (!email) {
      setStatus("error");
      setMessage("Email is required");
      return;
    }

    setSaving(true);
    setStatus("idle");

    try {
      await subscribe({
        email,
        diseases,
        min_risk_level: minRisk as "MEDIUM" | "HIGH" | "CRITICAL",
        regions: [], // All regions for now
        frequency: "immediate",
      });
      setStatus("success");
      setTimeout(() => setStatus("idle"), 3000);
    } catch (err: unknown) {
      setStatus("error");
      setMessage(
        err instanceof Error ? err.message : "Failed to update settings",
      );
    } finally {
      setSaving(false);
    }
  };

  const toggleDisease = (d: string) => {
    if (diseases.includes(d)) {
      setDiseases(diseases.filter((x) => x !== d));
    } else {
      setDiseases([...diseases, d]);
    }
  };

  return (
    <div className="space-y-8 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">
          Manage your preferences and notifications.
        </p>
      </div>

      <div className="glass-card p-8">
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-white/10">
          <Bell className="w-6 h-6 text-blue-400" />
          <h2 className="text-lg font-semibold text-white">Notifications</h2>
        </div>

        <div className="space-y-6">
          {/* Email Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300 flex items-center gap-2">
              <Mail className="w-4 h-4" />
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="officer@prism.org"
              className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500/50 transition-colors"
            />
            <p className="text-xs text-gray-500">
              We'll send alerts to this address.
            </p>
          </div>

          {/* Risk Threshold */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Minimum Risk Level
            </label>
            <div className="grid grid-cols-3 gap-2">
              {["MEDIUM", "HIGH", "CRITICAL"].map((level) => (
                <button
                  key={level}
                  onClick={() => setMinRisk(level)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                    minRisk === level
                      ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-900/20"
                      : "bg-white/5 border-transparent text-gray-400 hover:bg-white/10"
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Diseases */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Monitored Diseases
            </label>
            <div className="space-y-2">
              {(allDiseases.length > 0
                ? allDiseases.map((d) => d.disease_id)
                : ["DENGUE", "MALARIA", "CHIKUNGUNYA"]
              ).map((d) => (
                <label
                  key={d}
                  className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5 cursor-pointer hover:border-white/20 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={diseases.includes(d)}
                    onChange={() => toggleDisease(d)}
                    className="w-4 h-4 rounded border-gray-600 text-blue-600 focus:ring-blue-500 bg-gray-700"
                  />
                  <span className="text-white capitalize">
                    {d.toLowerCase()}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="pt-4 flex items-center justify-between">
            <div>
              {status === "success" && (
                <div className="text-emerald-400 flex items-center gap-2 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  <span>Saved successfully</span>
                </div>
              )}
              {status === "error" && (
                <div className="text-red-400 flex items-center gap-2 text-sm">
                  <AlertCircle className="w-4 h-4" />
                  <span>{message}</span>
                </div>
              )}
            </div>

            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all shadow-lg shadow-blue-900/20"
            >
              {saving ? (
                <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
