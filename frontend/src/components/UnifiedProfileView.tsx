
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface UnifiedProfileViewProps {
    profile: any;
}

export default function UnifiedProfileView({ profile }: UnifiedProfileViewProps) {
    const [activeTab, setActiveTab] = useState<'overview' | 'experience' | 'education' | 'skills' | 'raw'>('overview');

    if (!profile) return null;

    const basics = profile.basics || {};
    const contact = basics.contact_info || {};
    const work = profile.work_experience || [];
    const education = profile.education || [];
    const skills = profile.skills || [];

    // Helper to format dates
    const formatDate = (dateStr: string) => {
        if (!dateStr) return 'Present';
        try {
            // Check if YYYY-MM
            if (/^\d{4}-\d{2}$/.test(dateStr)) {
                const [year, month] = dateStr.split('-');
                return new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString(undefined, { year: 'numeric', month: 'short' });
            }
            return dateStr;
        } catch (e) {
            return dateStr;
        }
    };

    return (
        <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-xl overflow-hidden">
            {/* Header Section */}
            <div className="p-8 border-b border-[var(--border-color)] bg-gradient-to-r from-indigo-500/5 to-purple-500/5">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h2 className="text-3xl font-bold text-[var(--text-primary)]">
                            {basics.name || "Unified Profile"}
                        </h2>
                        {basics.title && (
                            <p className="text-lg text-indigo-400 font-medium mt-1">{basics.title}</p>
                        )}
                        {basics.summary && (
                            <p className="text-[var(--text-secondary)] mt-4 max-w-2xl text-sm leading-relaxed">
                                {basics.summary}
                            </p>
                        )}
                    </div>
                </div>

                {/* Contact Pills */}
                <div className="flex flex-wrap gap-3 mt-6">
                    {contact.email && (
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--bg-secondary)] border border-[var(--border-color)] text-xs text-[var(--text-secondary)]">
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            {contact.email}
                        </div>
                    )}
                    {contact.phone && (
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--bg-secondary)] border border-[var(--border-color)] text-xs text-[var(--text-secondary)]">
                            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            {contact.phone}
                        </div>
                    )}
                    {contact.linkedin_url && (
                        <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0077b5]/10 border border-[#0077b5]/20 text-xs text-[#0077b5] hover:bg-[#0077b5]/20 transition-colors">
                            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                            </svg>
                            LinkedIn
                        </a>
                    )}
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex gap-1 px-4 border-b border-[var(--border-color)] bg-[var(--bg-secondary)]/50 overflow-x-auto">
                {[
                    { id: 'overview', label: 'Overview' },
                    { id: 'experience', label: 'Experience' },
                    { id: 'education', label: 'Education' },
                    { id: 'skills', label: 'Skills' },
                    { id: 'raw', label: 'Raw Data' }
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        className={`px-4 py-3 text-sm font-medium capitalize transition-colors relative whitespace-nowrap ${activeTab === tab.id
                            ? 'text-indigo-400'
                            : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                            }`}
                    >
                        {tab.label}
                        {activeTab === tab.id && (
                            <motion.div
                                layoutId="activeTabProfile"
                                className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500"
                            />
                        )}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="p-6 min-h-[400px]">
                <AnimatePresence mode="wait">
                    {/* Overview Tab */}
                    {activeTab === 'overview' && (
                        <motion.div
                            key="overview"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                            className="space-y-8"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div className="space-y-4">
                                    <h3 className="text-sm font-bold text-[var(--text-muted)] uppercase tracking-wider">Top Skills</h3>
                                    <div className="flex flex-wrap gap-2">
                                        {skills.slice(0, 10).map((skill: string, i: number) => (
                                            <span key={i} className="px-2.5 py-1 text-xs font-medium rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                                                {skill}
                                            </span>
                                        ))}
                                        {skills.length > 10 && (
                                            <span className="px-2.5 py-1 text-xs font-medium rounded-md text-[var(--text-muted)] border border-[var(--border-color)]">
                                                +{skills.length - 10} more
                                            </span>
                                        )}
                                    </div>
                                </div>
                                <div className="space-y-4">
                                    <h3 className="text-sm font-bold text-[var(--text-muted)] uppercase tracking-wider">Education</h3>
                                    {education.length > 0 ? (
                                        education.slice(0, 2).map((edu: any, i: number) => (
                                            <div key={i} className="flex gap-3">
                                                <div className="w-1 h-full min-h-[40px] bg-[var(--border-color)] rounded-full shrink-0" />
                                                <div>
                                                    <div className="font-medium text-[var(--text-primary)]">{edu.institution}</div>
                                                    <div className="text-xs text-[var(--text-secondary)]">{edu.degree}</div>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-sm text-[var(--text-muted)] italic">No education listed</p>
                                    )}
                                </div>
                            </div>

                            <div className="pt-4 border-t border-[var(--border-color)]">
                                <h3 className="text-sm font-bold text-[var(--text-muted)] uppercase tracking-wider mb-4">Latest Experience</h3>
                                {work.length > 0 ? (
                                    <div className="space-y-4">
                                        {work.slice(0, 2).map((job: any, i: number) => (
                                            <div key={i} className="bg-[var(--bg-secondary)] rounded-lg p-4 border border-[var(--border-color)]">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div>
                                                        <div className="font-bold text-[var(--text-primary)]">{job.job_title}</div>
                                                        <div className="text-sm text-indigo-400">{job.company_name}</div>
                                                    </div>
                                                    <div className="text-xs text-[var(--text-muted)] whitespace-nowrap bg-[var(--bg-primary)] px-2 py-1 rounded">
                                                        {formatDate(job.start_date)} - {formatDate(job.end_date)}
                                                    </div>
                                                </div>
                                                <p className="text-sm text-[var(--text-secondary)] line-clamp-2">
                                                    {job.description}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-[var(--text-muted)] italic">No experience listed</p>
                                )}
                            </div>
                        </motion.div>
                    )}

                    {/* Experience Tab */}
                    {activeTab === 'experience' && (
                        <motion.div
                            key="experience"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                            className="space-y-8 relative pl-4"
                        >
                            {/* Timeline line */}
                            <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-[var(--border-color)]" />

                            {work.length > 0 ? (
                                work.map((job: any, i: number) => (
                                    <div key={i} className="relative pl-8">
                                        {/* Timeline Dot */}
                                        <div className="absolute left-1.5 top-2 w-5 h-5 rounded-full border-4 border-[var(--card-bg)] bg-indigo-500 -translate-x-1/2" />

                                        <div className="bg-[var(--bg-secondary)]/50 rounded-xl p-6 border border-[var(--border-color)] hover:border-indigo-500/30 transition-colors">
                                            <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-2 mb-4">
                                                <div>
                                                    <h3 className="text-lg font-bold text-[var(--text-primary)]">{job.job_title}</h3>
                                                    <div className="text-indigo-400 font-medium">{job.company_name}</div>
                                                    {job.location && (
                                                        <div className="text-xs text-[var(--text-muted)] mt-1 flex items-center gap-1">
                                                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                                            </svg>
                                                            {job.location}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="text-xs font-mono text-[var(--text-muted)] bg-[var(--card-bg)] px-3 py-1.5 rounded-full border border-[var(--border-color)] whitespace-nowrap">
                                                    {formatDate(job.start_date)} — {formatDate(job.end_date)}
                                                </div>
                                            </div>

                                            {job.description && (
                                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4 whitespace-pre-wrap">
                                                    {job.description}
                                                </p>
                                            )}

                                            {job.achievements && job.achievements.length > 0 && (
                                                <ul className="space-y-1">
                                                    {job.achievements.map((item: string, j: number) => (
                                                        <li key={j} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                                            <span className="text-indigo-400 mt-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
                                                            {item}
                                                        </li>
                                                    ))}
                                                </ul>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-12 text-[var(--text-muted)] border border-dashed border-[var(--border-color)] rounded-xl bg-[var(--bg-secondary)]/30 mx-8">
                                    No work experience found in your documents.
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Education Tab */}
                    {activeTab === 'education' && (
                        <motion.div
                            key="education"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                            className="grid grid-cols-1 md:grid-cols-2 gap-4"
                        >
                            {education.length > 0 ? (
                                education.map((edu: any, i: number) => (
                                    <div key={i} className="bg-[var(--bg-secondary)] rounded-xl p-6 border border-[var(--border-color)] flex gap-4 items-start group hover:border-indigo-500/30 transition-colors">
                                        <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 shrink-0 group-hover:scale-110 transition-transform">
                                            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 14l9-5-9-5-9 5 9 5z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
                                            </svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-[var(--text-primary)]">{edu.institution}</h3>
                                            <div className="text-indigo-400 font-medium mb-1">{edu.degree}</div>
                                            {(edu.start_date || edu.end_date) && (
                                                <div className="text-xs text-[var(--text-muted)]">
                                                    {edu.start_date} - {edu.end_date}
                                                </div>
                                            )}
                                            {edu.gpa && (
                                                <div className="mt-2 text-xs font-mono bg-green-500/10 text-green-400 px-2 py-1 rounded inline-block">
                                                    GPA: {edu.gpa}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="col-span-full text-center py-12 text-[var(--text-muted)] border border-dashed border-[var(--border-color)] rounded-xl bg-[var(--bg-secondary)]/30">
                                    No education found.
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Skills Tab */}
                    {activeTab === 'skills' && (
                        <motion.div
                            key="skills"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.2 }}
                        >
                            <h3 className="text-sm font-bold text-[var(--text-muted)] uppercase tracking-wider mb-6">All Skills</h3>
                            <div className="flex flex-wrap gap-3">
                                {skills.map((skill: string, i: number) => (
                                    <div key={i} className="px-4 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg text-sm text-[var(--text-primary)] hover:border-indigo-500/50 hover:text-indigo-400 transition-colors">
                                        {skill}
                                    </div>
                                ))}
                            </div>
                            {skills.length === 0 && (
                                <div className="text-center py-12 text-[var(--text-muted)] border border-dashed border-[var(--border-color)] rounded-xl bg-[var(--bg-secondary)]/30">
                                    No skills extracted.
                                </div>
                            )}
                        </motion.div>
                    )}

                    {/* Raw Tab */}
                    {activeTab === 'raw' && (
                        <motion.div
                            key="raw"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="bg-gray-900 rounded-xl p-4 overflow-auto max-h-[600px]"
                        >
                            <pre className="text-xs text-gray-300 font-mono">
                                {JSON.stringify(profile, null, 2)}
                            </pre>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
