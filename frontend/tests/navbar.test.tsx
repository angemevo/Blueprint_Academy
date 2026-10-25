import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { Navbar } from "@/components/navbar";
import { useAuthStore } from "@/stores/auth-store";

vi.mock("next/link", () => ({
  default: ({ href, children, ...rest }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...rest}>{children}</a>
  ),
}));

describe("Navbar", () => {
  beforeEach(() => useAuthStore.setState({ accessToken: null, status: "anonymous" }));

  it("propose la connexion a un visiteur", () => {
    render(<Navbar />);
    expect(screen.getByText("Connexion")).toBeInTheDocument();
    expect(screen.getByText("Catalogue")).toBeInTheDocument();
    expect(screen.queryByText("Mon espace")).not.toBeInTheDocument();
  });

  it("propose Mon espace a un connecte", () => {
    useAuthStore.getState().setAccessToken("tok");
    render(<Navbar />);
    expect(screen.getByText("Mon espace")).toBeInTheDocument();
    expect(screen.queryByText("Connexion")).not.toBeInTheDocument();
  });
});
