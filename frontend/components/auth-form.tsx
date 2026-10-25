"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { FormError, login, register, safeNext, type FieldErrors } from "@/lib/auth";

type Mode = "login" | "register";

const inputClass =
  "mt-1 w-full rounded border border-border-subtle bg-surface-1 px-3 py-2 text-content-primary";

function Field(props: {
  name: string;
  label: string;
  type?: string;
  autoComplete: string;
  errors: string[] | undefined;
}) {
  const { name, label, type = "text", autoComplete, errors } = props;
  return (
    <div>
      <label htmlFor={name} className="text-sm text-content-secondary">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        required
        autoComplete={autoComplete}
        aria-invalid={errors ? true : undefined}
        aria-describedby={errors ? `${name}-error` : undefined}
        className={inputClass}
      />
      {errors?.map((message) => (
        <p key={message} id={`${name}-error`} className="mt-1 text-sm text-red-400">
          {message}
        </p>
      ))}
    </div>
  );
}

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const [fields, setFields] = useState<FieldErrors>({});
  const [general, setGeneral] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const isLogin = mode === "login";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const get = (key: string) => String(data.get(key) ?? "");
    setFields({});
    setGeneral(null);
    setPending(true);
    try {
      if (isLogin) {
        await login(get("username"), get("password"));
      } else {
        await register({
          username: get("username"),
          email: get("email"),
          password: get("password"),
        });
      }
      const next = safeNext(new URLSearchParams(window.location.search).get("next"));
      router.replace(next);
    } catch (error) {
      if (error instanceof FormError) {
        setFields(error.fields);
        // Les erreurs globales DRF (non_field_errors, detail) rejoignent le message general.
        const extra = [...(error.fields.non_field_errors ?? []), ...(error.fields.detail ?? [])];
        setGeneral(extra.length > 0 ? extra.join(" ") : error.message);
      } else {
        setGeneral("Une erreur est survenue.");
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="mx-auto max-w-sm py-16">
      <h1 className="text-3xl font-semibold text-content-primary">
        {isLogin ? "Connexion" : "Inscription"}
      </h1>
      <form onSubmit={onSubmit} className="mt-6 space-y-4" noValidate={false}>
        {general && (
          <p role="alert" className="rounded border border-red-400 p-3 text-sm text-red-400">
            {general}
          </p>
        )}
        <Field
          name="username"
          label="Nom d'utilisateur"
          autoComplete="username"
          errors={fields.username}
        />
        {!isLogin && (
          <Field
            name="email"
            label="Email"
            type="email"
            autoComplete="email"
            errors={fields.email}
          />
        )}
        <Field
          name="password"
          label="Mot de passe"
          type="password"
          autoComplete={isLogin ? "current-password" : "new-password"}
          errors={fields.password}
        />
        <button
          type="submit"
          disabled={pending}
          className="w-full rounded bg-accent px-3 py-2 font-medium text-surface-1 disabled:opacity-60"
        >
          {isLogin ? "Se connecter" : "Creer mon compte"}
        </button>
      </form>
      <p className="mt-4 text-sm text-content-secondary">
        {isLogin ? "Pas encore de compte ? " : "Deja inscrit ? "}
        <Link href={isLogin ? "/inscription" : "/connexion"} className="text-accent">
          {isLogin ? "S'inscrire" : "Se connecter"}
        </Link>
      </p>
    </section>
  );
}
