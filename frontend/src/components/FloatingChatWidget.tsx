"use client";

import { useState } from "react";
import { ChatInterface } from "@/components/ChatInterface";
import { useAuth } from "@/lib/auth-context";
import AuthModal from "@/components/AuthModal";

/**
 * FloatingChatWidget Component
 *
 * Intercom-style floating chat widget that:
 * - Shows a floating button in bottom-right corner (always visible)
 * - Opens AuthModal if user is not authenticated
 * - Opens chat panel if user is authenticated
 * - Includes slide-up animation
 * - Responsive (bottom sheet on mobile)
 */

export default function FloatingChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [key, setKey] = useState(0);
  const { user } = useAuth();

  const handleNewConversation = () => {
    setConversationId(null);
    setKey((prev) => prev + 1);
  };

  const handleChatButtonClick = () => {
    if (user) {
      // User is authenticated - open chat
      setIsOpen(true);
    } else {
      // User is not authenticated - open auth modal
      setAuthModalOpen(true);
    }
  };

  const handleAuthSuccess = () => {
    // After successful authentication, open the chat
    setIsOpen(true);
  };

  return (
    <>
      {/* Auth Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={handleChatButtonClick}
          className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-gradient-to-br from-purple-600 to-indigo-600 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-200 flex items-center justify-center animate-pulse-soft"
          aria-label="Open chat assistant"
        >
          <svg
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </button>
      )}

      {/* Chat Panel - Only show if user is authenticated */}
      {isOpen && user && (
        <div className="fixed bottom-6 right-6 z-50 w-[400px] h-[600px] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-3rem)] md:max-h-[600px] animate-slide-up">
          <div className="h-full flex flex-col bg-gradient-to-br from-[#111827] to-[#1F2937] border border-purple-500/30 rounded-2xl shadow-2xl overflow-hidden">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-white/20 flex items-center justify-center">
                  <svg
                    className="h-6 w-6 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                    />
                  </svg>
                </div>
                <div>
                  <h3 className="text-white font-semibold text-sm">TaskFlow Assistant</h3>
                  <p className="text-white/80 text-xs flex items-center gap-1">
                    <span className="h-2 w-2 bg-emerald-400 rounded-full"></span>
                    Online
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors"
                aria-label="Close chat"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Chat Interface */}
            <div className="flex-1 overflow-hidden bg-[#0B1120]">
              <ChatInterface
                key={key}
                conversationId={conversationId || undefined}
                onConversationCreated={setConversationId}
              />
            </div>

            {/* Quick Actions Footer */}
            <div className="px-4 py-2 bg-[#111827] border-t border-[#1F2937]">
              <button
                onClick={handleNewConversation}
                className="text-xs text-purple-400 hover:text-purple-300 font-medium flex items-center gap-1"
              >
                <svg
                  className="h-3 w-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                New conversation
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
