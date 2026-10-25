import type { ReactNode } from "react";

import type { ContentBlock } from "@/lib/lessons";

const CALLOUT_LABELS: Record<string, string> = {
  info: "À retenir",
  why: "Pourquoi",
  when: "Quand l'utiliser",
  tip: "Astuce",
  pitfall: "Erreur classique",
  real_game: "Dans un vrai jeu",
};

const str = (value: unknown): string => (typeof value === "string" ? value : "");
const strings = (value: unknown): string[] =>
  Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
const isSafeUrl = (url: string) => /^(https?:\/\/|\/)/.test(url);

function Block({ block }: { block: ContentBlock }): ReactNode {
  switch (block.type) {
    case "heading": {
      const level = Number(block.level);
      const Tag = level === 3 ? "h3" : level === 4 ? "h4" : "h2";
      return <Tag className="mt-6 text-xl font-semibold text-content-primary">{str(block.text)}</Tag>;
    }
    case "text":
      return <p className="text-content-secondary">{str(block.text)}</p>;
    case "list": {
      const Tag = block.style === "numbered" ? "ol" : "ul";
      return (
        <Tag className={`pl-6 text-content-secondary ${Tag === "ol" ? "list-decimal" : "list-disc"}`}>
          {strings(block.items).map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </Tag>
      );
    }
    case "code":
      return (
        <figure>
          <pre className="overflow-x-auto rounded-md border border-border-subtle bg-surface-2 p-4 font-mono text-sm">
            <code data-language={str(block.language) || undefined}>{str(block.code)}</code>
          </pre>
          {str(block.caption) && (
            <figcaption className="mt-1 text-sm text-content-muted">{str(block.caption)}</figcaption>
          )}
        </figure>
      );
    case "callout": {
      const variant = str(block.variant) || "info";
      return (
        <aside
          data-variant={variant}
          className="rounded-md border border-border-subtle bg-surface-1 p-4"
        >
          <p className="font-semibold text-accent">
            {str(block.title) || CALLOUT_LABELS[variant] || CALLOUT_LABELS.info}
          </p>
          <p className="mt-1 text-content-secondary">{str(block.text)}</p>
        </aside>
      );
    }
    case "image": {
      const url = str(block.url);
      if (!isSafeUrl(url)) return null;
      return (
        <figure>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={url} alt={str(block.alt)} className="max-w-full rounded-md" loading="lazy" />
          {str(block.caption) && (
            <figcaption className="mt-1 text-sm text-content-muted">{str(block.caption)}</figcaption>
          )}
        </figure>
      );
    }
    case "graph": {
      const graph = block.graph as { nodes?: unknown[]; edges?: unknown[] } | undefined;
      return (
        <figure className="rounded-md border border-border-subtle bg-surface-1 p-4">
          <p className="text-content-secondary">
            Schéma de graphe : {graph?.nodes?.length ?? 0} nodes, {graph?.edges?.length ?? 0} connexions.
          </p>
          {str(block.caption) && (
            <figcaption className="mt-1 text-sm text-content-muted">{str(block.caption)}</figcaption>
          )}
        </figure>
      );
    }
    case "key_points":
      return (
        <section className="rounded-md border border-border-subtle bg-surface-1 p-4">
          <p className="font-semibold text-content-primary">{str(block.title) || "Points clés"}</p>
          <ul className="mt-2 list-disc pl-6 text-content-secondary">
            {strings(block.items).map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </section>
      );
    case "self_check":
      return (
        <details className="rounded-md border border-border-subtle bg-surface-1 p-4">
          <summary className="cursor-pointer text-content-primary">{str(block.question)}</summary>
          <p className="mt-2 text-content-secondary">{str(block.answer)}</p>
        </details>
      );
    default:
      return null; // bloc inconnu : ignoré proprement
  }
}

export function LessonBlocks({ blocks }: { blocks: ContentBlock[] }) {
  return (
    <div className="flex flex-col gap-4">
      {blocks.map((block, i) => (
        <Block key={i} block={block} />
      ))}
    </div>
  );
}
