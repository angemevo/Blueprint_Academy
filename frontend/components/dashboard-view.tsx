"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { fetchDashboard } from "@/lib/dashboard";

function Bar({ value, label }: { value: number; label: string }) {
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      className="h-2 w-full rounded bg-surface-2"
    >
      <div className="h-2 rounded bg-accent" style={{ width: `${pct}%` }} />
    </div>
  );
}

export function DashboardView() {
  const { data, isPending, isError } = useQuery({
    queryKey: ["dashboard"],
    queryFn: fetchDashboard,
  });

  if (isPending) {
    return (
      <p role="status" className="p-8 text-content-muted">
        Chargement...
      </p>
    );
  }
  if (isError) {
    return (
      <p role="alert" className="p-8 text-content-secondary">
        Impossible de charger votre espace pour le moment.
      </p>
    );
  }

  const xpPercent =
    data.next_level_xp ? Math.round((data.total_xp / data.next_level_xp) * 100) : 100;
  const isEmpty = data.current_paths.length === 0 && data.recent_attempts.length === 0;
  const firstPath = data.current_paths[0];

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-8">
      <h1 className="text-3xl font-bold text-content-primary">Mon espace</h1>

      <section aria-labelledby="niveau" className="rounded border border-surface-2 bg-surface-1 p-5">
        <h2 id="niveau" className="text-xl font-semibold text-content-primary">
          Niveau {data.level}
        </h2>
        <p className="mb-2 text-content-secondary">
          {data.total_xp} XP
          {data.xp_to_next_level !== null
            ? ` · encore ${data.xp_to_next_level} XP pour le niveau suivant`
            : " · niveau maximum atteint"}
        </p>
        <Bar value={xpPercent} label="Progression vers le niveau suivant" />
      </section>

      {isEmpty && (
        <p className="rounded border border-surface-2 bg-surface-1 p-5 text-content-secondary">
          Vous n&apos;avez pas encore commencé.{" "}
          <Link href="/catalogue" className="text-accent underline">
            Découvrir le catalogue
          </Link>
        </p>
      )}

      {data.next_lesson && firstPath && (
        <Link
          href={`/catalogue/${firstPath.slug}/lecons/${data.next_lesson.id}`}
          className="inline-block rounded bg-accent px-4 py-2 font-semibold text-surface-0"
        >
          Continuer : {data.next_lesson.title}
        </Link>
      )}

      {data.current_paths.length > 0 && (
        <section aria-labelledby="parcours">
          <h2 id="parcours" className="mb-3 text-xl font-semibold text-content-primary">
            Parcours en cours
          </h2>
          <ul className="space-y-3">
            {data.current_paths.map((p) => (
              <li key={p.id} className="rounded border border-surface-2 bg-surface-1 p-4">
                <Link href={`/catalogue/${p.slug}`} className="font-medium text-content-primary">
                  {p.title}
                </Link>
                <p className="mb-2 text-sm text-content-secondary">{p.completion_percent} %</p>
                <Bar value={p.completion_percent} label={`Avancement ${p.title}`} />
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.skills.length > 0 && (
        <section aria-labelledby="skills">
          <h2 id="skills" className="mb-3 text-xl font-semibold text-content-primary">
            Maîtrise des skills
          </h2>
          <ul className="space-y-3">
            {data.skills.map((s) => (
              <li key={s.id}>
                <p className="text-sm text-content-primary">
                  {s.name} · {s.mastery_score} %{s.is_mastered ? " · maîtrisé" : ""}
                </p>
                <Bar value={s.mastery_score} label={`Maîtrise ${s.name}`} />
              </li>
            ))}
          </ul>
        </section>
      )}

      {data.recent_attempts.length > 0 && (
        <section aria-labelledby="activite">
          <h2 id="activite" className="mb-3 text-xl font-semibold text-content-primary">
            Dernières activités
          </h2>
          <ul className="space-y-2">
            {data.recent_attempts.map((a) => (
              <li key={a.id} className="text-content-secondary">
                {a.exercise.title} · {a.is_correct ? "réussi" : "à retenter"} · score {a.score}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
