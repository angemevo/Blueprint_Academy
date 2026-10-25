import Link from "next/link";

import { HealthStatus } from "@/components/health-status";

/** Accueil provisoire, remplace par la vitrine plus tard. */
export default function HomePage() {
  return (
    <section className="flex flex-col gap-8 py-12">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight text-content-primary sm:text-5xl">
          Blueprint Academy
        </h1>
        <p className="mt-4 max-w-2xl text-content-secondary">
          Apprendre Unreal Engine Blueprint en pratiquant, directement dans le
          navigateur.
        </p>
        <Link
          href="/catalogue"
          className="mt-6 inline-block rounded bg-accent px-4 py-2 font-medium text-surface-0 hover:bg-accent-strong"
        >
          Voir le catalogue
        </Link>
      </div>
      <HealthStatus />
    </section>
  );
}
