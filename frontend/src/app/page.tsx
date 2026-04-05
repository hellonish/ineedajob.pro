'use client';

import { useEffect, useState } from 'react';
import { useStore } from '@/utils/store';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const { theme, toggleTheme, token, _hasHydrated, fetchUser, isAuthenticated } = useStore();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Restore session if we have token but not authenticated
  useEffect(() => {
    if (_hasHydrated && token && !isAuthenticated) {
      fetchUser();
    }
    // Redirect to dashboard if already logged in
    if (_hasHydrated && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [_hasHydrated, token, isAuthenticated, fetchUser, router]);

  const handleGoogleLogin = () => {
    window.location.href = 'http://localhost:8000/api/auth/google';
  };

  return (
    <main className="relative min-h-screen flex overflow-hidden">
      {/* Animated Background Orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Theme Toggle - Top Right */}
      {mounted && (
        <button
          onClick={toggleTheme}
          className="absolute top-4 right-4 z-20 !p-2 rounded-lg bg-[var(--card-bg)] hover:opacity-80 border border-[var(--border-color)] transition-colors"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? (
            <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </button>
      )}

      {/* Left Side - Features */}
      <div className="hidden lg:flex flex-1 flex-col justify-center !px-16 !py-12 relative z-10">
        <div className="max-w-lg">
          <h1 className="text-6xl font-bold !mb-6 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Wand
          </h1>
          <p className="text-2xl text-[var(--text-secondary)] !mb-12 leading-relaxed">
            Your AI-powered career companion that helps you land your dream job.
          </p>

          {/* Feature List */}
          <div className="space-y-6">
            <div className="flex items-start !gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] !mb-1">Match Score Analysis</h3>
                <p className="text-[var(--text-secondary)]">Instantly see how well your resume matches any job posting with AI-powered analysis.</p>
              </div>
            </div>

            <div className="flex items-start !gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] !mb-1">Smart Resume Suggestions</h3>
                <p className="text-[var(--text-secondary)]">Get personalized recommendations to improve your resume for each specific role.</p>
              </div>
            </div>

            <div className="flex items-start !gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-pink-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] !mb-1">Tailored Cover Letters</h3>
                <p className="text-[var(--text-secondary)]">Generate compelling cover letters customized for each job application.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login */}
      <div className="flex-1 flex flex-col items-center justify-center !px-8 !py-12 relative z-10">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center !mb-10">
            <h1 className="text-5xl font-bold !mb-3 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Wand
            </h1>
            <p className="text-lg text-[var(--text-secondary)]">
              Your AI-powered career companion
            </p>
          </div>

          {/* Login Card */}
          <div className="bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-3xl shadow-2xl !p-8">
            <div className="text-center !mb-8">
              <h2 className="text-2xl font-bold text-[var(--text-primary)] !mb-2">
                Get Started
              </h2>
              <p className="text-[var(--text-secondary)]">
                Sign in to analyze your resume and find your perfect job match
              </p>
            </div>

            {/* Google Button - Prominent */}
            <button
              onClick={handleGoogleLogin}
              className="flex items-center justify-center !gap-3 w-full !py-4 !px-6 bg-white text-gray-800 font-semibold text-base rounded-xl shadow-lg hover:-translate-y-0.5 hover:shadow-xl transition-all cursor-pointer border border-gray-200"
            >
              <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Continue with Google
            </button>

            <div className="!mt-6 text-center">
              <p className="text-sm text-[var(--text-muted)]">
                By continuing, you agree to our{' '}
                <a href="#" className="text-indigo-400 hover:underline">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="text-indigo-400 hover:underline">Privacy Policy</a>
              </p>
            </div>
          </div>

          {/* Footer */}
          <p className="text-center text-[var(--text-muted)] text-sm !mt-8">
            ✨ Powered by AI to help you land your dream job
          </p>
        </div>
      </div>
    </main>
  );
}
