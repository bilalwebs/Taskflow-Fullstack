"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { getToken, getUser, removeToken, User } from "./auth";

/**
 * Authentication context and hooks for client-side auth state management
 *
 * Provides:
 * - Current user session
 * - JWT token for API calls
 * - Loading state
 * - Sign out functionality
 */

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  setAuth: (token: string, user: User) => void;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Auth Provider Component
 *
 * Wraps the application to provide authentication state to all components.
 * Loads session from localStorage on mount.
 */
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Load session from localStorage on mount
   */
  useEffect(() => {
    const storedToken = getToken();
    const storedUser = getUser();

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
    }

    setIsLoading(false);
  }, []);

  /**
   * Set authentication state and persist to localStorage
   */
  const setAuth = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
  };

  /**
   * Sign out user and clear session
   */
  const signOut = () => {
    removeToken();
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, setAuth, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to access authentication context
 *
 * Usage:
 * ```tsx
 * const { user, token, isLoading, setAuth, signOut } = useAuth();
 * ```
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
