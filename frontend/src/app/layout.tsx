'use client';

import { useEffect, useState } from 'react';
import "./globals.css";
import { Inter } from 'next/font/google';
import { useStore } from '@/utils/store';
import { useGlobalWebSocket } from '@/hooks/useGlobalWebSocket';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme, _hasHydrated, token, isAuthenticated, fetchUser } = useStore();
  const [mounted, setMounted] = useState(false);

  useGlobalWebSocket();

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (_hasHydrated && token && useStore.getState().user === null) {
      fetchUser();
    }
  }, [_hasHydrated, token, fetchUser]);

  useEffect(() => {
    if (!mounted) return;
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme, mounted]);

  return (
    <html lang="en" className={`${inter.variable} ${mounted && theme === 'dark' ? 'dark' : ''}`}>
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
