import Link from "next/link";

export default function NotFound() {
  return (
    <section className="py-16">
      <p className="font-mono text-sm text-accent">404</p>
      <h1 className="mt-2 text-3xl font-semibold">Page introuvable</h1>
      <p className="mt-3 text-content-secondary">
        Cette page n&apos;existe pas ou a ete deplacee.
      </p>
      <Link href="/" className="mt-6 inline-block text-accent hover:underline">
        Retour a l&apos;accueil
      </Link>
    </section>
  );
}
