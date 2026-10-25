import { ApiError, apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

export type FieldErrors = Record<string, string[]>;

/** Erreur de formulaire : message general et/ou messages par champ. */
export class FormError extends Error {
  constructor(
    message: string,
    readonly fields: FieldErrors = {},
  ) {
    super(message);
    this.name = "FormError";
  }
}

const GENERIC = "Une erreur est survenue. Reessayez dans un instant.";

/** Extrait les erreurs par champ d'une reponse 400 de DRF. */
function toFormError(error: unknown, unauthorizedMessage?: string): FormError {
  if (!(error instanceof ApiError)) {
    return new FormError("Impossible de joindre le serveur. Verifiez votre connexion.");
  }
  if (error.status === 401 && unauthorizedMessage) {
    return new FormError(unauthorizedMessage);
  }
  const payload = error.payload;
  if (error.status === 400 && payload && typeof payload === "object") {
    const fields: FieldErrors = {};
    for (const [key, value] of Object.entries(payload as Record<string, unknown>)) {
      const list = Array.isArray(value) ? value : [value];
      fields[key] = list.filter((v): v is string => typeof v === "string");
    }
    return new FormError("Certains champs sont invalides.", fields);
  }
  return new FormError(GENERIC);
}

export async function login(username: string, password: string): Promise<void> {
  try {
    const { access } = await apiClient.post<{ access: string }>("auth/login/", {
      username,
      password,
    });
    useAuthStore.getState().setAccessToken(access);
  } catch (error) {
    throw toFormError(error, "Nom d'utilisateur ou mot de passe incorrect.");
  }
}

export async function register(input: {
  username: string;
  email: string;
  password: string;
}): Promise<void> {
  try {
    await apiClient.post("auth/register/", input);
  } catch (error) {
    throw toFormError(error);
  }
  await login(input.username, input.password);
}

/** N'accepte qu'un chemin interne, pour eviter une redirection ouverte. */
export function safeNext(raw: string | null): string {
  return raw && raw.startsWith("/") && !raw.startsWith("//") ? raw : "/mon-espace";
}
