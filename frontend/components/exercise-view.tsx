"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { ExerciseWorkspace } from "@/components/exercise-workspace";
import { fetchExercise } from "@/lib/exercises";

export function ExerciseView({
  pathSlug,
  lessonId,
  exerciseId,
}: {
  pathSlug: string;
  lessonId: number;
  exerciseId: number;
}) {
  const exercise = useQuery({
    queryKey: ["exercise", exerciseId],
    queryFn: () => fetchExercise(exerciseId),
  });

  return (
    <div>
      <Link
        href={`/catalogue/${pathSlug}/lecons/${lessonId}`}
        className="mt-8 inline-block text-sm text-accent hover:underline"
      >
        Retour à la leçon
      </Link>
      {exercise.isPending && <p role="status" className="p-8 text-content-muted">Chargement...</p>}
      {exercise.isError && (
        <p role="alert" className="py-12 text-content-secondary">
          Impossible d&apos;afficher cet exercice (introuvable ou non accessible).
        </p>
      )}
      {exercise.data && <ExerciseWorkspace exercise={exercise.data} />}
    </div>
  );
}
