import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthGuard } from "@/components/auth-guard";
import { useAuthStore } from "@/stores/auth-store";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/mon-espace",
}));

describe("AuthGuard", () => {
  beforeEach(() => replace.mockClear());

  it("redirige un visiteur vers la connexion", () => {
    useAuthStore.setState({ accessToken: null, status: "anonymous" });
    render(<AuthGuard>secret</AuthGuard>);
    expect(replace).toHaveBeenCalledWith("/connexion?next=%2Fmon-espace");
    expect(screen.queryByText("secret")).not.toBeInTheDocument();
  });

  it("attend la verification de session sans rediriger", () => {
    useAuthStore.setState({ accessToken: null, status: "unknown" });
    render(<AuthGuard>secret</AuthGuard>);
    expect(replace).not.toHaveBeenCalled();
  });

  it("affiche la page a un connecte", () => {
    useAuthStore.setState({ accessToken: "t", status: "authenticated" });
    render(<AuthGuard>secret</AuthGuard>);
    expect(screen.getByText("secret")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });
});
