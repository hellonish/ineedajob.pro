'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useStore } from '@/utils/store';

function CallbackHandler() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const login = useStore((s) => s.login);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const token = searchParams.get('token');
        const errorParam = searchParams.get('error');

        if (errorParam) {
            setError(errorParam);
            return;
        }

        if (token) {
            login(token)
                .then(() => router.push('/dashboard'))
                .catch((err) => setError(err.message));
        } else {
            setError('No token received');
        }
    }, [searchParams, login, router]);

    if (error) {
        return (
            <div className="text-red-400">
                <p className="text-xl !mb-4">Authentication Failed</p>
                <p className="text-sm text-slate-400">{error}</p>
                <button
                    onClick={() => router.push('/')}
                    className="!mt-6 !px-4 !py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                    Try Again
                </button>
            </div>
        );
    }

    return (
        <div className="text-slate-300">
            <div className="!mb-4 w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p>Signing you in...</p>
        </div>
    );
}

export default function AuthCallbackPage() {
    return (
        <main className="min-h-screen flex items-center justify-center bg-[#0a0a0f]">
            <div className="text-center">
                <Suspense fallback={
                    <div className="text-slate-300">
                        <div className="!mb-4 w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
                        <p>Loading...</p>
                    </div>
                }>
                    <CallbackHandler />
                </Suspense>
            </div>
        </main>
    );
}
