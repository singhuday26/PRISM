import { describe, it, expect, vi, beforeEach } from "vitest";

// We test that fetch URLs are constructed correctly by the api module
// by mocking global.fetch and importing the functions.

const mockFetch = vi.fn();
global.fetch = mockFetch;

// Reset before each to avoid cross-test contamination
beforeEach(() => {
  mockFetch.mockReset();
});

describe("api.ts URL construction", () => {
  it("fetchRegions calls /api/regions/", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ regions: [], count: 0 }),
    });

    const { fetchRegions } = await import("../lib/api");
    await fetchRegions();

    expect(mockFetch).toHaveBeenCalledWith("/api/regions");
  });

  it("fetchDiseases calls /api/diseases/", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ diseases: [], count: 0 }),
    });

    const { fetchDiseases } = await import("../lib/api");
    await fetchDiseases();

    expect(mockFetch).toHaveBeenCalledWith("/api/diseases/");
  });

  it("fetchAlerts builds correct query string", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ date: "", alerts: [], count: 0 }),
    });

    const { fetchAlerts } = await import("../lib/api");
    await fetchAlerts("IN-MH", "DENGUE", 10);

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("/api/alerts/latest");
    expect(url).toContain("region_id=IN-MH");
    expect(url).toContain("disease=DENGUE");
    expect(url).toContain("limit=10");
  });

  it("fetchLatestForecasts includes region and disease", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ date: "", forecasts: [], count: 0 }),
    });

    const { fetchLatestForecasts } = await import("../lib/api");
    await fetchLatestForecasts("IN-DL", "COVID");

    const url = mockFetch.mock.calls[0][0] as string;
    expect(url).toContain("/api/forecasts/latest");
    expect(url).toContain("region_id=IN-DL");
    expect(url).toContain("disease=COVID");
  });

  it("generateReport sends POST with correct body", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ report_id: "rpt_123", status: "accepted" }),
    });

    const { generateReport } = await import("../lib/api");
    await generateReport("weekly_summary", undefined, "DENGUE");

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/reports/generate",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );

    const body = JSON.parse(
      (mockFetch.mock.calls[0][1] as RequestInit).body as string,
    );
    expect(body.type).toBe("weekly_summary");
    expect(body.disease).toBe("DENGUE");
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      statusText: "Not Found",
    });

    const { fetchRegions } = await import("../lib/api");
    await expect(fetchRegions()).rejects.toThrow();
  });
});
