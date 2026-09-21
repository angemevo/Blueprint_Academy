import type { Metadata } from "next";

import { AppProviders } from "./providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "Blueprint Academy",
  description:
    "Apprendre Unreal Engine Blueprint en pratiquant : lecons, exercices, projets.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body className="min-h-screen font-sans antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
