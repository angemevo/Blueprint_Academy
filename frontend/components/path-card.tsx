import Link from "next/link";

import type { PathSummary } from "@/lib/catalogue";

export function PathCard({ path }: { path: PathSummary }) {
  return (
    <li>
      <Link
        href={`/catalogue/${path.slug}`}
        className="block h-full rounded border border-surface-2 bg-surface-1 p-5 hover:border-accent"
      >
        <h2 className="text-xl font-semibold text-content-primary">{path.title}</h2>
        {path.subtitle && (
          <p className="mt-1 text-content-secondary">{path.subtitle}</p>
        )}
        <p className="mt-3 text-sm text-content-secondary">
          {path.difficulty}
          {path.estimated_hours ? ` · ${path.estimated_hours} h` : ""}
        </p>
      </Link>
    </li>
  );
}
