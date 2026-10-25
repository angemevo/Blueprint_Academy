import Link from "next/link";

/** Accueil public, rendu statique. */
export default function HomePage() {
  return (
    <section className="flex flex-col gap-8 py-12">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight text-content-primary sm:text-5xl">
          Soyez operationnel dans Unreal des votre premier jour
        </h1>
        <p className="mt-4 max-w-2xl text-content-secondary">
          Blueprint Academy vous apprend Unreal Engine Blueprint en pratiquant,
          directement dans le navigateur : pas de video, pas besoin d&apos;installer
          Unreal. Vous construisez, la plateforme verifie.
        </p>
        <div className="mt-6 flex gap-3">
          <Link
            href="/catalogue"
            className="rounded bg-accent px-4 py-2 font-medium text-surface-0 hover:bg-accent-strong"
          >
            Voir le catalogue
          </Link>
          <Link
            href="/inscription"
            className="rounded border border-surface-2 px-4 py-2 font-medium text-content-primary hover:border-accent"
          >
            Creer un compte
          </Link>
        </div>
      </div>
    </section>
  );
}
