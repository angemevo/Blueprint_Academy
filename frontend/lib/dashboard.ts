import { apiClient } from "@/lib/api-client";

export type Dashboard = {
  total_xp: number;
  level: number;
  next_level_xp: number | null;
  xp_to_next_level: number | null;
  current_paths: { id: number; slug: string; title: string; completion_percent: number }[];
  next_lesson: { id: number; title: string } | null;
  recent_attempts: {
    id: number;
    exercise: { id: number; title: string; type: string };
    is_correct: boolean;
    score: number;
    attempt_number: number;
    created_at: string;
  }[];
  skills: { id: number; name: string; mastery_score: number; is_mastered: boolean }[];
};

export const fetchDashboard = () => apiClient.get<Dashboard>("progress/dashboard/");
