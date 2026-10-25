import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import MonEspacePage from "@/app/mon-espace/page";
import { DashboardView } from "@/components/dashboard-view";
import { useAuthStore } from "@/stores/auth-store";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/mon-espace",
}));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

const base = {
  total_xp: 0, level: 1, next_level_xp: 100, xp_to_next_level: 100,
  current_paths: [], next_lesson: null, recent_attempts: [], skills: [],
};

function renderView() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={client}>
      <DashboardView />
    </QueryClientProvider>,
  );
}

afterEach(() => vi.restoreAllMocks());

describe("tableau de bord", () => {
  beforeEach(() => replace.mockClear());

  it("redirige un visiteur vers la connexion", async () => {
    useAuthStore.setState({ accessToken: null, status: "anonymous" });
    await act(async () => {
      render(<MonEspacePage />);
    });
    expect(replace).toHaveBeenCalledWith("/connexion?next=%2Fmon-espace");
  });

  it("affiche un espace rempli", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, {
        ...base, total_xp: 150, level: 2, next_level_xp: 300, xp_to_next_level: 150,
        current_paths: [{ id: 1, slug: "bp", title: "Fondamentaux", completion_percent: 40 }],
        next_lesson: { id: 7, title: "Les variables" },
        skills: [{ id: 1, name: "Variables", mastery_score: 60, is_mastered: false }],
        recent_attempts: [{ id: 1, exercise: { id: 3, title: "Exo trois", type: "H" },
          is_correct: true, score: 100, attempt_number: 1, created_at: "2026-01-01T00:00:00Z" }],
      }),
    );
    renderView();
    expect(await screen.findByText("Niveau 2")).toBeInTheDocument();
    expect(screen.getByText(/encore 150 XP/)).toBeInTheDocument();
    expect(screen.getByRole("progressbar", { name: "Progression vers le niveau suivant" }))
      .toHaveAttribute("aria-valuenow", "50");
    expect(screen.getByText("Fondamentaux")).toBeInTheDocument();
    expect(screen.getByText(/Variables · 60 %/)).toBeInTheDocument();
    expect(screen.getByText(/Exo trois/)).toBeInTheDocument();
    expect(screen.getByText(/Continuer : Les variables/).closest("a"))
      .toHaveAttribute("href", "/catalogue/bp/lecons/7");
  });

  it("affiche l'état vide d'un nouvel étudiant", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(200, base));
    renderView();
    expect(await screen.findByText(/pas encore commencé/)).toBeInTheDocument();
    expect(screen.queryByText(/Continuer/)).not.toBeInTheDocument();
  });

  it("affiche une erreur si l'API échoue", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(500, {}));
    renderView();
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
