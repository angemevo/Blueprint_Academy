"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api-client";

export type HealthResponse = {
  status: string;
};

/** Ping la sonde `GET /api/health/` du backend. */
export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiClient.get<HealthResponse>("/health/"),
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}
