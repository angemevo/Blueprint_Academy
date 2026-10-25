"use client";

import { AuthGuard } from "@/components/auth-guard";
import { PlaceholderPage } from "@/components/placeholder-page";

export default function MonEspacePage() {
  return (
    <AuthGuard>
      <PlaceholderPage title="Mon espace" />
    </AuthGuard>
  );
}
