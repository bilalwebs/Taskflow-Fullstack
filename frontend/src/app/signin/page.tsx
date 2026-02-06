"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthForm from "@/components/AuthForm";
import Navbar from "@/components/Navbar";
import { setToken, setUser } from "@/lib/auth";
import { useAuth } from "@/lib/auth-context";

/**
 * Signin page - Client Component
 *
 * Handles user authentication with FastAPI backend.
 * On successful signin, stores JWT token and redirects to dashboard.
 * Uses dark theme matching dashboard aesthetic.
 */
export default function SigninPage() {
  const router = useRouter();
  const { setAuth } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handle signin submission
   */
  const handleSignin = async (email: string, password: string) => {
    setIsLoading(true);

    try {
      // Call FastAPI backend signin endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/signin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Signin failed");
      }

      const data = await response.json();

      // Store token and user info
      setToken(data.access_token);
      setUser(data.user);
      setAuth(data.access_token, data.user);

      // Successful signin - redirect to dashboard
      router.push("/dashboard");
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
        <AuthForm mode="signin" onSubmit={handleSignin} isLoading={isLoading} />
      </div>
    </div>
  );
}
