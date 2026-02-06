import Link from "next/link";
import Navbar from "@/components/Navbar";

/**
 * Landing page - Server Component
 *
 * Modern dark-themed landing page with:
 * - Purple gradient hero section
 * - Glassmorphism feature cards
 * - Professional design
 */
export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navbar />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto text-center">
          {/* Hero Text */}
          <h1 className="text-6xl md:text-7xl font-bold text-white dark:text-white light:text-gray-900 mb-6 leading-tight transition-colors">
            Organize Your Life,{" "}
            <span className="bg-gradient-to-r from-purple-500 to-indigo-500 bg-clip-text text-transparent">
              Effortlessly
            </span>
          </h1>

          <p className="text-xl text-gray-300 dark:text-gray-300 light:text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed transition-colors">
            The most intuitive task management app designed for modern professionals.
            Stay focused, organized, and productive.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/signup"
              className="px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all shadow-2xl hover:shadow-purple-500/50 hover:scale-105"
            >
              Create an account
            </Link>
            <Link
              href="/signin"
              className="px-8 py-4 text-lg font-semibold text-white dark:text-white light:text-purple-600 border-2 border-purple-500 rounded-xl hover:bg-purple-500/10 transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-white dark:text-white light:text-gray-900 text-center mb-16 transition-colors">
            Everything you need to stay productive
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Feature Card 1 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              <div className="relative bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center mb-4">
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
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white dark:text-white light:text-gray-900 mb-2 transition-colors">Intuitive Dashboard</h3>
                <p className="text-gray-400 dark:text-gray-400 light:text-gray-600 text-sm leading-relaxed transition-colors">
                  Beautiful, easy-to-use interface that makes task management a breeze.
                </p>
              </div>
            </div>

            {/* Feature Card 2 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              <div className="relative bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mb-4">
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
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white dark:text-white light:text-gray-900 mb-2 transition-colors">Lightning Fast</h3>
                <p className="text-gray-300 dark:text-gray-300 light:text-gray-600 text-sm leading-relaxed transition-colors">
                  Blazing fast performance with real-time sync across all your devices.
                </p>
              </div>
            </div>

            {/* Feature Card 3 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              <div className="relative bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-600 to-indigo-600 flex items-center justify-center mb-4">
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
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white dark:text-white light:text-gray-900 mb-2 transition-colors">Secure & Private</h3>
                <p className="text-gray-300 dark:text-gray-300 light:text-gray-600 text-sm leading-relaxed transition-colors">
                  Your data is encrypted and protected with industry-standard security.
                </p>
              </div>
            </div>

            {/* Feature Card 4 */}
            <div className="group relative">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-40 transition-opacity"></div>
              <div className="relative bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-purple-500/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center mb-4">
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
                      d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                    />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-white dark:text-white light:text-gray-900 mb-2 transition-colors">Beautiful Design</h3>
                <p className="text-gray-300 dark:text-gray-300 light:text-gray-600 text-sm leading-relaxed transition-colors">
                  Stunning dark theme interface that's easy on the eyes and looks amazing.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-indigo-600/20 blur-3xl"></div>
            <div className="relative bg-[#111827]/60 backdrop-blur-xl border border-white/10 rounded-3xl p-12 transition-colors">
              <h2 className="text-4xl font-bold text-white dark:text-white light:text-gray-900 mb-4 transition-colors">
                Ready to boost your productivity?
              </h2>
              <p className="text-xl text-gray-300 dark:text-gray-300 light:text-gray-600 mb-8 transition-colors">
                Join thousands of users who organize their life with TaskFlow
              </p>
              <Link
                href="/signup"
                className="inline-block px-10 py-4 text-lg font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all shadow-2xl hover:shadow-purple-500/50 hover:scale-105"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-white/10 transition-colors">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-gray-300 dark:text-gray-300 light:text-gray-600 text-sm transition-colors">
            © 2026 TaskFlow. Built with Next.js, FastAPI, and PostgreSQL.
          </p>
        </div>
      </footer>
    </div>
  );
}
