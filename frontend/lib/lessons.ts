import { apiClient } from "@/lib/api-client";
import { fetchPath, type LessonTitle, type PathDetail } from "@/lib/catalogue";

export type SkillRef = { id: number; name: string; slug: string };
export type ExerciseItem = { id: number; title: string; type: string };

export type ContentBlock = { type: string } & Record<string, unknown>;

export type LessonDetail = {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: { version?: number; blocks?: ContentBlock[] } | null;
  estimated_minutes: number | null;
  module_id: number;
  skills_taught: SkillRef[];
  exercises: ExerciseItem[];
};

export const fetchLesson = (id: number) => apiClient.get<LessonDetail>(`lessons/${id}/`);

export type LessonNav = {
  moduleTitle: string;
  previous: LessonTitle | null;
  next: LessonTitle | null;
};

/** Voisins d'une leçon dans son module (null si le module est introuvable). */
export function lessonNeighbours(
  path: PathDetail,
  moduleId: number,
  lessonId: number,
): LessonNav | null {
  const mod = path.modules.find((m) => m.id === moduleId);
  if (!mod) return null;
  const index = mod.lessons.findIndex((l) => l.id === lessonId);
  if (index === -1) return null;
  return {
    moduleTitle: mod.title,
    previous: mod.lessons[index - 1] ?? null,
    next: mod.lessons[index + 1] ?? null,
  };
}

export { fetchPath };
