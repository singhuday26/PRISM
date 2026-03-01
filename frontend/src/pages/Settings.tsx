import { useState, useEffect } from "react";
import { Bell, Save, Mail, Activity } from "lucide-react";
import { subscribe, fetchDiseases, type DiseaseInfo } from "../lib/api";
import { useToast } from "../context/ToastContext";

export function Settings() {
  const [email, setEmail] = useState("");
  const [diseases, setDiseases] = useState<string[]>(["DENGUE"]);
  const [minRisk, setMinRisk] = useState("HIGH");
  const [allDiseases, setAllDiseases] = useState<DiseaseInfo[]>([]);
  const [saving, setSaving] = useState(false);

  const { success, error } = useToast();

  useEffect(() => {
    fetchDiseases()
      .then((d) => setAllDiseases(d.diseases))
      .catch((err) => {
        console.error(err);
        error("Failed to load diseases list.");
      });
  }, [error]);

  const handleSave = async () => {
    if (!email) {
      error("Email address is required to subscribe to alerts.");
      return;
    }

    setSaving(true);

    try {
      await subscribe({
        email,
        diseases,
        min_risk_level: minRisk as "MEDIUM" | "HIGH" | "CRITICAL",
        regions: [], // All regions for now
        frequency: "immediate",
      });
      success("Notification preferences saved successfully!");
    } catch (err: unknown) {
      error(err instanceof Error ? err.message : "Failed to update notification settings");
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
    <div className="space-y-8 max-w-2xl mx-auto xl:mx-0">
      <div>
        <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
        <p className="text-gray-400">
          Manage your early warning notification preferences.
        </p>
      </div>

      <div className="glass-card p-6 sm:p-8 border border-white/5 rounded-xl">
        <div className="flex items-center gap-3 mb-8 pb-6 border-b border-white/10">
          <div className="p-2.5 rounded-lg bg-blue-500/10">
            <Bell className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Alert Subscriptions</h2>
            <p className="text-sm text-gray-400">Receive email alerts when risk thresholds are exceeded.</p>
          </div>
        </div>

        <div className="space-y-8">
          {/* Email Input */}
          <div className="space-y-3">
            <label className="text-sm font-semibold text-gray-300 flex items-center gap-2 uppercase tracking-wide">
              <Mail className="w-4 h-4 text-indigo-400" />
              Recipient Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="officer@prism.org"
              className="w-full bg-black/30 border border-white/10 rounded-lg px-4 py-3.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/50 transition-all placeholder:text-gray-600"
            />
          </div>

          {/* Risk Threshold */}
          <div className="space-y-3">
            <label className="text-sm font-semibold text-gray-300 flex items-center gap-2 uppercase tracking-wide">
              <Activity className="w-4 h-4 text-emerald-400" />
              Alert Sensitivity
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { level: "MEDIUM", desc: "All potential risks" },
                { level: "HIGH", desc: "Significant outbreaks" },
                { level: "CRITICAL", desc: "Severe emergencies only" }
              ].map(({ level, desc }) => (
                <button
                  key={level}
                  onClick={() => setMinRisk(level)}
                  className={`px-4 py-3 rounded-xl text-sm font-medium border-2 transition-all flex flex-col items-start gap-1 ${minRisk === level
                      ? "bg-blue-600/10 border-blue-500 text-blue-300 shadow-sm"
                      : "bg-white/5 border-transparent text-gray-500 hover:bg-white/10 hover:text-gray-300"
                    }`}
                >
                  <span className={minRisk === level ? "text-white" : ""}>{level} Risk</span>
                  <span className={`text-[10px] font-normal ${minRisk === level ? "text-blue-300/80" : "text-gray-500"}`}>{desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Diseases */}
          <div className="space-y-3">
            <label className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
              Monitored Pathogens
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {(allDiseases.length > 0
                ? allDiseases.map((d) => d.disease_id)
                : ["DENGUE", "MALARIA", "CHIKUNGUNYA"]
              ).map((d) => (
                <label
                  key={d}
                  className={`flex items-center gap-3 p-3.5 rounded-xl border-2 cursor-pointer transition-colors ${diseases.includes(d)
                      ? "bg-indigo-500/5 border-indigo-500/30"
                      : "bg-white/5 border-transparent hover:bg-white/10"
                    }`}
                >
                  <input
                    type="checkbox"
                    checked={diseases.includes(d)}
                    onChange={() => toggleDisease(d)}
                    className="w-4 h-4 rounded border-gray-600 text-indigo-500 focus:ring-indigo-500 bg-gray-700/50 outline-none"
                  />
                  <span className={`capitalize font-medium ${diseases.includes(d) ? "text-white" : "text-gray-400"}`}>
                    {d.toLowerCase()}
                  </span>
                </label>
              ))}
            </div>
            {diseases.length === 0 && (
              <p className="text-xs text-amber-500/80 mt-2">Warning: You will not receive any alerts until selecting at least one pathogen.</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="pt-6 border-t border-white/10 flex justify-end">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 px-8 py-3 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all shadow-lg shadow-blue-900/20 w-full sm:w-auto justify-center"
            >
              {saving ? (
                <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full" />
              ) : (
                <Save className="w-5 h-5" />
              )}
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
