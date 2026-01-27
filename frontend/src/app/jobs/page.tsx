'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, JobListItem } from '@/utils/api';
import Header from '@/components/Header';
import { motion, AnimatePresence } from 'framer-motion';
import ConfirmationModal from '@/components/ConfirmationModal';

// Status options for filter
const STATUS_OPTIONS = [
    { value: 'all', label: 'All Jobs' },
    { value: 'tracked', label: 'Tracked' },
    { value: 'applied', label: 'Applied' },
    { value: 'interview', label: 'Interview' },
    { value: 'offer', label: 'Offer' },
    { value: 'rejected', label: 'Rejected' },
];

const FILTER_STYLES: Record<string, { active: string; inactive: string }> = {
    all: {
        active: 'bg-indigo-500 text-white shadow-sm shadow-indigo-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-indigo-400 hover:bg-indigo-500/10'
    },
    tracked: {
        active: 'bg-slate-500 text-white shadow-sm shadow-slate-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-slate-400 hover:bg-slate-500/10'
    },
    applied: {
        active: 'bg-blue-500 text-white shadow-sm shadow-blue-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-blue-400 hover:bg-blue-500/10'
    },
    interview: {
        active: 'bg-yellow-500 text-white shadow-sm shadow-yellow-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-yellow-400 hover:bg-yellow-500/10'
    },
    offer: {
        active: 'bg-green-500 text-white shadow-sm shadow-green-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-green-400 hover:bg-green-500/10'
    },
    rejected: {
        active: 'bg-red-500 text-white shadow-sm shadow-red-500/20',
        inactive: 'text-[var(--text-muted)] hover:text-red-400 hover:bg-red-500/10'
    }
};

// Job Card Component
function JobCard({
    job,
    onDelete,
    onView
}: {
    job: JobListItem;
    onDelete: () => void;
    onView: () => void;
}) {
    const [isDeleting, setIsDeleting] = useState(false);

    // Get data from job_posting (API structure)
    const jobTitle = job.job_posting?.job_title || 'Untitled Position';
    const companyName = job.job_posting?.company_name || 'Unknown Company';
    const skills = job.job_posting?.technical_skills?.slice(0, 4) || [];
    const allSkills = job.job_posting?.technical_skills || [];
    const score = job.final_score ?? 0;

    const handleDelete = async () => {
        if (isDeleting) return;
        setIsDeleting(true);
        try {
            await onDelete();
        } finally {
            setIsDeleting(false);
        }
    };

    const statusColors: Record<string, string> = {
        tracked: 'bg-slate-500/20 text-slate-400',
        applied: 'bg-blue-500/20 text-blue-400',
        interview: 'bg-yellow-500/20 text-yellow-400',
        offer: 'bg-green-500/20 text-green-400',
        rejected: 'bg-red-500/20 text-red-400',
    };

    const getScoreColor = (s: number) => {
        if (s >= 80) return 'text-green-400';
        if (s >= 60) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="relative z-10 flex flex-col h-full bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl !p-5 hover:border-indigo-500/30 transition-colors group"
        >
            <div className="flex-1">
                <div className="flex items-start justify-between !mb-3">
                    <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-[var(--text-primary)] truncate !mb-1 group-hover:text-indigo-400 transition-colors cursor-pointer" onClick={onView}>
                            {jobTitle}
                        </h3>
                        <p className="text-sm text-[var(--text-secondary)]">{companyName}</p>
                    </div>
                    <div className="text-center !ml-4">
                        <motion.p
                            initial={{ scale: 0.8 }}
                            animate={{ scale: 1 }}
                            className={`text-2xl font-bold ${getScoreColor(score)}`}
                        >
                            {score}%
                        </motion.p>
                        <p className="text-xs text-[var(--text-muted)]">Match</p>
                    </div>
                </div>

                <div className="flex items-center !gap-2 !mb-3">
                    <span className={`!px-2 !py-0.5 text-xs rounded-full ${statusColors[job.status] || statusColors.tracked}`}>
                        {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                </div>

                {skills.length > 0 && (
                    <div className="flex flex-wrap !gap-1.5 !mb-3">
                        {skills.map((skill, i) => (
                            <span key={i} className="!px-2 !py-0.5 bg-[var(--bg-primary)] text-xs text-[var(--text-secondary)] rounded-md">
                                {skill}
                            </span>
                        ))}
                        {allSkills.length > 4 && (
                            <span className="!px-2 !py-0.5 text-xs text-[var(--text-muted)]">
                                +{allSkills.length - 4} more
                            </span>
                        )}
                    </div>
                )}
            </div>

            <div className="flex items-center justify-between !pt-3 border-t border-[var(--border-color)] mt-auto">
                <button
                    onClick={handleDelete}
                    disabled={isDeleting}
                    className="flex items-center !gap-1.5 !px-3 !py-1.5 text-sm text-red-400 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50 cursor-pointer"
                >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                    {isDeleting ? 'Deleting...' : 'Delete'}
                </button>
                <button
                    onClick={onView}
                    className="flex items-center !gap-1.5 !px-4 !py-1.5 bg-indigo-500/10 text-indigo-400 text-sm font-medium rounded-lg hover:bg-indigo-500/20 transition-colors cursor-pointer"
                >
                    View Details
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </button>
            </div>
        </motion.div>
    );
}

export default function JobsPage() {
    const router = useRouter();
    const { isAuthenticated, token, _hasHydrated, fetchUser, user, jobsFilter, setJobsFilter } = useStore();
    const [jobs, setJobs] = useState<JobListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');

    const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

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
            loadJobs();
        }
    }, [_hasHydrated, isAuthenticated, token, user, fetchUser, router]);

    const loadJobs = async () => {
        setIsLoading(true);
        try {
            const data = await api.getJobs();
            setJobs(data);
            if (data.length === 0) {
                // Empty state handled by UI
            }
        } catch (error) {
            console.error('Failed to load jobs:', error);
        } finally {
            setIsLoading(false);
        }
    };



    const handleDelete = (id: string) => {
        setShowDeleteConfirm(id);
    };

    const handleConfirmDelete = async () => {
        if (!showDeleteConfirm) return;



        try {
            await api.deleteJob(showDeleteConfirm);
            setJobs(jobs.filter(j => j.id !== showDeleteConfirm));
        } catch (error) {
            console.error('Failed to delete job:', error);
        } finally {
            setShowDeleteConfirm(null);
        }
    };

    const filteredJobs = jobs.filter(job => {
        if (jobsFilter !== 'all' && job.status !== jobsFilter) return false;

        if (searchQuery.trim()) {
            const title = job.job_posting?.job_title || '';
            const company = job.job_posting?.company_name || '';
            const query = searchQuery.toLowerCase();
            return title.toLowerCase().includes(query) || company.toLowerCase().includes(query);
        }

        return true;
    });

    if (!_hasHydrated || !isAuthenticated) {
        return null;
    }

    return (
        <main className="min-h-screen relative z-0">
            <Header />

            <div className="max-w-6xl mx-auto !px-6 !py-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between !gap-4 !mb-6">
                    <motion.h2
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="text-2xl font-bold text-[var(--text-primary)]"
                    >
                        My Jobs
                    </motion.h2>

                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="relative w-full md:w-80"
                    >
                        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--text-muted)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Search jobs..."
                            className="w-full !pl-10 !pr-4 !py-2.5 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-xl text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-indigo-500/50"
                        />
                    </motion.div>
                </div>

                <div className="flex flex-col md:flex-row md:items-center justify-between !gap-4 !mb-6">
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="inline-flex flex-wrap items-center !gap-2 !p-2 bg-[var(--card-bg)] backdrop-blur-md border border-[var(--border-color)] rounded-full"
                    >
                        {STATUS_OPTIONS.map((option) => {
                            const isSelected = jobsFilter === option.value;
                            const styles = FILTER_STYLES[option.value];

                            return (
                                <button
                                    key={option.value}
                                    onClick={() => setJobsFilter(option.value)}
                                    className={`!px-4 !py-1.5 text-xs font-medium rounded-full transition-all duration-300 cursor-pointer ${isSelected ? styles.active : styles.inactive
                                        }`}
                                >
                                    {option.label}
                                </button>
                            );
                        })}
                    </motion.div>

                    <motion.button
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => router.push('/dashboard')}
                        className="flex items-center !gap-2 !px-4 !py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition-colors shadow-sm cursor-pointer"
                    >
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                        </svg>
                        New Job
                    </motion.button>
                </div>

                {isLoading ? (
                    <div className="text-center !py-12">
                        <div className="inline-block w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                        <p className="text-[var(--text-muted)] !mt-4">Loading jobs...</p>
                    </div>
                ) : filteredJobs.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center !py-12 bg-[var(--card-bg)] border border-[var(--border-color)] rounded-2xl"
                    >
                        <svg className="w-16 h-16 mx-auto text-[var(--text-muted)] !mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                        <p className="text-lg text-[var(--text-secondary)] !mb-2">No jobs found</p>
                        <p className="text-sm text-[var(--text-muted)]">
                            {searchQuery || jobsFilter !== 'all' ? 'Try adjusting your filters' : 'Start by analyzing a job posting on the dashboard'}
                        </p>
                        <button
                            onClick={() => router.push('/dashboard')}
                            className="!mt-6 !px-6 !py-2.5 bg-indigo-500 text-white text-sm font-medium rounded-lg hover:bg-indigo-600 transition-colors cursor-pointer"
                        >
                            Go to Dashboard
                        </button>
                    </motion.div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 !gap-4 relative z-0">
                        <AnimatePresence>
                            {filteredJobs.map((job) => (
                                <JobCard
                                    key={job.id}
                                    job={job}
                                    onDelete={() => handleDelete(job.id)}
                                    onView={() => router.push(`/jobs/${job.id}`)}
                                />
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            <ConfirmationModal
                isOpen={!!showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(null)}
                onConfirm={handleConfirmDelete}
                title="Delete Job"
                message="Are you sure you want to delete this job? This action cannot be undone."
                confirmLabel="Delete Job"
                isDestructive={true}
            />
        </main >
    );
}
