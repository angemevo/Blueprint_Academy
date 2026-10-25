import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ExercisePage from "@/app/catalogue/[slug]/lecons/[id]/exercices/[exerciseId]/page";
import { ExerciseWorkspace } from "@/components/exercise-workspace";
import type { ExerciseDetail } from "@/lib/exercises";
import { useAuthStore } from "@/stores/auth-store";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/catalogue/p/lecons/2/exercices/5",
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

const base = {
  difficulty: "beginner", time_limit_seconds: null, max_attempts: null, xp_reward: 5, hints_count: 0,
};
const questionEx: ExerciseDetail = {
  ...base, id: 5, type: "A", title: "Question A",
  content: { question: "Quel est le premier événement ?" },
};
const mcqEx = (multiple: boolean): ExerciseDetail => ({
  ...base, id: 6, type: "B", title: "QCM B",
  content: {
    question: "Lesquels ?", multiple,
    options: [{ id: "o1", text: "Option un" }, { id: "o2", text: "Option deux" }],
  },
});

const renderWs = (ex: ExerciseDetail) => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <ExerciseWorkspace exercise={ex} />
    </QueryClientProvider>,
  );
};

const body = (spy: { mock: { calls: unknown[][] } }) =>
  JSON.parse(((spy.mock.calls[0]?.[1] as RequestInit).body as string));

afterEach(() => vi.restoreAllMocks());

describe("page d'exercice", () => {
  beforeEach(() => replace.mockClear());
  it("redirige un visiteur vers la connexion", async () => {
    useAuthStore.setState({ accessToken: null, status: "anonymous" });
    await act(async () => {
      render(<ExercisePage params={Promise.resolve({ slug: "p", id: "2", exerciseId: "5" })} />);
    });
    expect(replace).toHaveBeenCalledWith("/connexion?next=%2Fcatalogue%2Fp%2Flecons%2F2%2Fexercices%2F5");
  });
});

describe("ExerciseWorkspace", () => {
  it("type A : envoie la réponse avec la durée et affiche le résultat", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 0, feedback: ["Ce n'est pas la bonne réponse."],
        hints: ["Pense à BeginPlay"], attempt_number: 1 }),
    );
    renderWs(questionEx);
    expect(screen.getByRole("button", { name: "Valider" })).toBeDisabled();
    fireEvent.change(screen.getByLabelText("Ta réponse"), { target: { value: "Tick" } });
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    expect(await screen.findByText(/Raté · score 0/)).toBeInTheDocument();
    expect(screen.getByText("Pense à BeginPlay")).toBeInTheDocument();
    const sent = body(spy);
    expect(sent.submission).toEqual({ answer: "Tick" });
    expect(typeof sent.duration_seconds).toBe("number");
    expect(String(spy.mock.calls[0]?.[0])).toContain("exercises/5/submit/");

    fireEvent.click(screen.getByRole("button", { name: "Réessayer" }));
    expect(screen.queryByText(/Raté/)).not.toBeInTheDocument();
    expect(screen.getByLabelText("Ta réponse")).toHaveValue("");
  });

  it("type B choix unique : radio, soumission d'un seul id, réussite", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: true, score: 100, feedback: ["Bonne réponse."], hints: [], attempt_number: 1 }),
    );
    renderWs(mcqEx(false));
    fireEvent.click(screen.getByLabelText("Option un"));
    fireEvent.click(screen.getByLabelText("Option deux"));
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    expect(await screen.findByText(/Réussi · score 100/)).toBeInTheDocument();
    expect(body(spy).submission).toEqual({ selected_option_ids: ["o2"] });
    expect(screen.queryByRole("button", { name: "Réessayer" })).not.toBeInTheDocument();
  });

  it("type B choix multiple : cases à cocher", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 0, feedback: [], hints: [], attempt_number: 1 }),
    );
    renderWs(mcqEx(true));
    fireEvent.click(screen.getByLabelText("Option un"));
    fireEvent.click(screen.getByLabelText("Option deux"));
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    await screen.findByText(/Raté/);
    expect(body(spy).submission).toEqual({ selected_option_ids: ["o1", "o2"] });
  });

  it("409 : message de limite d'essais", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(json(409, { detail: "max" }));
    renderWs(questionEx);
    fireEvent.change(screen.getByLabelText("Ta réponse"), { target: { value: "x" } });
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(/nombre maximum d'essais/);
  });

  it("erreur réseau : message générique", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("offline"));
    renderWs(questionEx);
    fireEvent.change(screen.getByLabelText("Ta réponse"), { target: { value: "x" } });
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/L'envoi a échoué/));
  });

  it("type non géré : message, pas de plantage", () => {
    renderWs({ ...base, id: 7, type: "E", title: "Graphe", content: {} });
    expect(screen.getByText(/bientôt disponible/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Valider" })).not.toBeInTheDocument();
  });

  const orderEx: ExerciseDetail = {
    ...base, id: 7, type: "C", title: "Ordre C",
    content: {
      prompt: "Remets dans l'ordre",
      items: [{ id: "i1", label: "Event BeginPlay" }, { id: "i2", label: "Print String" }, { id: "i3", label: "Delay" }],
    },
  };

  it("type C : réordonner puis envoyer produit le bon corps", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 33, feedback: ["1 élément(s) sur 3 bien placé(s)."],
        hints: [], attempt_number: 1 }),
    );
    renderWs(orderEx);
    fireEvent.click(await screen.findByRole("button", { name: "Descendre Event BeginPlay" }));
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    expect(await screen.findByText(/Raté · score 33/)).toBeInTheDocument();
    expect(body(spy).submission).toEqual({ order: ["i2", "i1", "i3"] });
  });

  it("type C : affiche le résultat partiel", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 33, feedback: ["1 élément(s) sur 3 bien placé(s)."],
        hints: [], attempt_number: 1 }),
    );
    renderWs(orderEx);
    fireEvent.click(await screen.findByRole("button", { name: "Valider" }));
    expect(await screen.findByText("1 élément(s) sur 3 bien placé(s).")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Réessayer" })).toBeInTheDocument();
  });

  const matchEx: ExerciseDetail = {
    ...base, id: 8, type: "D", title: "Association D",
    content: {
      prompt: "Associe",
      left: [{ id: "l1", label: "Branch" }, { id: "l2", label: "Delay" }],
      right: [{ id: "r2", label: "Attend" }, { id: "r1", label: "Choisit" }],
    },
  };

  it("type D : associer puis envoyer produit le bon corps", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 50, feedback: ["1 paire(s) sur 2 correcte(s)."],
        hints: [], attempt_number: 1 }),
    );
    renderWs(matchEx);
    fireEvent.change(await screen.findByLabelText("Associer Branch à"), { target: { value: "r1" } });
    expect(screen.getByRole("button", { name: "Valider" })).toBeEnabled();
    fireEvent.change(screen.getByLabelText("Associer Delay à"), { target: { value: "r2" } });
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    expect(await screen.findByText(/Raté · score 50/)).toBeInTheDocument();
    expect(screen.getByText("1 paire(s) sur 2 correcte(s).")).toBeInTheDocument();
    expect(body(spy).submission).toEqual({
      pairs: [{ left_id: "l1", right_id: "r1" }, { left_id: "l2", right_id: "r2" }],
    });
  });

  it("type D : un élément de droite ne sert qu'une fois", async () => {
    const spy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      json(200, { is_correct: false, score: 0, feedback: [], hints: [], attempt_number: 1 }),
    );
    renderWs(matchEx);
    fireEvent.change(await screen.findByLabelText("Associer Branch à"), { target: { value: "r1" } });
    fireEvent.change(screen.getByLabelText("Associer Delay à"), { target: { value: "r1" } });
    fireEvent.click(screen.getByRole("button", { name: "Valider" }));
    await screen.findByText(/Raté/);
    expect(body(spy).submission).toEqual({ pairs: [{ left_id: "l2", right_id: "r1" }] });
  });
});
