"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthForm from "@/components/AuthForm";
import Navbar from "@/components/Navbar";

/**
 * Signup page - Client Component
 *
 * Handles user registration with FastAPI backend.
 * On successful signup, shows success message and redirects to signin.
 * Does NOT auto-login user (professional SaaS pattern).
 * Uses dark theme matching dashboard aesthetic.
 */
export default function SignupPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  /**
   * Handle signup submission
   */
  const handleSignup = async (email: string, password: string) => {
    setIsLoading(true);

    try {
      // Call FastAPI backend signup endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Signup failed");
      }

      // Successful signup - show success message
      setShowSuccess(true);

      // Redirect to signin after 2 seconds
      setTimeout(() => {
        router.push("/signin");
      }, 2000);
    } catch (error) {
      // Re-throw error to be handled by AuthForm
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      <div className="flex min-h-screen items-center justify-center px-4 pt-20">
        {showSuccess && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/80 backdrop-blur-sm animate-slide-up">
            <div className="bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl max-w-md w-full p-8 text-center transition-colors">
              <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-emerald-500/20 mx-auto mb-4">
                <svg
                  className="h-8 w-8 text-emerald-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-2">
                Account Created Successfully!
              </h3>
              <p className="text-gray-300 mb-6">
                Please sign in to continue to your dashboard.
              </p>
              <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
                <svg
                  className="animate-spin h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Redirecting to sign in...
              </div>
            </div>
          </div>
        )}
        <AuthForm mode="signup" onSubmit={handleSignup} isLoading={isLoading} />
      </div>
    </div>
  );
}
