"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { LessonBlocks } from "@/components/lesson-blocks";
import { fetchLesson, fetchPath, lessonNeighbours } from "@/lib/lessons";

export function LessonView({ pathSlug, lessonId }: { pathSlug: string; lessonId: number }) {
  const lesson = useQuery({ queryKey: ["lesson", lessonId], queryFn: () => fetchLesson(lessonId) });
  const path = useQuery({ queryKey: ["path", pathSlug], queryFn: () => fetchPath(pathSlug) });

  if (lesson.isPending) return <p role="status" className="p-8 text-content-muted">Chargement...</p>;
  if (lesson.isError) {
    return (
      <p role="alert" className="py-12 text-content-secondary">
        Impossible d&apos;afficher cette leçon (introuvable ou non accessible).
      </p>
    );
  }

  const data = lesson.data;
  const nav = path.data ? lessonNeighbours(path.data, data.module_id, data.id) : null;
  const href = (id: number) => `/catalogue/${pathSlug}/lecons/${id}`;

  return (
    <article className="py-12">
      <Link href={`/catalogue/${pathSlug}`} className="text-sm text-accent hover:underline">
        {nav ? `Retour au parcours · ${nav.moduleTitle}` : "Retour au parcours"}
      </Link>
      <h1 className="mt-3 text-3xl font-semibold text-content-primary">{data.title}</h1>
      {data.summary && <p className="mt-2 text-content-secondary">{data.summary}</p>}

      {data.skills_taught.length > 0 && (
        <section aria-label="Compétences enseignées" className="mt-4">
          <h2 className="text-sm font-semibold text-content-muted">Compétences enseignées</h2>
          <ul className="mt-1 flex flex-wrap gap-2">
            {data.skills_taught.map((s) => (
              <li key={s.id} className="rounded-full bg-surface-2 px-3 py-1 text-sm text-accent">
                {s.name}
              </li>
            ))}
          </ul>
        </section>
      )}

      <div className="mt-8">
        <LessonBlocks blocks={data.content?.blocks ?? []} />
      </div>

      <section aria-label="Exercices" className="mt-10">
        <h2 className="text-xl font-semibold text-content-primary">Exercices</h2>
        {data.exercises.length === 0 ? (
          <p className="mt-2 text-content-secondary">Aucun exercice pour cette leçon.</p>
        ) : (
          <ul className="mt-2 list-disc pl-6 text-content-secondary">
            {data.exercises.map((e) => (
              <li key={e.id}>
                <Link
                  href={`/catalogue/${pathSlug}/lecons/${data.id}/exercices/${e.id}`}
                  className="text-accent hover:underline"
                >
                  {e.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      {nav && (
        <nav aria-label="Navigation dans le module" className="mt-10 flex justify-between">
          {nav.previous ? (
            <Link href={href(nav.previous.id)} className="text-accent hover:underline">
              ← {nav.previous.title}
            </Link>
          ) : (
            <span />
          )}
          {nav.next && (
            <Link href={href(nav.next.id)} className="text-accent hover:underline">
              {nav.next.title} →
            </Link>
          )}
        </nav>
      )}
    </article>
  );
}
