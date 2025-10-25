// This is the root layout component for the Next.js application.
// It defines the main HTML structure, including <html> and <body> tags,
// that will be shared across all pages of the app.
// We also import global styles here.

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Video Editor",
  description: "Edit videos using natural language commands",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
