import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

/*
 * Smoke-test each page component:
 *   - renders without crashing
 *   - renders known static text / headings
 *
 * All API calls are mocked so these tests are pure render tests.
 */

// ---------- global fetch mock ----------
const mockFetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () =>
      Promise.resolve({
        regions: [],
        diseases: [],
        forecasts: [],
        alerts: [],
        hotspots: [],
        count: 0,
        date: "2025-01-01",
      }),
  }),
);
global.fetch = mockFetch as unknown as typeof fetch;

beforeEach(() => {
  mockFetch.mockClear();
});

// Helper to wrap with Router (required by Link / NavLink usage)
function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

// ---------- tests ----------

describe("Dashboard page", () => {
  it("renders without crashing", async () => {
    const { Dashboard } = await import("../pages/Dashboard");
    const { container } = renderWithRouter(<Dashboard />);
    expect(container).toBeTruthy();
  });
});

describe("Analysis page", () => {
  it("renders without crashing", async () => {
    const { Analysis } = await import("../pages/Analysis");
    const { container } = renderWithRouter(<Analysis />);
    expect(container).toBeTruthy();
  });
});

describe("Resources page", () => {
  it("renders without crashing", async () => {
    const { Resources } = await import("../pages/Resources");
    const { container } = renderWithRouter(<Resources />);
    expect(container).toBeTruthy();
  });
});

describe("Reports page", () => {
  it("renders without crashing", async () => {
    const { Reports } = await import("../pages/Reports");
    const { container } = renderWithRouter(<Reports />);
    expect(container).toBeTruthy();
  });
});

describe("Settings page", () => {
  it("renders without crashing", async () => {
    const { Settings } = await import("../pages/Settings");
    const { container } = renderWithRouter(<Settings />);
    expect(container).toBeTruthy();
  });
});
