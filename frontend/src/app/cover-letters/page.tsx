'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, CoverLetter, JobListItem } from '@/utils/api';
import Header from '@/components/Header';
import { motion, AnimatePresence } from 'framer-motion';
import ConfirmationModal from '@/components/ConfirmationModal';

export default function CoverLettersPage() {
    const router = useRouter();
    const { token, isAuthenticated, _hasHydrated } = useStore();

    const [letters, setLetters] = useState<CoverLetter[]>([]);
    const [jobs, setJobs] = useState<JobListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) {
            router.push('/');
            return;
        }
        loadData();
    }, [token, _hasHydrated]);

    const loadData = async () => {
        try {
            const [fetchedLetters, fetchedJobs] = await Promise.all([
                api.getCoverLetters().catch(() => []),
                api.getJobs().catch(() => [])
            ]);

            setLetters(fetchedLetters);
            setJobs(fetchedJobs);

        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateSelect = (jobId: string) => {
        router.push(`/jobs/${jobId}/cover-letter`);
    };

    if (!_hasHydrated || !isAuthenticated || loading) {
        return (
            <div className="min-h-screen">
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    return (
        <main className="min-h-screen bg-[var(--bg-primary)]">
            <Header />

            <div className="max-w-6xl mx-auto px-6 py-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">Cover Letters</h1>
                        <p className="text-[var(--text-secondary)]">Manage and generate tailored cover letters for your applications.</p>
                    </div>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-lg shadow-indigo-500/20 transition-all hover:scale-105 cursor-pointer flex items-center gap-2"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        New Cover Letter
                    </button>
                </div>

                {letters.length === 0 ? (
                    <div className="text-center py-20 bg-[var(--card-bg)] border border-[var(--border-color)] border-dashed rounded-xl">
                        <p className="text-[var(--text-muted)] text-lg">No cover letters found.</p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="mt-4 text-indigo-500 hover:text-indigo-400 font-medium"
                        >
                            Create your first one
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {letters.map((letter) => {
                            // Find associated job info (from jobs state or potentially encoded in letter if extended)
                            // For this demo, we lookup from jobs list if available
                            const job = jobs.find(j => j.id === letter.job_id);
                            const jobTitle = job?.job_posting.job_title || 'Unknown Position';
                            const company = job?.job_posting.company_name || 'Unknown Company';

                            return (
                                <motion.div
                                    key={letter.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl p-6 hover:border-indigo-500/30 transition-all cursor-pointer group"
                                    onClick={() => router.push(`/jobs/${letter.job_id}/cover-letter`)}
                                >
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="px-2 py-1 bg-indigo-500/10 text-indigo-400 text-xs font-bold uppercase rounded tracking-wider">
                                            {letter.mode}
                                        </div>
                                        <div className="text-xs text-[var(--text-muted)]">
                                            {new Date(letter.updated_at).toLocaleDateString()}
                                        </div>
                                    </div>

                                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1 truncate">{jobTitle}</h3>
                                    <p className="text-sm text-[var(--text-secondary)] mb-4 truncate">{company}</p>

                                    <div className="opacity-0 group-hover:opacity-100 transition-opacity text-sm text-indigo-500 font-medium flex items-center gap-1">
                                        View Letter →
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Create Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowCreateModal(false)}
                            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="relative w-full max-w-lg bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-2xl shadow-2xl overflow-hidden max-h-[80vh] flex flex-col"
                        >
                            <div className="p-6 border-b border-[var(--border-color)] flex justify-between items-center">
                                <h2 className="text-xl font-bold text-[var(--text-primary)]">Select a Job</h2>
                                <button onClick={() => setShowCreateModal(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-2">
                                {jobs.length === 0 ? (
                                    <p className="text-center text-[var(--text-muted)] py-8">No jobs found to generate a cover letter for.</p>
                                ) : (
                                    jobs.map(job => (
                                        <button
                                            key={job.id}
                                            onClick={() => handleCreateSelect(job.id)}
                                            className="w-full text-left p-4 rounded-xl bg-[var(--card-bg)] border border-[var(--border-color)] hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all group"
                                        >
                                            <div className="font-semibold text-[var(--text-primary)]">{job.job_posting.job_title}</div>
                                            <div className="text-sm text-[var(--text-secondary)]">{job.job_posting.company_name}</div>
                                        </button>
                                    ))
                                )}
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </main>
    );
}
