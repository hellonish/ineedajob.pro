'use client';

import ConfirmationModal from '@/components/ConfirmationModal';
import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, Job, QualificationItem, ResumeSuggestion, NewsResponse } from '@/utils/api';
import Header from '@/components/Header';
import ResumeEditor from '@/components/ResumeEditor';
import { motion, AnimatePresence } from 'framer-motion';

// Icons
const ICONS = {
    location: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
    ),
    money: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
    ),
    check: (
        <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
    ),
    x: (
        <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    )
};

const STATUS_OPTIONS = [
    { value: 'tracked', label: 'Tracked', color: 'bg-slate-500/10 text-slate-400 border-slate-500/20' },
    { value: 'applied', label: 'Applied', color: 'bg-blue-500/10 text-blue-400 border-blue-500/20' },
    { value: 'interview', label: 'Interview', color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' },
    { value: 'offer', label: 'Offer', color: 'bg-green-500/10 text-green-400 border-green-500/20' },
    { value: 'rejected', label: 'Rejected', color: 'bg-red-500/10 text-red-400 border-red-500/20' },
];

function QualificationRow({ item }: { item: QualificationItem }) {
    return (
        <div className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-primary)] border border-[var(--border-color)]">
            <div className="flex-shrink-0 mt-0.5">
                {item.matched ? ICONS.check : ICONS.x}
            </div>
            <div>
                <p className="text-sm font-medium text-[var(--text-primary)]">{item.name}</p>
                {item.matched && item.evidence && (
                    <p className="text-xs text-[var(--text-muted)] mt-1 pl-2 border-l-2 border-green-500/20">
                        "{item.evidence}"
                    </p>
                )}
            </div>
        </div>
    );
}

function SkillTag({ item }: { item: QualificationItem }) {
    return (
        <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border ${item.matched
            ? 'bg-green-500/10 text-green-400 border-green-500/20'
            : 'bg-red-500/10 text-red-400 border-red-500/20'
            }`}>
            {item.name}
        </span>
    );
}

function SuggestionCard({ item }: { item: ResumeSuggestion }) {
    const [copied, setCopied] = useState(false);

    const actionColors = {
        ADD: 'bg-blue-500 text-blue-100',
        UPDATE: 'bg-yellow-500 text-yellow-900',
        DELETE: 'bg-red-500 text-red-100'
    };

    // Make section names human-readable
    const formatSection = (section: string) => {
        // Convert work_experience[0].description -> Work Experience • Description
        // Convert skills[2] -> Skills
        let formatted = section
            .replace(/_/g, ' ')
            .replace(/\[(\d+)\]/g, '')
            .replace(/\./g, ' • ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
            .replace(/\s+/g, ' ')
            .trim();

        return formatted || section;
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(item.suggestion);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="p-4 rounded-xl bg-[var(--bg-primary)] border border-[var(--border-color)] group relative">
            <button
                onClick={handleCopy}
                className="absolute top-4 right-4 p-1.5 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--card-bg)] rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                title="Copy suggestion"
            >
                {copied ? (
                    <svg className="w-4 h-4 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                ) : (
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                )}
            </button>
            <div className="flex items-center gap-3 mb-2 pr-8">
                <span className={`px-2 py-0.5 text-xs font-bold rounded-md ${actionColors[item.action]}`}>
                    {item.action}
                </span>
                <span className="text-sm font-medium text-[var(--text-secondary)]">in {formatSection(item.section)}</span>
                {item.target && (
                    <span className="text-xs text-[var(--text-muted)] bg-[var(--card-bg)] px-2 py-0.5 rounded">
                        {item.target}
                    </span>
                )}
            </div>
            <p className="text-sm text-[var(--text-primary)]">{item.suggestion}</p>
        </div>
    );
}

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const router = useRouter();
    // Unwrap params using React.use()
    const { id } = use(params);

    const { token, isAuthenticated, _hasHydrated } = useStore();
    const [job, setJob] = useState<Job | null>(null);
    const [loading, setLoading] = useState(true);
    const [updating, setUpdating] = useState(false);

    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

    // Re-evaluation State
    const [isReevaluating, setIsReevaluating] = useState(false);
    const [reevaluationResume, setReevaluationResume] = useState<Record<string, unknown>>({});
    const [isSubmittingReevaluation, setIsSubmittingReevaluation] = useState(false);

    // Tab & News State
    const [activeTab, setActiveTab] = useState<'analysis' | 'news' | 'history'>('analysis');
    const [news, setNews] = useState<NewsResponse | null>(null);
    const [loadingNews, setLoadingNews] = useState(false);

    // Job Link Edit State
    const [isEditingLink, setIsEditingLink] = useState(false);
    const [jobLinkInput, setJobLinkInput] = useState('');
    const [savingLink, setSavingLink] = useState(false);

    useEffect(() => {
        if (!_hasHydrated) return;
        if (!token) {
            router.push('/');
            return;
        }
        loadJob();
    }, [id, token, _hasHydrated]);

    const loadJob = async () => {
        try {
            const data = await api.getJob(id);
            setJob(data);
        } catch (error) {
            console.error(error);
            // Handle error (e.g. redirect or show error)
            router.push('/jobs');
        } finally {
            setLoading(false);
        }
    };



    const handleStatusChange = async (newStatus: string) => {
        if (!job || updating) return;
        setUpdating(true);
        try {
            await api.updateJob(job.id, { status: newStatus as any });
            setJob({ ...job, status: newStatus as any });
        } catch (error) {
            console.error(error);
        } finally {
            setUpdating(false);
        }
    };

    const handleDelete = () => {
        setShowDeleteConfirm(true);
    };

    const handleConfirmDelete = async () => {
        if (!job) return;
        try {
            await api.deleteJob(id);
            router.push('/jobs');
        } catch (error) {
            console.error(error);
        } finally {
            setShowDeleteConfirm(false);
        }
    };

    const handleReevaluate = () => {
        if (!job) return;

        // Find latest resume data
        // If resume_history exists, take the last one. Otherwise fallback to property if we track it?
        // job schema has resume_history array.
        let currentResume = {};
        if (job.resume_history && job.resume_history.length > 0) {
            // Sort by version desc just to be safe
            const latest = [...job.resume_history].sort((a, b) => b.version - a.version)[0];
            currentResume = latest.resume_data;
        } else {
            // Fallback or empty? Ideally we should have it.
            currentResume = {};
        }

        setReevaluationResume(currentResume as Record<string, unknown>);
        setIsReevaluating(true);
    };

    const handleSubmitReevaluation = async (resumeData: Record<string, unknown>) => {
        if (!job) return;
        setIsSubmittingReevaluation(true);
        try {
            const result = await api.reEvaluateJob(job.id, { modified_resume: resumeData });

            // Update local state
            setJob({
                ...job,
                analysis_result: {
                    ...job.analysis_result,
                    final_score: result.final_score,
                    resume_formatting_score: result.formatting_score,
                    keyword_match_score: result.keyword_match_score,
                    qualification_match_score: result.qualification_match_score,
                    skill_match_score: result.skill_match_score,
                } as any
            });

            // Reload full job to get updated lists
            await loadJob();

            setIsReevaluating(false);
        } catch (error) {
            console.error(error);
            alert('Failed to re-evaluate. Please try again.');
        } finally {
            setIsSubmittingReevaluation(false);
        }
    };

    const loadNews = async () => {
        if (!job || !job.job_posting.company_name || news) return;
        setLoadingNews(true);
        try {
            const newsData = await api.getNews(job.job_posting.company_name);
            setNews(newsData);
        } catch (error) {
            console.error(error);
        } finally {
            setLoadingNews(false);
        }
    };

    const handleSaveJobLink = async () => {
        if (!job) return;
        setSavingLink(true);
        try {
            const updated = await api.updateJob(job.id, { job_link: jobLinkInput.trim() || null });
            setJob(updated);
            setIsEditingLink(false);
        } catch (error) {
            console.error(error);
            alert('Failed to save job link');
        } finally {
            setSavingLink(false);
        }
    };

    const handleDeleteJobLink = async () => {
        if (!job) return;
        setSavingLink(true);
        try {
            const updated = await api.updateJob(job.id, { job_link: '' });
            setJob(updated);
            setJobLinkInput('');
            setIsEditingLink(false);
        } catch (error) {
            console.error(error);
            alert('Failed to delete job link');
        } finally {
            setSavingLink(false);
        }
    };

    const handleTabChange = (tab: 'analysis' | 'news' | 'history') => {
        setActiveTab(tab);
        if (tab === 'news') {
            loadNews();
        }
    };

    if (!_hasHydrated || !isAuthenticated || loading || !job) {
        return (
            <div className="min-h-screen">
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                </div>
            </div>
        );
    }

    const result = job.analysis_result;
    const score = result?.final_score || 0;
    const scoreColor = score >= 80 ? 'text-green-400' : score >= 60 ? 'text-yellow-400' : 'text-red-400';
    const currentStatus = STATUS_OPTIONS.find(s => s.value === job.status) || STATUS_OPTIONS[0];

    return (
        <main className="min-h-screen bg-[var(--bg-primary)]">
            <Header />

            <div className="max-w-5xl mx-auto px-6 py-8">
                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
                    <div>
                        <motion.div
                            initial={{ opacity: 0, y: -20 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <button
                                onClick={() => router.push('/jobs')}
                                className="text-sm text-[var(--text-muted)] hover:text-[var(--text-primary)] mb-4 flex items-center gap-1 transition-colors cursor-pointer"
                            >
                                ← Back to Jobs
                            </button>
                            <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">{job.job_posting.job_title}</h1>
                            <p className="text-xl text-[var(--text-secondary)] mb-4">{job.job_posting.company_name}</p>

                            <div className="flex flex-wrap items-center gap-4 text-sm text-[var(--text-muted)]">
                                {job.job_posting.location && (
                                    <span className="flex items-center gap-1.5">
                                        {ICONS.location}
                                        {job.job_posting.location}
                                    </span>
                                )}
                                {job.job_posting.salary_range && (
                                    <span className={`flex items-center gap-1.5 ${job.job_posting.salary_range.toLowerCase().includes('estimated') ? 'text-amber-600/80 italic' : ''}`} title={job.job_posting.salary_range.toLowerCase().includes('estimated') ? "Estimated based on market data" : "Salary from job posting"}>
                                        {ICONS.money}
                                        {job.job_posting.salary_range}
                                    </span>
                                )}
                                {job.job_posting.job_link && (
                                    <a
                                        href={job.job_posting.job_link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 transition-colors"
                                        title="Open job posting"
                                    >
                                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        View Original
                                    </a>
                                )}
                                <span className="bg-[var(--card-bg)] px-2 py-1 rounded-md border border-[var(--border-color)]">
                                    Added {new Date(job.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </motion.div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="flex flex-col items-end gap-4"
                    >
                        {/* Score Circle */}
                        <div className="relative w-32 h-32 flex items-center justify-center">
                            <svg className="w-full h-full transform -rotate-90">
                                <circle
                                    cx="64" cy="64" r="60"
                                    stroke="currentColor" strokeWidth="8"
                                    fill="transparent"
                                    className="text-[var(--border-color)]"
                                />
                                <circle
                                    cx="64" cy="64" r="60"
                                    stroke="currentColor" strokeWidth="8"
                                    fill="transparent"
                                    strokeDasharray={377}
                                    strokeDashoffset={377 - (377 * score) / 100}
                                    className={score >= 80 ? 'text-green-500' : score >= 60 ? 'text-yellow-500' : 'text-red-500'}
                                    strokeLinecap="round"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className={`text-3xl font-bold ${scoreColor}`}>{score}</span>
                                <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider">Match</span>
                            </div>
                        </div>

                        {/* Status Dropdown */}
                        <div className="relative group z-20">
                            <button className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-colors cursor-pointer ${currentStatus.color}`}>
                                <span className={`w-2 h-2 rounded-full ${currentStatus.color.split(' ')[0].replace('/10', '')}`} />
                                {currentStatus.label}
                                <svg className="w-4 h-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7 7" />
                                </svg>
                            </button>
                            <div className="absolute right-0 mt-1 w-40 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl shadow-xl overflow-hidden hidden group-hover:block">
                                {STATUS_OPTIONS.map((opt) => (
                                    <button
                                        key={opt.value}
                                        onClick={() => handleStatusChange(opt.value)}
                                        className="w-full text-left px-4 py-2.5 text-sm text-[var(--text-secondary)] hover:bg-[var(--card-bg)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* LEFT COLUMN: Content (Switches based on Tab) */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Tabs */}
                        <div className="flex items-center gap-6 border-b border-[var(--border-color)]">
                            <button
                                onClick={() => handleTabChange('analysis')}
                                className={`pb-3 text-sm font-medium transition-all relative ${activeTab === 'analysis'
                                    ? 'text-[var(--text-primary)]'
                                    : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                    }`}
                            >
                                Match Analysis
                                {activeTab === 'analysis' && (
                                    <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />
                                )}
                            </button>
                            <button
                                onClick={() => handleTabChange('news')}
                                className={`pb-3 text-sm font-medium transition-all relative ${activeTab === 'news'
                                    ? 'text-[var(--text-primary)]'
                                    : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                    }`}
                            >
                                Company News
                                {activeTab === 'news' && (
                                    <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />
                                )}
                            </button>
                            <button
                                onClick={() => handleTabChange('history')}
                                className={`pb-3 text-sm font-medium transition-all relative ${activeTab === 'history'
                                    ? 'text-[var(--text-primary)]'
                                    : 'text-[var(--text-muted)] hover:text-[var(--text-secondary)]'
                                    }`}
                            >
                                History
                                {activeTab === 'history' && (
                                    <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500" />
                                )}
                            </button>
                        </div>

                        <motion.div
                            key={activeTab}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.2 }}
                            className="space-y-8"
                        >
                            {activeTab === 'analysis' && (
                                <>
                                    {/* Qualifications Mapping */}
                                    {result && (
                                        <section>
                                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                                                Qualifications Impact
                                                <span className="text-xs font-normal text-[var(--text-muted)] bg-[var(--card-bg)] px-2 py-0.5 rounded-full border border-[var(--border-color)]">
                                                    {result.required_matched}/{result.required_total} Required
                                                </span>
                                            </h3>
                                            <div className="space-y-3">
                                                {(result.required_qualifications || []).map((q, i) => (
                                                    <QualificationRow key={i} item={q} />
                                                ))}
                                                {(result.preferred_qualifications || []).map((q, i) => (
                                                    <QualificationRow key={`pref-${i}`} item={q} />
                                                ))}
                                            </div>
                                        </section>
                                    )}

                                    {/* Resume Suggestions */}
                                    {result && result.resume_suggestions && result.resume_suggestions.length > 0 && (
                                        <section>
                                            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Resume Optimization Plan</h3>
                                            <div className="space-y-3">
                                                {result.resume_suggestions.map((s, i) => (
                                                    <SuggestionCard key={i} item={s} />
                                                ))}
                                            </div>
                                        </section>
                                    )}
                                </>
                            )}

                            {activeTab === 'news' && (
                                // NEWS TAB CONTENT
                                <div className="space-y-4">
                                    {loadingNews ? (
                                        <div className="flex flex-col gap-4">
                                            {[1, 2, 3].map(i => (
                                                <div key={i} className="h-24 bg-[var(--card-bg)] rounded-xl animate-pulse" />
                                            ))}
                                        </div>
                                    ) : news && news.articles.length > 0 ? (
                                        news.articles.map((article, i) => (
                                            <a
                                                key={i}
                                                href={article.url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="block p-4 rounded-xl bg-[var(--card-bg)] border border-[var(--border-color)] hover:border-indigo-500/30 hover:shadow-lg transition-all group"
                                            >
                                                <div className="flex justify-between items-start gap-4">
                                                    <div>
                                                        <h4 className="text-[var(--text-primary)] font-medium group-hover:text-indigo-400 transition-colors mb-2">
                                                            {article.title}
                                                        </h4>
                                                        <p className="text-sm text-[var(--text-secondary)] line-clamp-2 mb-3">
                                                            {article.description}
                                                        </p>
                                                        <div className="flex items-center gap-3 text-xs text-[var(--text-muted)]">
                                                            <span className="font-medium text-[var(--text-primary)]">{article.source}</span>
                                                            <span>•</span>
                                                            <span>{new Date(article.published_at).toLocaleDateString()}</span>
                                                        </div>
                                                    </div>
                                                    <svg className="w-5 h-5 text-[var(--text-muted)] group-hover:text-indigo-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                    </svg>
                                                </div>
                                            </a>
                                        ))
                                    ) : (
                                        <div className="text-center py-12 text-[var(--text-muted)] bg-[var(--card-bg)] rounded-xl border border-[var(--border-color)]">
                                            <p>No news found for this company.</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {activeTab === 'history' && (
                                <div className="space-y-4">
                                    {!job.resume_history || job.resume_history.length === 0 ? (
                                        <div className="text-center py-12 text-[var(--text-muted)] bg-[var(--card-bg)] rounded-xl border border-[var(--border-color)]">
                                            <p>No resume history available.</p>
                                        </div>
                                    ) : (
                                        [...job.resume_history].sort((a, b) => b.version - a.version).map((entry) => (
                                            <div key={entry.version} className="p-4 rounded-xl bg-[var(--card-bg)] border border-[var(--border-color)]">
                                                <div className="flex justify-between items-center mb-3">
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-lg font-bold text-[var(--text-primary)]">Version {entry.version}</span>
                                                            {entry.version === job.resume_history!.length && (
                                                                <span className="px-2 py-0.5 text-xs text-indigo-400 bg-indigo-500/10 rounded-full">Current</span>
                                                            )}
                                                        </div>
                                                        <span className="text-xs text-[var(--text-muted)]">
                                                            {new Date(entry.created_at).toLocaleString()}
                                                        </span>
                                                    </div>
                                                    {entry.score !== undefined && (
                                                        <div className="flex flex-col items-end">
                                                            <span className={`text-xl font-bold ${entry.score >= 80 ? 'text-green-400' : entry.score >= 60 ? 'text-yellow-400' : 'text-red-400'}`}>
                                                                {entry.score}
                                                            </span>
                                                            <span className="text-xs text-[var(--text-muted)]">Score</span>
                                                        </div>
                                                    )}
                                                </div>
                                                <details className="group">
                                                    <summary className="text-sm font-medium text-indigo-400 cursor-pointer hover:text-indigo-300 select-none flex items-center gap-1">
                                                        <svg className="w-4 h-4 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                                        </svg>
                                                        View Data
                                                    </summary>
                                                    <div className="mt-3 relative">
                                                        <pre className="p-4 bg-[var(--bg-secondary)] rounded-lg overflow-x-auto text-xs text-[var(--text-secondary)] font-mono border border-[var(--border-color)]">
                                                            {JSON.stringify(entry.resume_data, null, 2)}
                                                        </pre>
                                                        <button
                                                            onClick={() => {
                                                                navigator.clipboard.writeText(JSON.stringify(entry.resume_data, null, 2));
                                                                alert('Copied to clipboard!');
                                                            }}
                                                            className="absolute top-2 right-2 p-1.5 text-indigo-400 hover:text-indigo-300 bg-[var(--card-bg)] rounded-md border border-[var(--border-color)] transition-colors"
                                                            title="Copy to Clipboard"
                                                        >
                                                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                </details>
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </motion.div>
                    </div>

                    {/* RIGHT COLUMN: Skills & Actions */}
                    <div className="space-y-8">
                        {/* Job Link Card */}
                        <div className="p-6 rounded-2xl bg-[var(--card-bg)] border border-[var(--border-color)] backdrop-blur-sm">
                            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-4">Job Link</h3>

                            {isEditingLink ? (
                                <div className="space-y-3">
                                    <input
                                        type="url"
                                        value={jobLinkInput}
                                        onChange={(e) => setJobLinkInput(e.target.value)}
                                        placeholder="https://careers.example.com/job/12345"
                                        className="w-full bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-lg py-2 px-3 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30"
                                        autoFocus
                                    />
                                    <div className="flex gap-2">
                                        <button
                                            onClick={handleSaveJobLink}
                                            disabled={savingLink}
                                            className="flex-1 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 rounded-lg transition-colors cursor-pointer"
                                        >
                                            {savingLink ? 'Saving...' : 'Save'}
                                        </button>
                                        <button
                                            onClick={() => {
                                                setIsEditingLink(false);
                                                setJobLinkInput(job.job_posting.job_link || '');
                                            }}
                                            disabled={savingLink}
                                            className="flex-1 py-2 text-sm font-medium text-[var(--text-secondary)] bg-[var(--bg-primary)] hover:bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg transition-colors cursor-pointer"
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                </div>
                            ) : job.job_posting.job_link ? (
                                <div className="space-y-3">
                                    <a
                                        href={job.job_posting.job_link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 transition-colors break-all"
                                    >
                                        <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                        </svg>
                                        {job.job_posting.job_link}
                                    </a>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => {
                                                setJobLinkInput(job.job_posting.job_link || '');
                                                setIsEditingLink(true);
                                            }}
                                            className="flex-1 py-2 text-sm font-medium text-[var(--text-secondary)] bg-[var(--bg-primary)] hover:bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg transition-colors cursor-pointer"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={handleDeleteJobLink}
                                            disabled={savingLink}
                                            className="flex-1 py-2 text-sm font-medium text-red-400 bg-red-500/10 hover:bg-red-500/20 rounded-lg transition-colors cursor-pointer"
                                        >
                                            {savingLink ? 'Deleting...' : 'Delete'}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <button
                                    onClick={() => {
                                        setJobLinkInput('');
                                        setIsEditingLink(true);
                                    }}
                                    className="w-full flex items-center justify-center gap-2 py-2 text-sm font-medium text-[var(--text-secondary)] bg-[var(--bg-primary)] hover:bg-[var(--bg-secondary)] border border-dashed border-[var(--border-color)] rounded-lg transition-colors cursor-pointer"
                                >
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                    Add Job Link
                                </button>
                            )}
                        </div>

                        {/* Actions Card */}
                        <div className="p-6 rounded-2xl bg-[var(--card-bg)] border border-[var(--border-color)] backdrop-blur-sm">
                            <h3 className="text-sm font-semibold text-[var(--text-secondary)] uppercase tracking-wider mb-4">Actions</h3>

                            <button
                                onClick={handleReevaluate}
                                className="w-full mb-3 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-[var(--text-primary)] bg-[var(--bg-primary)] hover:bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg transition-colors cursor-pointer"
                            >
                                <svg className="w-4 h-4 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                Re-analyze Application
                            </button>

                            <button
                                onClick={handleDelete}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-red-400 bg-red-500/10 hover:bg-red-500/20 rounded-lg transition-colors cursor-pointer"
                            >
                                {ICONS.x}
                                Delete Job Application
                            </button>

                            <div className="mt-4 pt-4 border-t border-[var(--border-color)]">
                                <button
                                    onClick={() => router.push(`/jobs/${job.id}/cover-letter`)}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors cursor-pointer shadow-lg shadow-indigo-500/20"
                                >
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                    </svg>
                                    Cover Letter
                                </button>
                            </div>
                        </div>

                        {/* Skills Cloud */}
                        {result && (
                            <div className="p-6 rounded-2xl bg-[var(--card-bg)] border border-[var(--border-color)] backdrop-blur-sm">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Technical Skills</h3>
                                <div className="flex flex-wrap gap-2 mb-6">
                                    {(result.technical_skills || []).map((s, i) => (
                                        <SkillTag key={i} item={s} />
                                    ))}
                                </div>

                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Soft Skills</h3>
                                <div className="flex flex-wrap gap-2">
                                    {(result.soft_skills || []).map((s, i) => (
                                        <SkillTag key={i} item={s} />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Benefits */}
                        {result && result.compensation_and_benefits && result.compensation_and_benefits.length > 0 && (
                            <div className="p-6 rounded-2xl bg-[var(--card-bg)] border border-[var(--border-color)] backdrop-blur-sm">
                                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Perks & Benefits</h3>
                                <ul className="space-y-2">
                                    {result.compensation_and_benefits.map((b, i) => (
                                        <li key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                            <span className="text-green-500 mt-1">✓</span>
                                            {b}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>
                <ConfirmationModal
                    isOpen={showDeleteConfirm}
                    onClose={() => setShowDeleteConfirm(false)}
                    onConfirm={handleConfirmDelete}
                    title="Delete Job"
                    message="Are you sure you want to delete this job? This action cannot be undone."
                    confirmLabel="Delete Job"
                    isDestructive={true}
                />

                {/* Re-evaluation Modal */}
                <AnimatePresence>
                    {isReevaluating && (
                        <ResumeEditor
                            initialData={reevaluationResume}
                            onSave={handleSubmitReevaluation}
                            onCancel={() => setIsReevaluating(false)}
                            isSubmitting={isSubmittingReevaluation}
                            jobId={job?.id}
                        />
                    )}
                </AnimatePresence>
            </div>
        </main >
    );
}
