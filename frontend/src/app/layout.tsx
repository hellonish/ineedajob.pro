'use client';

import { useEffect, useState } from 'react';
import "./globals.css";
import { useStore } from '@/utils/store';
import { useGlobalWebSocket } from '@/hooks/useGlobalWebSocket';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme, _hasHydrated, token, isAuthenticated, fetchUser } = useStore();
  const [mounted, setMounted] = useState(false);

  // Global WebSocket connection
  useGlobalWebSocket();

  // Wait for client mount to avoid hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Global session check
  useEffect(() => {
    if (_hasHydrated && token && !isAuthenticated) {
      // Double check: store might need to catch up if we just set it in rehydrate
      // But fetchUser is safe to call
    }
    if (_hasHydrated && token && useStore.getState().user === null) {
      fetchUser();
    }
  }, [_hasHydrated, token, fetchUser]);

  useEffect(() => {
    if (!mounted) return;
    // Apply theme class to document
    if (theme === 'light') {
      document.documentElement.classList.add('light');
    } else {
      document.documentElement.classList.remove('light');
    }
  }, [theme, mounted]);

  return (
    <html lang="en" className={mounted && theme === 'light' ? 'light' : ''}>
      <head>
        <title>Wand - AI Resume Analyzer</title>
        <meta name="description" content="Analyze your resume against job postings with AI-powered insights" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
