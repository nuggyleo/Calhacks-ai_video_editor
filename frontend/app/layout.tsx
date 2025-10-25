// This is the root layout component for the Next.js application.
// It defines the main HTML structure, including <html> and <body> tags,
// that will be shared across all pages of the app.
// We also import global styles here.

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Lobster } from "next/font/google";
import "./globals.css";
import AuthProvider from "@/components/auth/AuthProvider";

const inter = Inter({ subsets: ["latin"] });

const lobster = Lobster({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-lobster",
});

export const metadata: Metadata = {
  title: "AI Video Editor",
  description: "Edit videos with the power of conversation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} ${lobster.variable}`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
