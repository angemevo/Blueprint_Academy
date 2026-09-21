/**
 * Client API minimal, unique point de sortie vers le backend Django.
 *
 * Choix structurants (voir CLAUDE.md > Auth) :
 * - `credentials: "include"` pour que le cookie httpOnly de refresh circule ;
 * - l'access token restera en memoire (jamais en localStorage) et sera injecte
 *   ici par le store d'auth en Phase 3.
 */

/** URL de base cote navigateur, surchargeable par variable d'environnement. */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

/** URL de base cote serveur Next (SSR / server components, reseau Docker). */
export const INTERNAL_API_BASE_URL =
  process.env.INTERNAL_API_URL ?? API_BASE_URL;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly payload: unknown = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  /** Force l'URL de base (utile depuis un server component). */
  baseUrl?: string;
};

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, baseUrl, headers, ...init } = options;
  const base = baseUrl ?? (typeof window === "undefined" ? INTERNAL_API_BASE_URL : API_BASE_URL);
  const url = `${base.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;

  const response = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      ...headers,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });

  const payload = await parseBody(response);

  if (!response.ok) {
    throw new ApiError(
      `${response.status} ${response.statusText} sur ${path}`,
      response.status,
      payload,
    );
  }

  return payload as T;
}

async function parseBody(response: Response): Promise<unknown> {
  if (response.status === 204) return null;
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) return response.text();
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export const apiClient = {
  get: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "POST", body }),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "PATCH", body }),
  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>(path, { ...options, method: "DELETE" }),
};
