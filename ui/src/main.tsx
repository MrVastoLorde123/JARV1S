import { Component, StrictMode, type ErrorInfo, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

class InterfaceErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("JARVIS interface rendering failure", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, background: "#06090e", color: "#e7edf5", fontFamily: "system-ui, sans-serif" }}>
          <section style={{ width: "min(620px, 100%)", padding: 24, border: "1px solid #3a2630", borderRadius: 12, background: "#0d1219" }}>
            <div style={{ fontSize: 10, letterSpacing: "0.14em", color: "#d06b73" }}>JARVIS INTERFACE FAILURE</div>
            <h1 style={{ margin: "8px 0", fontSize: 24 }}>The interface hit a rendering error.</h1>
            <p style={{ color: "#8c9aaa", lineHeight: 1.55 }}>The shell is still running. Refresh the page after inspecting the browser console.</p>
            <pre style={{ overflow: "auto", whiteSpace: "pre-wrap", padding: 12, borderRadius: 8, background: "#080c12", color: "#bbc6d4", fontSize: 12 }}>{this.state.error.message}</pre>
            <button type="button" onClick={() => window.location.reload()} style={{ marginTop: 12, padding: "9px 12px", borderRadius: 7, border: "1px solid #466183", background: "#142131", color: "#e3edf8" }}>RELOAD INTERFACE</button>
          </section>
        </main>
      );
    }

    return this.props.children;
  }
}

const root = document.getElementById("root");

if (!root) {
  throw new Error("JARVIS interface root element #root was not found.");
}

createRoot(root).render(
  <StrictMode>
    <InterfaceErrorBoundary>
      <App />
    </InterfaceErrorBoundary>
  </StrictMode>,
);
