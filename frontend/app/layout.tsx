import type { Metadata } from "next";

import { Navbar } from "@/components/navbar";
import { SessionProvider } from "@/components/session-provider";
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
        <AppProviders>
          <SessionProvider>
            <Navbar />
            <main className="mx-auto max-w-5xl px-4 sm:px-6">{children}</main>
          </SessionProvider>
        </AppProviders>
      </body>
    </html>
  );
}
