import { apiClient, setAccessTokenProvider } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

// Branche le jeton en memoire sur le client d'API.
setAccessTokenProvider(() => useAuthStore.getState().accessToken);

/** Tente de retrouver la session via le cookie httpOnly de refresh. */
export async function restoreSession(): Promise<void> {
  try {
    const { access } = await apiClient.post<{ access: string }>("auth/refresh/");
    useAuthStore.getState().setAccessToken(access);
  } catch {
    useAuthStore.getState().clear();
  }
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post("auth/logout/");
  } finally {
    useAuthStore.getState().clear();
  }
}
