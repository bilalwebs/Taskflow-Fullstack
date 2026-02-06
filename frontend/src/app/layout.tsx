import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/lib/theme-context";
import FloatingChatWidget from "@/components/FloatingChatWidget";
import AnimatedBackground from "@/components/AnimatedBackground";
import "./globals.css";

/**
 * Root layout for the application
 *
 * This is a Server Component that wraps all pages.
 * AuthProvider is included to make authentication state
 * available throughout the application.
 * ThemeProvider enables light/dark mode switching.
 * AnimatedBackground provides the full-viewport animated gradient background.
 * FloatingChatWidget is included to show chat button on all pages after auth.
 */

export const metadata: Metadata = {
  title: "TaskFlow - Multi-User Task Management",
  description: "A secure, multi-user todo application built with Next.js and FastAPI",
  keywords: ["todo", "task management", "productivity"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased transition-colors">
        <AnimatedBackground />
        <AuthProvider>
          <ThemeProvider>
            {children}
            <FloatingChatWidget />
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
