import { HealthStatus } from "@/components/health-status";

/**
 * Page de verification de la Phase 1.
 *
 * Elle sera remplacee par la vitrine publique (SSR/SSG, SEO) en Phase 3.
 */
export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center gap-10 px-6 py-16">
      <div>
        <p className="font-mono text-xs tracking-[0.2em] text-accent uppercase">
          Phase 1 - Architecture et configuration
        </p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight text-content-primary sm:text-5xl">
          Blueprint Academy
        </h1>
        <p className="mt-4 max-w-2xl text-content-secondary">
          Apprendre Unreal Engine Blueprint en pratiquant.{" "}
          <span className="text-content-muted">
            Learn - Practice - Build - Validate - Progress.
          </span>
        </p>
      </div>

      <HealthStatus />

      <footer className="font-mono text-xs text-content-muted">
        Socle pret : Django + DRF + PostgreSQL / Next.js + TypeScript + Tailwind
        + TanStack Query.
      </footer>
    </main>
  );
}
