"use client";

import { notFound } from "next/navigation";
import { use } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { ExerciseView } from "@/components/exercise-view";

type Props = { params: Promise<{ slug: string; id: string; exerciseId: string }> };

export default function ExercisePage({ params }: Props) {
  const { slug, id, exerciseId } = use(params);
  const lessonId = Number(id);
  const exId = Number(exerciseId);
  if (!Number.isInteger(lessonId) || lessonId <= 0 || !Number.isInteger(exId) || exId <= 0) {
    notFound();
  }
  return (
    <AuthGuard>
      <ExerciseView pathSlug={slug} lessonId={lessonId} exerciseId={exId} />
    </AuthGuard>
  );
}
