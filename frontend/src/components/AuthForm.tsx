"use client";

import { useState, FormEvent } from "react";
import ErrorModal from "./ErrorModal";

/**
 * Reusable authentication form component
 *
 * Client Component - handles user interactions and form validation.
 * Used by both signup and signin pages.
 */

interface AuthFormProps {
  mode: "signup" | "signin";
  onSubmit: (email: string, password: string) => Promise<void>;
  isLoading?: boolean;
}

interface ValidationErrors {
  email?: string;
  password?: string;
}

/**
 * Validate email format
 */
function validateEmail(email: string): string | undefined {
  if (!email) {
    return "Email is required";
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return "Please enter a valid email address";
  }

  return undefined;
}

/**
 * Validate password strength
 * Requirements: min 8 chars, uppercase, lowercase, number
 */
function validatePassword(password: string, mode: "signup" | "signin"): string | undefined {
  if (!password) {
    return "Password is required";
  }

  // Only enforce strength requirements for signup
  if (mode === "signup") {
    if (password.length < 8) {
      return "Password must be at least 8 characters long";
    }

    if (!/[A-Z]/.test(password)) {
      return "Password must contain at least one uppercase letter";
    }

    if (!/[a-z]/.test(password)) {
      return "Password must contain at least one lowercase letter";
    }

    if (!/[0-9]/.test(password)) {
      return "Password must contain at least one number";
    }
  }

  return undefined;
}

export default function AuthForm({ mode, onSubmit, isLoading = false }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [submitError, setSubmitError] = useState<string>("");
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [serverError, setServerError] = useState<string>("");

  /**
   * Parse backend error and convert to user-friendly message
   */
  const parseServerError = (error: Error): { message: string; field?: "email" | "password" } => {
    const errorMessage = error.message.toLowerCase();

    // Email already exists
    if (errorMessage.includes("email") && (errorMessage.includes("already") || errorMessage.includes("exists") || errorMessage.includes("registered"))) {
      return {
        message: "This email is already registered.",
        field: "email"
      };
    }

    // Invalid credentials
    if (errorMessage.includes("invalid") && (errorMessage.includes("credentials") || errorMessage.includes("password"))) {
      return {
        message: "Invalid email or password. Please try again.",
        field: undefined
      };
    }

    // User not found
    if (errorMessage.includes("not found") || errorMessage.includes("does not exist")) {
      return {
        message: "No account found with this email.",
        field: "email"
      };
    }

    // Generic invalid data
    if (errorMessage.includes("invalid data") || errorMessage.includes("validation")) {
      return {
        message: mode === "signup"
          ? "Please check your information and try again."
          : "Invalid email or password.",
        field: undefined
      };
    }

    // Network errors
    if (errorMessage.includes("network") || errorMessage.includes("fetch")) {
      return {
        message: "Connection error. Please check your internet and try again.",
        field: undefined
      };
    }

    // Default fallback
    return {
      message: mode === "signup"
        ? "Unable to create account. Please try again."
        : "Unable to sign in. Please try again.",
      field: undefined
    };
  };

  /**
   * Handle form submission with validation
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});
    setSubmitError("");
    setShowErrorModal(false);
    setServerError("");

    // Validate inputs
    const emailError = validateEmail(email);
    const passwordError = validatePassword(password, mode);

    if (emailError || passwordError) {
      setErrors({
        email: emailError,
        password: passwordError,
      });
      return;
    }

    // Submit form
    try {
      await onSubmit(email, password);
    } catch (error) {
      const parsedError = parseServerError(error as Error);

      if (parsedError.field) {
        // Show field-level error
        setErrors({
          [parsedError.field]: parsedError.message
        });
        setServerError(parsedError.message);
      } else {
        // Show modal for general errors
        setSubmitError(parsedError.message);
        setShowErrorModal(true);
      }
    }
  };

  /**
   * Clear errors when user types
   */
  const handleEmailChange = (value: string) => {
    setEmail(value);
    if (errors.email || serverError) {
      setErrors({ ...errors, email: undefined });
      setServerError("");
    }
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    if (errors.password) {
      setErrors({ ...errors, password: undefined });
    }
  };

  const isSignup = mode === "signup";
  const title = isSignup ? "Create Account" : "Sign In";
  const submitText = isSignup ? "Sign Up" : "Sign In";
  const alternateText = isSignup ? "Already have an account?" : "Don't have an account?";
  const alternateLink = isSignup ? "/signin" : "/signup";
  const alternateLinkText = isSignup ? "Sign In" : "Sign Up";

  return (
    <>
      {/* Error Modal */}
      <ErrorModal
        isOpen={showErrorModal}
        title={isSignup ? "Unable to Create Account" : "Unable to Sign In"}
        message={submitError}
        onClose={() => setShowErrorModal(false)}
      />

      <div className="w-full max-w-md mx-auto">
        <div className="bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl p-8 transition-colors">
          {/* Header */}
          <div className="mb-8 text-center">
            <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gradient-to-br from-purple-600 to-indigo-600 mb-4">
              <svg
                className="h-8 w-8 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-white transition-colors">{title}</h2>
            <p className="mt-2 text-gray-300 transition-colors">
              {isSignup ? "Start managing your tasks today" : "Welcome back to TaskFlow"}
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-300 mb-2 transition-colors">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => handleEmailChange(e.target.value)}
                disabled={isLoading}
                className={`w-full px-4 py-3 border rounded-xl focus:ring-2 transition-all text-white placeholder:text-gray-500 bg-[#0B1120]/80 ${
                  errors.email
                    ? "border-red-500 bg-red-500/10 focus:ring-red-500 focus:border-red-500"
                    : "border-white/10 focus:ring-purple-500 focus:border-purple-500"
                } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && (
                <div className="mt-2 space-y-1">
                  <p className="text-sm text-red-400 font-medium flex items-center gap-1">
                    <svg className="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {errors.email}
                  </p>
                  {serverError && serverError.includes("already registered") && (
                    <p className="text-xs text-gray-400 ml-5">
                      Please{" "}
                      <a href="/signin" className="text-purple-400 hover:text-purple-300 font-semibold">
                        sign in
                      </a>
                      {" "}or use a different email.
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-300 mb-2 transition-colors">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                disabled={isLoading}
                className={`w-full px-4 py-3 border rounded-xl focus:ring-2 transition-all text-white placeholder:text-gray-500 bg-[#0B1120]/80 ${
                  errors.password
                    ? "border-red-500 bg-red-500/10 focus:ring-red-500 focus:border-red-500"
                    : "border-white/10 focus:ring-purple-500 focus:border-purple-500"
                } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
                placeholder={isSignup ? "Create a strong password" : "Enter your password"}
                autoComplete={isSignup ? "new-password" : "current-password"}
              />
              {errors.password && (
                <p className="mt-2 text-sm text-red-400 font-medium flex items-center gap-1">
                  <svg className="h-4 w-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {errors.password}
                </p>
              )}
              {isSignup && !errors.password && (
                <p className="mt-2 text-xs text-gray-400 transition-colors">
                  Must be at least 8 characters with uppercase, lowercase, and number
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-3 px-4 rounded-xl font-semibold text-white transition-all shadow-lg ${
                isLoading
                  ? "bg-gray-600 cursor-not-allowed"
                  : "bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 hover:shadow-purple-500/50"
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                submitText
              )}
            </button>
          </form>

          {/* Alternate Action */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-300 transition-colors">
              {alternateText}{" "}
              <a href={alternateLink} className="text-purple-400 hover:text-purple-300 font-semibold">
                {alternateLinkText}
              </a>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
