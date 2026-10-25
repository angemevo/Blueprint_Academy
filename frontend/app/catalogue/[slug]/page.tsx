import Link from "next/link";
import { notFound } from "next/navigation";

import { fetchPath, type PathDetail } from "@/lib/catalogue";

export const revalidate = 60;

type Props = { params: Promise<{ slug: string }> };

export default async function PathDetailPage({ params }: Props) {
  const { slug } = await params;
  let path: PathDetail | null;
  try {
    path = await fetchPath(slug);
  } catch {
    return (
      <section className="py-12">
        <p role="alert" className="text-content-secondary">
          Impossible de charger ce parcours pour le moment. Reessayez dans un instant.
        </p>
      </section>
    );
  }
  if (!path) notFound();

  return (
    <section className="py-12">
      <Link href="/catalogue" className="text-sm text-accent hover:underline">
        Retour au catalogue
      </Link>
      <h1 className="mt-3 text-3xl font-semibold text-content-primary">{path.title}</h1>
      {path.subtitle && <p className="mt-2 text-content-secondary">{path.subtitle}</p>}
      {path.description && (
        <p className="mt-4 max-w-2xl text-content-secondary">{path.description}</p>
      )}
      {path.modules.length === 0 ? (
        <p className="mt-8 text-content-secondary">Le contenu de ce parcours arrive bientot.</p>
      ) : (
        <ol className="mt-8 flex flex-col gap-6">
          {path.modules.map((module) => (
            <li key={module.id}>
              <h2 className="text-xl font-semibold text-content-primary">{module.title}</h2>
              {module.description && (
                <p className="mt-1 text-content-secondary">{module.description}</p>
              )}
              <ol className="mt-3 list-decimal pl-6 text-content-secondary">
                {module.lessons.map((lesson) => (
                  <li key={lesson.id}>
                    <Link
                      href={`/catalogue/${path.slug}/lecons/${lesson.id}`}
                      className="text-accent hover:underline"
                    >
                      {lesson.title}
                    </Link>
                  </li>
                ))}
              </ol>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
