import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            backgroundColor: "#1e293b",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: "2rem",
          }}
        >
          <div
            style={{
              maxWidth: "42rem",
              width: "100%",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "0.5rem",
              padding: "2rem",
            }}
          >
            <h1
              style={{
                fontSize: "1.5rem",
                fontWeight: "bold",
                color: "#f87171",
                marginBottom: "1rem",
              }}
            >
              ⚠️ Application Error
            </h1>
            <p style={{ color: "#d1d5db", marginBottom: "1rem" }}>
              Something went wrong while rendering the application.
            </p>
            <details
              style={{
                backgroundColor: "rgba(0,0,0,0.3)",
                borderRadius: "0.25rem",
                padding: "1rem",
                fontSize: "0.875rem",
              }}
            >
              <summary
                style={{
                  color: "#9ca3af",
                  cursor: "pointer",
                  marginBottom: "0.5rem",
                }}
              >
                Error Details
              </summary>
              <pre
                style={{
                  color: "#fca5a5",
                  whiteSpace: "pre-wrap",
                  overflow: "auto",
                }}
              >
                {this.state.error?.toString()}
              </pre>
              {this.state.errorInfo && (
                <pre
                  style={{
                    color: "#6b7280",
                    whiteSpace: "pre-wrap",
                    overflow: "auto",
                    marginTop: "0.5rem",
                    fontSize: "0.75rem",
                  }}
                >
                  {this.state.errorInfo.componentStack}
                </pre>
              )}
            </details>
            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: "1rem",
                padding: "0.5rem 1rem",
                backgroundColor: "#ef4444",
                color: "white",
                borderRadius: "0.25rem",
                border: "none",
                cursor: "pointer",
              }}
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
