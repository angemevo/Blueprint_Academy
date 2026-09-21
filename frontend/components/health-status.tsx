"use client";

import { API_BASE_URL } from "@/lib/api-client";
import { useHealth } from "@/lib/hooks/use-health";

type Tone = "pending" | "ok" | "error";

const TONE_STYLES: Record<Tone, { dot: string; label: string; text: string }> = {
  pending: {
    dot: "bg-warning",
    label: "Verification...",
    text: "text-content-secondary",
  },
  ok: { dot: "bg-success", label: "En ligne", text: "text-success" },
  error: { dot: "bg-danger", label: "Injoignable", text: "text-danger" },
};

/** Carte de verification de la liaison frontend -> backend. */
export function HealthStatus() {
  const { data, error, isPending, isFetching, refetch } = useHealth();

  const tone: Tone = isPending ? "pending" : error ? "error" : "ok";
  const style = TONE_STYLES[tone];

  return (
    <section className="w-full max-w-xl rounded-xl border border-border-subtle bg-surface-1/80 p-6 backdrop-blur">
      <header className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-medium tracking-wide text-content-secondary uppercase">
            Backend Django
          </h2>
          <p className="mt-1 font-mono text-xs text-content-muted">
            GET {API_BASE_URL}/health/
          </p>
        </div>
        <span className={`flex items-center gap-2 text-sm font-medium ${style.text}`}>
          <span className={`size-2 rounded-full ${style.dot}`} aria-hidden />
          {style.label}
        </span>
      </header>

      <pre className="mt-5 overflow-x-auto rounded-lg border border-border-subtle bg-surface-0 p-4 font-mono text-sm text-content-primary">
        {isPending
          ? "..."
          : error
            ? error.message
            : JSON.stringify(data, null, 2)}
      </pre>

      <button
        type="button"
        onClick={() => void refetch()}
        disabled={isFetching}
        className="mt-4 rounded-md border border-border-subtle px-3 py-1.5 text-sm text-content-secondary transition-colors hover:border-accent hover:text-accent disabled:opacity-50"
      >
        {isFetching ? "Ping en cours..." : "Relancer le ping"}
      </button>
    </section>
  );
}
