import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { ErrorBoundary } from "../components/ErrorBoundary";

function ProblemChild(): React.ReactNode {
  throw new Error("Test error");
  return null;
}

function GoodChild() {
  return <div>All good</div>;
}

describe("ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>,
    );
    expect(screen.getByText("All good")).toBeInTheDocument();
  });

  it("renders error UI when a child throws", () => {
    // Suppress console.error for the expected error
    const spy = vi.spyOn(console, "error").mockImplementation(() => { });

    render(
      <ErrorBoundary>
        <ProblemChild />
      </ErrorBoundary>,
    );

    expect(screen.getByText(/Application Error/i)).toBeInTheDocument();
    expect(screen.getByText("Reload Page")).toBeInTheDocument();
    expect(screen.getByText("Error Details")).toBeInTheDocument();

    spy.mockRestore();
  });
});
