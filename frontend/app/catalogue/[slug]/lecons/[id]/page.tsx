"use client";

import { notFound } from "next/navigation";
import { use } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { LessonView } from "@/components/lesson-view";

type Props = { params: Promise<{ slug: string; id: string }> };

export default function LessonPage({ params }: Props) {
  const { slug, id } = use(params);
  const lessonId = Number(id);
  if (!Number.isInteger(lessonId) || lessonId <= 0) notFound();
  return (
    <AuthGuard>
      <LessonView pathSlug={slug} lessonId={lessonId} />
    </AuthGuard>
  );
}
