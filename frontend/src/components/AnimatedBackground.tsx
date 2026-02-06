"use client";

/**
 * AnimatedBackground Component
 *
 * Full-viewport animated background with multiple radial gradient layers.
 * Creates a professional SaaS look similar to Linear.app, Vercel.com, Relume.io.
 *
 * Features:
 * - Multiple animated radial gradient layers (purple, indigo, blue)
 * - Slow, smooth movement (20-40s loops)
 * - GPU-optimized (uses transform and opacity)
 * - Fixed position behind all content
 */

export default function AnimatedBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0B1120] via-[#0F172A] to-[#020617]"></div>

      {/* Animated gradient layer 1 - Purple glow */}
      <div className="absolute top-0 -left-1/4 w-1/2 h-1/2 bg-purple-600/20 rounded-full blur-3xl animate-glow-1"></div>

      {/* Animated gradient layer 2 - Indigo glow */}
      <div className="absolute top-1/4 right-0 w-1/2 h-1/2 bg-indigo-600/20 rounded-full blur-3xl animate-glow-2"></div>

      {/* Animated gradient layer 3 - Blue glow */}
      <div className="absolute bottom-0 left-1/3 w-1/2 h-1/2 bg-blue-600/15 rounded-full blur-3xl animate-glow-3"></div>

      {/* Additional subtle glow - Purple */}
      <div className="absolute top-1/2 left-1/4 w-1/3 h-1/3 bg-purple-500/10 rounded-full blur-2xl animate-glow-4"></div>

      {/* Additional subtle glow - Indigo */}
      <div className="absolute bottom-1/4 right-1/4 w-1/3 h-1/3 bg-indigo-500/10 rounded-full blur-2xl animate-glow-5"></div>
    </div>
  );
}
