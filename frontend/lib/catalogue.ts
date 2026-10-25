import { apiClient, ApiError } from "@/lib/api-client";

export type PathSummary = {
  id: number;
  title: string;
  slug: string;
  subtitle: string;
  description: string;
  difficulty: string;
  estimated_hours: number | null;
  order: number;
};

export type LessonTitle = {
  id: number;
  title: string;
  slug: string;
  summary: string;
  order: number;
  estimated_minutes: number | null;
};

export type ModuleOutline = {
  id: number;
  title: string;
  slug: string;
  description: string;
  order: number;
  lessons: LessonTitle[];
};

export type PathDetail = PathSummary & { modules: ModuleOutline[] };

/** Revalidation ISR : la vitrine est rendue cote serveur puis mise en cache. */
const REVALIDATE = { next: { revalidate: 60 } } as RequestInit;

const byOrder = <T extends { order: number }>(items: T[]) =>
  [...items].sort((a, b) => a.order - b.order);

/** Liste publique des parcours (reponse paginee ou simple tableau). */
export async function fetchPaths(): Promise<PathSummary[]> {
  const data = await apiClient.get<PathSummary[] | { results: PathSummary[] }>(
    "learning-paths/",
    REVALIDATE,
  );
  const items = Array.isArray(data) ? data : data.results;
  return byOrder(items);
}

/** Detail d'un parcours, ou null s'il n'existe pas / n'est pas publie. */
export async function fetchPath(slug: string): Promise<PathDetail | null> {
  try {
    const path = await apiClient.get<PathDetail>(
      `learning-paths/${encodeURIComponent(slug)}/`,
      REVALIDATE,
    );
    return {
      ...path,
      modules: byOrder(path.modules).map((m) => ({
        ...m,
        lessons: byOrder(m.lessons),
      })),
    };
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}
