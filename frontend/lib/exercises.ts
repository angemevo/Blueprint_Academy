import { apiClient } from "@/lib/api-client";

export type ExerciseDetail = {
  id: number;
  type: string;
  title: string;
  content: Record<string, unknown>;
  difficulty: string;
  time_limit_seconds: number | null;
  max_attempts: number | null;
  xp_reward: number;
  hints_count: number;
};

export type SubmissionResult = {
  is_correct: boolean;
  score: number;
  feedback: string[];
  hints: string[];
  attempt_number: number;
};

export type SubmissionPayload = Record<string, unknown>;

export const fetchExercise = (id: number) => apiClient.get<ExerciseDetail>(`exercises/${id}/`);

export const submitExercise = (id: number, submission: SubmissionPayload, durationSeconds: number) =>
  apiClient.post<SubmissionResult>(`exercises/${id}/submit/`, {
    submission,
    duration_seconds: durationSeconds,
  });
