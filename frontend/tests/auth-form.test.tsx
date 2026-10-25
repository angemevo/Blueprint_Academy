import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthForm } from "@/components/auth-form";
import { logout } from "@/lib/session";
import { useAuthStore } from "@/stores/auth-store";

const replace = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: React.ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));

const json = (status: number, body: unknown) =>
  new Response(body === null ? null : JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });

function fill(values: Record<string, string>) {
  for (const [label, value] of Object.entries(values)) {
    fireEvent.change(screen.getByLabelText(label), { target: { value } });
  }
}

describe("AuthForm", () => {
  beforeEach(() => {
    replace.mockClear();
    useAuthStore.setState({ accessToken: null, status: "anonymous" });
    vi.restoreAllMocks();
  });

  it("inscrit puis connecte, et redirige vers l'espace", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(json(201, { id: 1 }))
      .mockResolvedValueOnce(json(200, { access: "tok" }));
    render(<AuthForm mode="register" />);
    fill({ "Nom d'utilisateur": "ange", Email: "a@b.fr", "Mot de passe": "Secret-12345" });
    fireEvent.click(screen.getByRole("button", { name: "Creer mon compte" }));
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/mon-espace"));
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain("auth/register/");
    expect(String(fetchMock.mock.calls[1]?.[0])).toContain("auth/login/");
    expect(useAuthStore.getState().status).toBe("authenticated");
  });

  it("affiche les erreurs du serveur sous le bon champ", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      json(400, { email: ["Cet email est deja utilise."], password: ["Mot de passe trop court."] }),
    );
    render(<AuthForm mode="register" />);
    fill({ "Nom d'utilisateur": "ange", Email: "a@b.fr", "Mot de passe": "abc" });
    fireEvent.click(screen.getByRole("button", { name: "Creer mon compte" }));
    const email = await screen.findByText("Cet email est deja utilise.");
    expect(email.id).toBe("email-error");
    expect(screen.getByText("Mot de passe trop court.").id).toBe("password-error");
    expect(replace).not.toHaveBeenCalled();
  });

  it("indique des identifiants faux en francais", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(json(401, { detail: "No active account" }));
    render(<AuthForm mode="login" />);
    fill({ "Nom d'utilisateur": "ange", "Mot de passe": "mauvais" });
    fireEvent.click(screen.getByRole("button", { name: "Se connecter" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Nom d'utilisateur ou mot de passe incorrect.",
    );
  });

  it("la deconnexion efface la session", async () => {
    useAuthStore.getState().setAccessToken("tok");
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(json(204, null));
    await logout();
    expect(useAuthStore.getState().status).toBe("anonymous");
    expect(useAuthStore.getState().accessToken).toBeNull();
  });
});
