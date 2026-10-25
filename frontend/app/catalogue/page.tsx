import { PathCard } from "@/components/path-card";
import { fetchPaths, type PathSummary } from "@/lib/catalogue";

export const revalidate = 60;
export const metadata = { title: "Catalogue - Blueprint Academy" };

export default async function CataloguePage() {
  let paths: PathSummary[] = [];
  let failed = false;
  try {
    paths = await fetchPaths();
  } catch {
    failed = true;
  }

  return (
    <section className="py-12">
      <h1 className="text-3xl font-semibold text-content-primary">Catalogue</h1>
      {failed ? (
        <p role="alert" className="mt-6 text-content-secondary">
          Impossible de charger les parcours pour le moment. Reessayez dans un instant.
        </p>
      ) : paths.length === 0 ? (
        <p className="mt-6 text-content-secondary">
          Aucun parcours n&apos;est publie pour le moment. Revenez bientot.
        </p>
      ) : (
        <ul className="mt-6 grid gap-4 sm:grid-cols-2">
          {paths.map((path) => (
            <PathCard key={path.id} path={path} />
          ))}
        </ul>
      )}
    </section>
  );
}
