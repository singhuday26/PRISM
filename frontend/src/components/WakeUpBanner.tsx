/**
 * WakeUpBanner
 *
 * Silently pings the backend health endpoint on mount. If the backend is cold
 * (no response within SHOW_AFTER_MS), a non-blocking banner appears to reassure
 * the user that data is loading. Automatically dismisses once the backend responds.
 */

import { useEffect, useState } from "react";

// How long (ms) to wait before showing the "warming up" banner.
// Render free tier cold starts take ~20–40 s — show the banner after 3 s.
const SHOW_AFTER_MS = 3_000;

// The health ping endpoint (via Vercel proxy → Render).
const HEALTH_URL = "/api/health/ping";

export function WakeUpBanner() {
  const [visible, setVisible] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    let showTimer: ReturnType<typeof setTimeout> | null = null;
    let aborted = false;

    const checkBackend = async () => {
      // Schedule the banner to appear if backend hasn't responded yet
      showTimer = setTimeout(() => {
        if (!aborted) setVisible(true);
      }, SHOW_AFTER_MS);

      try {
        await fetch(HEALTH_URL, { method: "GET", cache: "no-store" });
      } catch {
        // Even on error, stop showing the banner — app will handle errors itself
      } finally {
        if (showTimer) clearTimeout(showTimer);
        if (!aborted) setVisible(false);
      }
    };

    checkBackend();

    return () => {
      aborted = true;
      if (showTimer) clearTimeout(showTimer);
    };
  }, []);

  if (!visible || dismissed) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        position: "fixed",
        bottom: "1.5rem",
        left: "50%",
        transform: "translateX(-50%)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        padding: "0.75rem 1.25rem",
        borderRadius: "0.75rem",
        background: "rgba(15, 23, 42, 0.92)",
        backdropFilter: "blur(12px)",
        border: "1px solid rgba(99, 102, 241, 0.4)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
        color: "#e2e8f0",
        fontSize: "0.875rem",
        fontFamily: "Inter, system-ui, sans-serif",
        maxWidth: "90vw",
        animation: "prism-slideup 0.35s ease-out",
      }}
    >
      {/* Animated spinner */}
      <div
        style={{
          width: "1rem",
          height: "1rem",
          borderRadius: "50%",
          border: "2px solid rgba(99, 102, 241, 0.3)",
          borderTopColor: "#6366f1",
          flexShrink: 0,
          animation: "prism-spin 0.8s linear infinite",
        }}
      />

      <span>
        <strong style={{ color: "#a5b4fc" }}>Server is warming up</strong>
        {" — "}free-tier hosts sleep after inactivity. Data loads in ~20 s.
      </span>

      {/* Dismiss button */}
      <button
        onClick={() => setDismissed(true)}
        aria-label="Dismiss"
        style={{
          marginLeft: "0.5rem",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          color: "#94a3b8",
          fontSize: "1.1rem",
          lineHeight: 1,
          padding: "0 0.2rem",
          flexShrink: 0,
        }}
      >
        ×
      </button>

      <style>{`
        @keyframes prism-spin { to { transform: rotate(360deg); } }
        @keyframes prism-slideup {
          from { opacity: 0; transform: translateX(-50%) translateY(1rem); }
          to   { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
      `}</style>
    </div>
  );
}
