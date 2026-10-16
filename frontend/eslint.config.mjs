// Configuration ESLint plate : règles Next.js (Core Web Vitals) et TypeScript.
import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

export default defineConfig([
  ...nextVitals,
  ...nextTs,
  // Fichiers générés : ni écrits ni relus à la main.
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);
