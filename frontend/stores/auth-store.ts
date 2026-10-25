import { create } from "zustand";

/**
 * Etat de session cote client.
 *
 * Le jeton d'acces vit uniquement en memoire (jamais en localStorage) ; le
 * refresh token reste dans le cookie httpOnly gere par le backend.
 * - `unknown`   : session pas encore verifiee (premier chargement) ;
 * - `anonymous` : visiteur ;
 * - `authenticated` : jeton d'acces valide en memoire.
 */
export type SessionStatus = "unknown" | "anonymous" | "authenticated";

type AuthState = {
  accessToken: string | null;
  status: SessionStatus;
  setAccessToken: (token: string) => void;
  clear: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  status: "unknown",
  setAccessToken: (token) => set({ accessToken: token, status: "authenticated" }),
  clear: () => set({ accessToken: null, status: "anonymous" }),
}));
