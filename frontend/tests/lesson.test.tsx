import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import LessonPage from "@/app/catalogue/[slug]/lecons/[id]/page";
import { LessonBlocks } from "@/components/lesson-blocks";
import { LessonView } from "@/components/lesson-view";
import { useAuthStore } from "@/stores/auth-store";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/catalogue/p/lecons/2",
  notFound: () => {
    throw new Error("NEXT_NOT_FOUND");
  },
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

afterEach(() => vi.restoreAllMocks());

describe("blocs de leçon", () => {
  it("affiche chaque type de bloc connu", () => {
    render(
      <LessonBlocks
        blocks={[
          { type: "heading", text: "Titre H" },
          { type: "text", text: "Paragraphe T" },
          { type: "list", style: "bullet", items: ["Item L1", "Item L2"] },
          { type: "code", code: "Print String", language: "text", caption: "Légende code" },
          { type: "callout", variant: "pitfall", text: "Texte callout" },
          { type: "image", url: "/img.png", alt: "Une image" },
          { type: "graph", graph: { nodes: [{ id: "a" }], edges: [] } },
          { type: "key_points", items: ["Point K1"] },
          { type: "self_check", question: "Question Q", answer: "Réponse R" },
        ]}
      />,
    );
    for (const text of ["Titre H", "Paragraphe T", "Item L2", "Print String", "Légende code",
      "Erreur classique", "Texte callout", "Point K1", "Question Q", "Réponse R"]) {
      expect(screen.getByText(text)).toBeInTheDocument();
    }
    expect(screen.getByRole("img", { name: "Une image" })).toHaveAttribute("src", "/img.png");
    expect(screen.getByText(/1 nodes/)).toBeInTheDocument();
  });

  it("ignore les blocs inconnus et les images non sûres", () => {
    const { container } = render(
      <LessonBlocks
        blocks={[
          { type: "hologram", text: "x" },
          { type: "image", url: "javascript:alert(1)" },
          { type: "text", text: "Reste" },
        ]}
      />,
    );
    expect(screen.getByText("Reste")).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
    expect(container.textContent).toBe("Reste");
  });
});

describe("page de leçon", () => {
  beforeEach(() => replace.mockClear());

  it("redirige un visiteur vers la connexion", async () => {
    useAuthStore.setState({ accessToken: null, status: "anonymous" });
    await act(async () => {
      render(<LessonPage params={Promise.resolve({ slug: "p", id: "2" })} />);
    });
    expect(replace).toHaveBeenCalledWith("/connexion?next=%2Fcatalogue%2Fp%2Flecons%2F2");
    expect(screen.queryByText("Leçon 2")).not.toBeInTheDocument();
  });

  it("affiche la leçon, ses skills, exercices et la navigation", async () => {
    const lesson = (id: number, order: number) => ({
      id, title: `Leçon ${id}`, slug: `l${id}`, summary: "", order, estimated_minutes: 5,
    });
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("lessons/2/")) {
        return json(200, {
          id: 2, title: "Leçon 2", slug: "l2", summary: "Résumé", module_id: 1,
          content: { blocks: [{ type: "text", text: "Corps" }, { type: "zzz" }] },
          estimated_minutes: 5, skills_taught: [{ id: 1, name: "Variables", slug: "v" }],
          exercises: [{ id: 9, title: "Exo neuf", type: "H" }],
        });
      }
      return json(200, {
        id: 1, title: "P", slug: "p", subtitle: "", description: "", difficulty: "beginner",
        estimated_hours: 1, order: 1,
        modules: [{ id: 1, title: "Mod", slug: "m", description: "", order: 1,
          lessons: [lesson(3, 3), lesson(1, 1), lesson(2, 2)] }],
      });
    });
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={client}>
        <LessonView pathSlug="p" lessonId={2} />
      </QueryClientProvider>,
    );
    expect(await screen.findByText("Corps")).toBeInTheDocument();
    expect(screen.getByText("Variables")).toBeInTheDocument();
    expect(screen.getByText("Exo neuf")).toBeInTheDocument();
    const prev = await screen.findByText(/← Leçon 1/);
    expect(prev.closest("a")).toHaveAttribute("href", "/catalogue/p/lecons/1");
    expect(screen.getByText(/Leçon 3 →/).closest("a")).toHaveAttribute("href", "/catalogue/p/lecons/3");
  });

  it("affiche une erreur si la leçon est inaccessible", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(404, {}));
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={client}>
        <LessonView pathSlug="p" lessonId={2} />
      </QueryClientProvider>,
    );
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
