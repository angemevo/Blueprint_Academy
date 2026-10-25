export function PlaceholderPage({ title }: { title: string }) {
  return (
    <section className="py-16">
      <h1 className="text-3xl font-semibold text-content-primary">{title}</h1>
      <p className="mt-3 text-content-secondary">Cette page arrive bientot.</p>
    </section>
  );
}
