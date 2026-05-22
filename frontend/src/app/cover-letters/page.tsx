'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, CoverLetter, JobListItem } from '@/utils/api';
import Header from '@/components/Header';
import { motion, AnimatePresence } from 'framer-motion';
import ConfirmationModal from '@/components/ConfirmationModal';

const MODE_LABELS: Record<string, string> = {
    storyline: 'Storyline',
    disruptive: 'Disruptive',
    regular: 'Regular',
    auto: 'Auto-Detect',
    custom: 'Custom',
};

const MODE_COLORS: Record<string, string> = {
    storyline: 'bg-[var(--accent-dim)] text-[var(--accent)]',
    disruptive: 'bg-[var(--danger-dim)] text-[var(--danger)]',
    regular: 'bg-[var(--success-dim)] text-[var(--success)]',
    auto: 'bg-[var(--warning-dim)] text-[var(--warning)]',
    custom: 'bg-[var(--accent-dim)] text-[var(--accent)]',
};

const MODE_STYLES: Record<string, { color: string; border: string }> = {
    storyline: { color: 'var(--accent)', border: 'var(--accent-border)' },
    disruptive: { color: 'var(--danger)', border: 'var(--danger-border)' },
    regular: { color: 'var(--success)', border: 'var(--success-border)' },
    auto: { color: 'var(--warning)', border: 'var(--warning-border)' },
    custom: { color: 'var(--accent)', border: 'var(--accent-border)' },
};

function formatDate(dateStr: string) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function CoverLettersPage() {
    const router = useRouter();
    const { token, isAuthenticated, _hasHydrated } = useStore();

    const [letters, setLetters] = useState<CoverLetter[]>([]);
    const [jobs, setJobs] = useState<JobListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);

    // Modal state
    const [modalTab, setModalTab] = useState<'select' | 'paste'>('paste');
    const [searchQuery, setSearchQuery] = useState('');
    const [quickJdText, setQuickJdText] = useState('');

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) { router.push('/'); return; }
        loadData();
    }, [token, _hasHydrated]);

    const loadData = async () => {
        try {
            const [fetchedLetters, fetchedJobs] = await Promise.all([
                api.getCoverLetters().catch(() => []),
                api.getJobs('tracked').catch(() => [])
            ]);
            setLetters(fetchedLetters);
            setJobs(fetchedJobs);
        } catch { } finally { setLoading(false); }
    };

    const filteredJobs = jobs.filter(job => {
        if (!searchQuery.trim()) return true;
        const q = searchQuery.toLowerCase();
        const title = (job.job_posting?.job_title || '').toLowerCase();
        const company = (job.job_posting?.company_name || '').toLowerCase();
        const location = (job.job_posting?.location || '').toLowerCase();
        const qualifications = (job.job_posting?.required_qualifications || []).join(' ').toLowerCase();
        const skills = [
            ...(job.job_posting?.technical_skills || []),
            ...(job.job_posting?.soft_skills || []),
        ].join(' ').toLowerCase();
        return title.includes(q) || company.includes(q) || location.includes(q)
            || qualifications.includes(q) || skills.includes(q);
    });

    const handleCreateSelect = (jobId: string) => {
        router.push(`/jobs/${jobId}/cover-letter`);
    };

    const handleQuickStart = () => {
        if (!quickJdText.trim()) return;
        sessionStorage.setItem('quick_jd_text', quickJdText.trim());
        sessionStorage.removeItem('quick_company_name');
        router.push('/cover-letters/quick');
        closeModal();
    };

    const closeModal = () => {
        setShowCreateModal(false);
        setModalTab('paste');
        setSearchQuery('');
        setQuickJdText('');
    };

    if (!_hasHydrated || !isAuthenticated || loading) {
        return (
            <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div
                        className="w-8 h-8 border-2 rounded-full animate-spin"
                        style={{
                            borderColor: 'var(--border-strong)',
                            borderTopColor: 'var(--accent)',
                        }}
                    />
                </div>
            </div>
        );
    }

    return (
        <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
            <Header />

            <div className="max-w-screen-xl mx-auto px-8 py-6">
                {/* Page header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-lg font-semibold" style={{ color: 'var(--text-1)' }}>
                            Cover Letters
                        </h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>
                            {letters.length} {letters.length === 1 ? 'letter' : 'letters'}
                        </p>
                    </div>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="px-3 py-1.5 rounded-lg text-sm transition-colors cursor-pointer"
                        style={{
                            border: '1px solid var(--border-strong)',
                            color: 'var(--text-2)',
                            background: 'transparent',
                        }}
                        onMouseEnter={e => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-1)';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--accent-border)';
                        }}
                        onMouseLeave={e => {
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)';
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-strong)';
                        }}
                    >
                        New Cover Letter
                    </button>
                </div>

                {/* Letters table */}
                {letters.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20">
                        <p className="text-sm mb-2" style={{ color: 'var(--text-3)' }}>
                            No cover letters yet.
                        </p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="text-sm cursor-pointer"
                            style={{ color: 'var(--accent)', background: 'none', border: 'none', padding: 0 }}
                        >
                            Create your first one →
                        </button>
                    </div>
                ) : (
                    <div
                        className="w-full rounded-lg overflow-hidden"
                        style={{ border: '1px solid var(--border)' }}
                    >
                        {/* Header row */}
                        <div
                            className="grid items-center px-4 py-2"
                            style={{
                                gridTemplateColumns: '140px 1fr 1fr 80px 24px',
                                background: 'var(--surface)',
                                borderBottom: '1px solid var(--border)',
                            }}
                        >
                            {['Mode', 'Job Title', 'Company', 'Date', ''].map((col) => (
                                <span
                                    key={col}
                                    className="text-xs uppercase tracking-widest"
                                    style={{ color: 'var(--text-3)' }}
                                >
                                    {col}
                                </span>
                            ))}
                        </div>

                        {/* Data rows */}
                        {letters.map((letter, idx) => {
                            const job = jobs.find(j => j.id === letter.job_id);
                            const jobTitle = job?.job_posting?.job_title
                                || (letter.content as Record<string, unknown>)?.job_title as string
                                || 'Unknown Position';
                            const company = job?.job_posting?.company_name
                                || (letter.content as Record<string, unknown>)?.company_name as string
                                || 'Unknown Company';
                            const modeKey = letter.mode || 'regular';
                            const modeLabel = letter.content?.mode_label || MODE_LABELS[modeKey] || modeKey;
                            const modeStyle = MODE_STYLES[modeKey] || { color: 'var(--text-3)', border: 'var(--border)' };

                            const handleClick = () => {
                                if (letter.job_id) {
                                    router.push(`/jobs/${letter.job_id}/cover-letter`);
                                } else {
                                    router.push(`/cover-letters/quick?view=${letter.id}`);
                                }
                            };

                            return (
                                <div
                                    key={letter.id}
                                    className="grid items-center px-4 py-3 cursor-pointer transition-colors"
                                    style={{
                                        gridTemplateColumns: '140px 1fr 1fr 80px 24px',
                                        background: 'var(--bg)',
                                        borderBottom: idx < letters.length - 1 ? '1px solid var(--border)' : 'none',
                                    }}
                                    onClick={handleClick}
                                    onMouseEnter={e => {
                                        (e.currentTarget as HTMLDivElement).style.background = 'var(--hover)';
                                    }}
                                    onMouseLeave={e => {
                                        (e.currentTarget as HTMLDivElement).style.background = 'var(--bg)';
                                    }}
                                >
                                    {/* Mode tag */}
                                    <div>
                                        <span
                                            className="px-2 py-0.5 rounded text-xs border"
                                            style={{
                                                color: modeStyle.color,
                                                borderColor: modeStyle.border,
                                            }}
                                        >
                                            {String(modeLabel)}
                                        </span>
                                    </div>

                                    {/* Job title */}
                                    <span
                                        className="text-sm truncate pr-4"
                                        style={{ color: 'var(--text-1)' }}
                                    >
                                        {jobTitle}
                                    </span>

                                    {/* Company */}
                                    <span
                                        className="text-sm truncate pr-4"
                                        style={{ color: 'var(--text-2)' }}
                                    >
                                        {company}
                                    </span>

                                    {/* Date */}
                                    <span
                                        className="text-xs font-mono tabular-nums"
                                        style={{ color: 'var(--text-3)' }}
                                    >
                                        {formatDate(letter.updated_at)}
                                    </span>

                                    {/* Arrow */}
                                    <span className="text-base" style={{ color: 'var(--text-3)' }}>
                                        ›
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* Create modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={closeModal}
                            className="absolute inset-0"
                            style={{ background: 'var(--overlay)' }}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="relative w-full max-w-2xl rounded-xl overflow-hidden flex flex-col max-h-[88vh]"
                            style={{
                                background: 'var(--card)',
                                border: '1px solid var(--border)',
                            }}
                        >
                            {/* Modal header */}
                            <div
                                className="flex items-center justify-between px-4 py-3"
                                style={{ borderBottom: '1px solid var(--border)' }}
                            >
                                {/* Tabs */}
                                <div className="flex gap-1">
                                    <button
                                        onClick={() => setModalTab('select')}
                                        className="px-3 py-1 text-sm rounded-md transition-colors cursor-pointer"
                                        style={{
                                            background: modalTab === 'select' ? 'var(--hover)' : 'transparent',
                                            color: modalTab === 'select' ? 'var(--text-1)' : 'var(--text-3)',
                                            border: 'none',
                                        }}
                                    >
                                        Select Job
                                    </button>
                                    <button
                                        onClick={() => setModalTab('paste')}
                                        className="px-3 py-1 text-sm rounded-md transition-colors cursor-pointer"
                                        style={{
                                            background: modalTab === 'paste' ? 'var(--hover)' : 'transparent',
                                            color: modalTab === 'paste' ? 'var(--text-1)' : 'var(--text-3)',
                                            border: 'none',
                                        }}
                                    >
                                        Insert JD
                                    </button>
                                </div>
                                <button
                                    onClick={closeModal}
                                    className="text-lg leading-none cursor-pointer"
                                    style={{ color: 'var(--text-3)', background: 'none', border: 'none' }}
                                >
                                    ×
                                </button>
                            </div>

                            {/* Select Job tab */}
                            {modalTab === 'select' && (
                                <>
                                    {/* Search input */}
                                    <div className="px-3 pt-3">
                                        <input
                                            type="text"
                                            placeholder="Search by title, company, skills..."
                                            value={searchQuery}
                                            onChange={e => setSearchQuery(e.target.value)}
                                            className="w-full px-3 py-2 text-sm rounded-lg outline-none"
                                            style={{
                                                background: 'var(--surface)',
                                                border: '1px solid var(--border)',
                                                color: 'var(--text-1)',
                                            }}
                                            autoFocus
                                        />
                                    </div>

                                    {/* Job list */}
                                    <div className="flex-1 overflow-y-auto mt-2 min-h-[360px]">
                                        {filteredJobs.length === 0 ? (
                                            <p
                                                className="text-center text-sm py-8"
                                                style={{ color: 'var(--text-3)' }}
                                            >
                                                {searchQuery ? 'No matching jobs.' : 'No tracked jobs found.'}
                                            </p>
                                        ) : (
                                            filteredJobs.map((job, idx) => (
                                                <button
                                                    key={job.id}
                                                    onClick={() => handleCreateSelect(job.id)}
                                                    className="w-full text-left px-4 py-3 cursor-pointer transition-colors"
                                                    style={{
                                                        borderBottom: idx < filteredJobs.length - 1 ? '1px solid var(--border)' : 'none',
                                                        background: 'transparent',
                                                        border: 'none',
                                                        borderBottomStyle: 'solid',
                                                        borderBottomWidth: idx < filteredJobs.length - 1 ? '1px' : '0',
                                                        borderBottomColor: 'var(--border)',
                                                    }}
                                                    onMouseEnter={e => {
                                                        (e.currentTarget as HTMLButtonElement).style.background = 'var(--hover)';
                                                    }}
                                                    onMouseLeave={e => {
                                                        (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                                                    }}
                                                >
                                                    <div className="text-sm" style={{ color: 'var(--text-1)' }}>
                                                        {job.job_posting.company_name}
                                                    </div>
                                                    <div className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>
                                                        {job.job_posting.job_title}
                                                    </div>
                                                </button>
                                            ))
                                        )}
                                    </div>
                                </>
                            )}

                            {/* Paste JD tab */}
                            {modalTab === 'paste' && (
                                <div className="p-4 flex flex-col gap-3">
                                    <p className="text-xs" style={{ color: 'var(--text-3)' }}>
                                        Paste a job description to generate a cover letter without tracking the job.
                                    </p>
                                    <textarea
                                        placeholder="Paste the job description here..."
                                        value={quickJdText}
                                        onChange={e => setQuickJdText(e.target.value)}
                                        rows={12}
                                        className="w-full px-3 py-2 text-sm rounded-lg outline-none resize-none"
                                        style={{
                                            background: 'var(--surface)',
                                            border: '1px solid var(--border)',
                                            color: 'var(--text-1)',
                                        }}
                                        autoFocus
                                    />
                                    <button
                                        onClick={handleQuickStart}
                                        disabled={!quickJdText.trim()}
                                        className="w-full py-2.5 rounded-lg text-sm font-medium transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                                        style={{
                                            background: 'var(--accent)',
                                            color: 'var(--bg)',
                                            border: 'none',
                                        }}
                                    >
                                        Generate Cover Letter
                                    </button>
                                </div>
                            )}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </main>
    );
}
