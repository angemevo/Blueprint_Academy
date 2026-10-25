"use client";

import { useMutation } from "@tanstack/react-query";
import { Suspense, lazy, useCallback, useEffect, useRef, useState } from "react";

import { ApiError } from "@/lib/api-client";
import {
  submitExercise,
  type ExerciseDetail,
  type SubmissionPayload,
  type SubmissionResult,
} from "@/lib/exercises";

const LazyOrdering = lazy(() => import("@/components/ordering-input"));
const LazyMatching = lazy(() => import("@/components/matching-input"));

type McqOption = { id: string; text: string };

/** Interface commune des espaces par type : produit une soumission, ou null si incomplète. */
type InputProps = {
  content: Record<string, unknown>;
  disabled: boolean;
  onChange: (submission: SubmissionPayload | null) => void;
};

function QuestionInput({ content, disabled, onChange }: InputProps) {
  return (
    <input
      type="text"
      aria-label="Ta réponse"
      disabled={disabled}
      placeholder={typeof content.placeholder === "string" ? content.placeholder : ""}
      onChange={(e) => onChange(e.target.value.trim() ? { answer: e.target.value } : null)}
      className="w-full rounded border border-surface-2 bg-surface-2 p-2 text-content-primary"
    />
  );
}

function McqInput({ content, disabled, onChange }: InputProps) {
  const options = (content.options as McqOption[] | undefined) ?? [];
  const multiple = content.multiple === true;
  const [selected, setSelected] = useState<string[]>([]);

  const update = (next: string[]) => {
    setSelected(next);
    onChange(next.length ? { selected_option_ids: next } : null);
  };
  const toggle = (id: string) => {
    if (!multiple) return update([id]);
    update(selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id]);
  };

  return (
    <fieldset className="space-y-2">
      <legend className="sr-only">Options</legend>
      {options.map((o) => (
        <label key={o.id} className="flex items-center gap-2 text-content-secondary">
          <input
            type={multiple ? "checkbox" : "radio"}
            name="mcq"
            disabled={disabled}
            checked={selected.includes(o.id)}
            onChange={() => toggle(o.id)}
          />
          {o.text}
        </label>
      ))}
    </fieldset>
  );
}

function OrderingWorkspace({ content, disabled, onChange }: InputProps) {
  const items = (content.items as { id: string; label: string }[] | undefined) ?? [];
  const handle = useCallback((order: string[]) => onChange({ order }), [onChange]);
  return (
    <Suspense fallback={<p role="status" className="text-content-muted">Chargement...</p>}>
      <LazyOrdering items={items} disabled={disabled} onChange={handle} />
    </Suspense>
  );
}

function MatchingWorkspace({ content, disabled, onChange }: InputProps) {
  const left = (content.left as { id: string; label: string }[] | undefined) ?? [];
  const right = (content.right as { id: string; label: string }[] | undefined) ?? [];
  const handle = useCallback(
    (pairs: { left_id: string; right_id: string }[]) =>
      onChange(pairs.length ? { pairs } : null),
    [onChange],
  );
  return (
    <Suspense fallback={<p role="status" className="text-content-muted">Chargement...</p>}>
      <LazyMatching left={left} right={right} disabled={disabled} onChange={handle} />
    </Suspense>
  );
}

const INPUTS: Record<string, (p: InputProps) => React.ReactElement> = {
  A: QuestionInput,
  B: McqInput,
  C: OrderingWorkspace,
  D: MatchingWorkspace,
};

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 409) {
      return "Tu as atteint le nombre maximum d'essais pour cet exercice.";
    }
    if (error.status === 501) return "Ce type d'exercice n'est pas encore disponible.";
  }
  return "L'envoi a échoué. Vérifie ta connexion et réessaie.";
}

/** Espace d'exercice unique : route par type (voir CLAUDE.md > Frontend). */
export function ExerciseWorkspace({ exercise }: { exercise: ExerciseDetail }) {
  const Input = INPUTS[exercise.type];
  const startedAt = useRef<number | null>(null);
  useEffect(() => {
    startedAt.current = Date.now();
  }, []);
  const [submission, setSubmission] = useState<SubmissionPayload | null>(null);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [round, setRound] = useState(0);

  const mutation = useMutation({
    mutationFn: (payload: SubmissionPayload) =>
      submitExercise(
        exercise.id,
        payload,
        Math.round((Date.now() - (startedAt.current ?? Date.now())) / 1000),
      ),
    onSuccess: setResult,
  });

  const retry = () => {
    setResult(null);
    setSubmission(null);
    mutation.reset();
    startedAt.current = Date.now();
    setRound((r) => r + 1);
  };

  const rawQuestion = exercise.content.question ?? exercise.content.prompt;
  const question = typeof rawQuestion === "string" ? rawQuestion : "";

  return (
    <section aria-label="Espace d'exercice" className="py-12">
      <h1 className="text-3xl font-semibold text-content-primary">{exercise.title}</h1>
      {!Input ? (
        <p role="status" className="mt-6 text-content-secondary">
          Ce type d&apos;exercice sera bientôt disponible.
        </p>
      ) : (
        <form
          className="mt-6 space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (submission) mutation.mutate(submission);
          }}
        >
          <p className="text-content-primary">{question}</p>
          <Input
            key={round}
            content={exercise.content}
            disabled={mutation.isPending || result !== null}
            onChange={setSubmission}
          />
          {result === null && (
            <button
              type="submit"
              disabled={!submission || mutation.isPending}
              className="rounded bg-accent px-4 py-2 text-content-primary disabled:opacity-50"
            >
              Valider
            </button>
          )}
        </form>
      )}

      {mutation.isError && (
        <p role="alert" className="mt-4 text-content-secondary">
          {errorMessage(mutation.error)}
        </p>
      )}

      {result && (
        <div role="status" aria-label="Résultat" className="mt-6 space-y-2">
          <p className="font-semibold text-content-primary">
            {result.is_correct ? "Réussi" : "Raté"} · score {result.score}/100
          </p>
          {result.feedback.length > 0 && (
            <ul className="list-disc pl-6 text-content-secondary">
              {result.feedback.map((f, i) => (
                <li key={i}>{f}</li>
              ))}
            </ul>
          )}
          {result.hints.length > 0 && (
            <div>
              <h2 className="text-sm font-semibold text-content-muted">Indices</h2>
              <ul className="list-disc pl-6 text-content-secondary">
                {result.hints.map((h, i) => (
                  <li key={i}>{h}</li>
                ))}
              </ul>
            </div>
          )}
          {!result.is_correct && (
            <button type="button" onClick={retry} className="text-accent hover:underline">
              Réessayer
            </button>
          )}
        </div>
      )}
    </section>
  );
}
