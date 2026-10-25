"use client";

import Link from "next/link";

import { logout } from "@/lib/session";
import { useAuthStore } from "@/stores/auth-store";

const linkClass =
  "rounded px-3 py-2 text-sm text-content-secondary transition hover:text-content-primary";

export function Navbar() {
  const status = useAuthStore((s) => s.status);

  return (
    <header className="border-b border-border-subtle bg-surface-1/90 backdrop-blur">
      <nav
        aria-label="Navigation principale"
        className="mx-auto flex max-w-5xl flex-wrap items-center gap-1 px-4 py-2"
      >
        <Link
          href="/"
          className="mr-auto font-mono text-sm font-semibold tracking-wide text-accent"
        >
          Blueprint Academy
        </Link>
        <Link href="/" className={linkClass}>
          Accueil
        </Link>
        <Link href="/catalogue" className={linkClass}>
          Catalogue
        </Link>
        {status === "authenticated" ? (
          <>
            <Link href="/mon-espace" className={linkClass}>
              Mon espace
            </Link>
            <button type="button" className={linkClass} onClick={() => void logout()}>
              Deconnexion
            </button>
          </>
        ) : (
          <>
            <Link href="/connexion" className={linkClass}>
              Connexion
            </Link>
            <Link href="/inscription" className={linkClass}>
              Inscription
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
