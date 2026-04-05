'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useStore, QueueItem } from '@/utils/store';
import { api, JobListItem, QueueStatusResponse } from '@/utils/api';
import Header from '@/components/Header';
import { motion, AnimatePresence } from 'framer-motion';



// Stats Card Component
function StatCard({
    label,
    value,
    color,
    delay
}: {
    label: string;
    value: number;
    color: string;
    delay?: number;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: delay || 0 }}
            className="bg-[var(--card-bg)] backdrop-blur-sm border border-[var(--border-color)] rounded-xl !p-4 text-center hover:opacity-80 transition-opacity"
        >
            <p className={`text-2xl font-bold !mb-1 ${color}`}>{value}</p>
            <p className="text-xs text-[var(--text-secondary)]">{label}</p>
        </motion.div>
    );
}

// Queue Item Component
function QueueItemRow({
    item,
    onRemove
}: {
    item: QueueItem;
    onRemove: () => void;
}) {
    const [elapsed, setElapsed] = useState(0);

    // Calculate elapsed time since start (if analyzing) or generally
    useEffect(() => {
        // Only count up if analyzing or pending
        if (item.status === 'complete' || item.status === 'error') return;

        const tick = () => {
            setElapsed(Math.floor((Date.now() - item.startTime) / 1000));
        };
        tick();
        const interval = setInterval(tick, 1000);
        return () => clearInterval(interval);
    }, [item.startTime, item.status]);



    const formatTime = (s: number) => {
        const m = Math.floor(s / 60);
        const sec = s % 60;
        return m > 0 ? `${m}m ${sec}s` : `${sec}s`;
    };

    return (
        <motion.div
            layout
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="flex items-center justify-between !py-3 !px-4 bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg"
        >
            <div className="flex-1 min-w-0">
                <p className="text-sm text-[var(--text-primary)] truncate">{item.jobTitle}</p>
                <p className="text-xs text-[var(--text-muted)]">
                    {item.status === 'analyzing' && `Analyzing... ${formatTime(elapsed)}`}
                    {item.status === 'pending' && 'Waiting...'}
                    {item.status === 'complete' && 'Complete'}
                    {item.status === 'error' && `Error: ${item.error}`}
                </p>
            </div>
            <button
                onClick={onRemove}
                className="!ml-3 text-[var(--text-muted)] hover:text-red-400 transition-colors text-lg cursor-pointer"
                title="Remove"
            >
                ×
            </button>
        </motion.div>
    );
}

export default function DashboardPage() {
    const router = useRouter();
    const { isAuthenticated, token, _hasHydrated, fetchUser, user, queue, addToQueue, updateQueueItem, removeFromQueue, clearQueue, setQueue } = useStore();
    const [jobs, setJobs] = useState<JobListItem[]>([]);
    const [jobInput, setJobInput] = useState('');
    const [jobLink, setJobLink] = useState('');
    const [isQueueOpen, setIsQueueOpen] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);



    // Initial Data Fetch
    useEffect(() => {
        if (!_hasHydrated) return;

        if (token && !user) {
            fetchUser();
            return;
        }

        if (!token) {
            router.push('/');
            return;
        }

        if (isAuthenticated) {
            // Fetch Jobs
            api.getJobs()
                .then(data => {
                    setJobs(data);
                })
                .catch((err) => {
                    console.error(err);
                });

            // Fetch Queue Status
            api.getQueueStatus()
                .then((status: QueueStatusResponse) => {
                    // Sync frontend queue with backend status
                    const mappedQueue: QueueItem[] = status.jobs.map(j => ({
                        id: j.id,
                        jobTitle: j.job_title,
                        status: j.status === 'processing' ? 'analyzing' : 'pending',
                        startTime: Date.now(), // Approximate
                    }));
                    setQueue(mappedQueue);
                })
                .catch(console.error);
        }
    }, [_hasHydrated, isAuthenticated, token, user, fetchUser, router, setQueue]);



    // Auto-focus textarea
    useEffect(() => {
        textareaRef.current?.focus();
    }, []);

    // Calculate stats
    const stats = {
        total: jobs.length,
        applied: jobs.filter((j) => j.status === 'applied').length,
        interview: jobs.filter((j) => j.status === 'interview').length,
        offer: jobs.filter((j) => j.status === 'offer').length,
        rejected: jobs.filter((j) => j.status === 'rejected').length,
    };

    // Paste from clipboard
    const handlePaste = async () => {
        try {
            const text = await navigator.clipboard.readText();
            setJobInput(text);
            textareaRef.current?.focus();
        } catch {
            alert('Unable to access clipboard. Please paste manually.');
        }
    };

    // Submit job for analysis via new JobLens pipeline
    const handleSubmit = async () => {
        if (!jobInput.trim() || isSubmitting) return;

        setIsSubmitting(true);
        try {
            const newJob = await api.createJob({
                jd_text: jobInput.trim(),
                company_website: jobLink.trim() || undefined,
            });

            setJobInput('');
            setJobLink('');
            router.push(`/jobs/${newJob.id}`);

        } catch (error) {
            console.error(error);
            alert('Failed to analyze job. Please try again.');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!_hasHydrated || !isAuthenticated) {
        return null;
    }

    const displayQueue = queue;

    return (
        <main className="min-h-screen">
            <Header />

            <div className="max-w-6xl mx-auto !px-6 !py-8">
                {/* Stats Cards */}
                <div className="grid grid-cols-2 md:grid-cols-5 !gap-4 !mb-8">
                    <StatCard label="Total Applications" value={stats.total} color="text-[var(--text-primary)]" delay={0} />
                    <StatCard label="Applied" value={stats.applied} color="text-blue-500" delay={0.1} />
                    <StatCard label="Interview" value={stats.interview} color="text-yellow-500" delay={0.2} />
                    <StatCard label="Offer" value={stats.offer} color="text-green-500" delay={0.3} />
                    <StatCard label="Rejected" value={stats.rejected} color="text-red-500" delay={0.4} />
                </div>

                {/* Job Input Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-[var(--card-bg)] backdrop-blur-sm border border-[var(--border-color)] rounded-2xl !p-6 !mb-6"
                >
                    <h2 className="text-lg font-semibold !mb-4 text-[var(--text-primary)]">
                        Analyze a Job Posting
                    </h2>

                    {/* Company Website Input */}
                    <div className="!mb-4">
                        <label className="block text-xs text-[var(--text-secondary)] !mb-1.5">
                            Company Website (optional — used for company research)
                        </label>
                        <div className="relative">
                            <input
                                type="url"
                                value={jobLink}
                                onChange={(e) => setJobLink(e.target.value)}
                                placeholder="https://company.com"
                                className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg !py-2.5 !pl-10 !pr-4 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all"
                            />
                            <svg
                                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                            </svg>
                        </div>
                    </div>

                    <div className="relative">
                        <textarea
                            ref={textareaRef}
                            value={jobInput}
                            onChange={(e) => setJobInput(e.target.value)}
                            placeholder="Paste the job description here..."
                            className="w-full h-64 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-xl !p-4 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] resize-none focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all"
                        />
                        <button
                            onClick={handlePaste}
                            className="absolute top-3 right-3 flex items-center !gap-2 !px-3 !py-1.5 bg-[var(--card-bg)] hover:opacity-80 text-xs text-[var(--text-secondary)] rounded-lg border border-[var(--border-color)] transition-colors cursor-pointer"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                            </svg>
                            Paste from clipboard
                        </button>
                    </div>
                    <button
                        onClick={handleSubmit}
                        disabled={!jobInput.trim() || isSubmitting}
                        className="!mt-4 w-full !py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all cursor-pointer"
                    >
                        {isSubmitting ? 'Starting analysis...' : 'Analyze Job'}
                    </button>
                </motion.div>

                {/* Analysis Queue */}
                <AnimatePresence>
                    {displayQueue.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="bg-[var(--card-bg)] backdrop-blur-sm border border-[var(--border-color)] rounded-2xl overflow-hidden"
                        >
                            <div
                                onClick={() => setIsQueueOpen(!isQueueOpen)}
                                className="w-full flex items-center justify-between !px-6 !py-4 hover:opacity-90 transition-opacity cursor-pointer"
                            >
                                <div className="flex items-center !gap-3">
                                    <span className="text-[var(--text-primary)] font-medium">Analysis Queue</span>
                                    <span className="!px-2 !py-0.5 bg-indigo-500/20 text-indigo-400 text-xs rounded-full">
                                        {displayQueue.length}
                                    </span>
                                </div>
                                <div className="flex items-center !gap-3">
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            clearQueue();
                                        }}
                                        className="text-xs text-[var(--text-muted)] hover:text-red-400 transition-colors cursor-pointer"
                                    >
                                        Clear all
                                    </button>
                                    <div className="flex-shrink-0 ml-2">
                                        <svg
                                            className={`w-5 h-5 text-[var(--text-secondary)] transition-transform ${isQueueOpen ? 'rotate-180' : ''}`}
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7 7" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                            {isQueueOpen && (
                                <motion.div
                                    className="!px-6 !pb-4 space-y-2"
                                >
                                    <AnimatePresence mode='popLayout'>
                                        {displayQueue.map((item) => (
                                            <QueueItemRow
                                                key={item.id}
                                                item={item}
                                                onRemove={() => {
                                                    api.cancelJob(item.id).catch(console.error);
                                                    removeFromQueue(item.id);
                                                }}
                                            />
                                        ))}
                                    </AnimatePresence>
                                </motion.div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main >
    );
}
