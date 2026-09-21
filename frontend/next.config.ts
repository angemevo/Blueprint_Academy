import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Sortie autonome : utile pour l'image de production (Phase 7).
  output: "standalone",
};

export default nextConfig;
