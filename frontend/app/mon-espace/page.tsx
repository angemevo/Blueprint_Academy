"use client";

import { AuthGuard } from "@/components/auth-guard";
import { DashboardView } from "@/components/dashboard-view";

export default function MonEspacePage() {
  return (
    <AuthGuard>
      <DashboardView />
    </AuthGuard>
  );
}
