
import { useState } from 'react';
import { motion } from 'framer-motion';

// Types derived from backend models
export interface ProfileItem {
    category: string;
    field: string;
    resume_value: string | null;
    linkedin_value: string | null;
    portfolio_value: string | null;
    status: 'match' | 'mismatch' | 'partial';
}

export interface DiscrepancyItem {
    field: string;
    resume: string | null;
    linkedin: string | null;
    portfolio: string | null;
    issue: string;
    severity: 'low' | 'medium' | 'high';
}

export interface SkillsAnalysis {
    matching_skills: string[];
    missing_from_resume: string[];
    missing_from_linkedin: string[];
    missing_from_portfolio: string[];
}

export interface DiscrepancyResult {
    comparison_table: ProfileItem[];
    skills_analysis: SkillsAnalysis;
    mismatches: ProfileItem[];
    partial_presence: ProfileItem[];
    fully_consistent: ProfileItem[];
    discrepancies: DiscrepancyItem[];
    consistency_score: number;
    recommendations: string[];
}

interface DiscrepancyReportViewProps {
    data: any; // Using any initially to handle raw JSON parse, but casting inside
}

export default function DiscrepancyReportView({ data }: DiscrepancyReportViewProps) {
    const report = data as DiscrepancyResult;
    const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'table'>('overview');

    const scoreColor = report.consistency_score >= 90 ? 'text-[var(--success)]' :
        report.consistency_score >= 70 ? 'text-[var(--warning)]' : 'text-[var(--danger)]';

    const scoreBg = report.consistency_score >= 90 ? 'bg-[var(--success)]' :
        report.consistency_score >= 70 ? 'bg-[var(--warning)]' : 'bg-[var(--danger)]';

    return (
        <div className="space-y-8">
            {/* Score Header */}
            <div className="flex items-center gap-6 p-6 bg-[var(--bg-secondary)] rounded-xl border border-[var(--border-color)]">
                <div className="relative w-24 h-24 flex items-center justify-center">
                    <svg className="w-full h-full" viewBox="0 0 36 36">
                        <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="var(--border)"
                            strokeWidth="4"
                        />
                        <path
                            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="4"
                            strokeDasharray={`${report.consistency_score}, 100`}
                            className={scoreColor}
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className={`text-2xl font-bold ${scoreColor}`}>{report.consistency_score}%</span>
                        <span className="text-xs text-[var(--text-muted)] uppercase">Consistent</span>
                    </div>
                </div>
                <div>
                    <h3 className="text-xl font-bold text-[var(--text-primary)]">Profile Consistency Score</h3>
                    <p className="text-[var(--text-secondary)]">
                        {report.consistency_score === 100 ? "Perfect match across all sources!" :
                            "Discrepancies found between your Resume, LinkedIn, and Portfolio."}
                    </p>
                </div>
            </div>

            {/* Navigation Tabs */}
            <div className="flex gap-2 border-b border-[var(--border-color)]">
                {['overview', 'skills', 'table'].map((tab) => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab as any)}
                        className={`px-4 py-2 text-sm font-medium capitalize transition-colors relative ${activeTab === tab
                            ? 'text-[var(--accent)]'
                            : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                            }`}
                    >
                        {tab}
                        {activeTab === tab && (
                            <motion.div
                                layoutId="activeTab"
                                className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--accent)]"
                            />
                        )}
                    </button>
                ))}
            </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
                <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Recommendations */}
                    {report.recommendations?.length > 0 && (
                        <div className="bg-[var(--accent-dim)] border border-[var(--accent-border)] rounded-xl p-6">
                            <h4 className="text-sm font-bold text-[var(--accent)] uppercase tracking-wide mb-4">Recommended Actions</h4>
                            <ul className="space-y-2">
                                {report.recommendations.map((rec, i) => (
                                    <li key={i} className="flex items-start gap-2 text-[var(--text-primary)] text-sm">
                                        <span className="text-[var(--accent)] mt-1">•</span>
                                        {rec}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {/* Discrepancies List */}
                    <div>
                        <h4 className="text-lg font-bold text-[var(--text-primary)] mb-4">Detected Discrepancies</h4>
                        {report.discrepancies?.length > 0 ? (
                            <div className="space-y-4">
                                {report.discrepancies.map((disc, i) => (
                                    <div key={i} className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-4 flex gap-4">
                                        <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${disc.severity === 'high' ? 'bg-[var(--danger)]' : disc.severity === 'medium' ? 'bg-[var(--warning)]' : 'bg-[var(--accent)]'
                                            }`} />
                                        <div className="flex-1">
                                            <div className="flex justify-between items-start mb-1">
                                                <h5 className="font-medium text-[var(--text-primary)]">{disc.field}</h5>
                                                <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${disc.severity === 'high' ? 'bg-[var(--danger-dim)] text-[var(--danger)]' :
                                                    disc.severity === 'medium' ? 'bg-[var(--warning-dim)] text-[var(--warning)]' : 'bg-[var(--accent-dim)] text-[var(--accent)]'
                                                    }`}>
                                                    {disc.severity}
                                                </span>
                                            </div>
                                            <p className="text-sm text-[var(--text-secondary)] mb-3">{disc.issue}</p>
                                            <div className="grid grid-cols-3 gap-2 text-xs bg-[var(--bg-secondary)] p-3 rounded border border-[var(--border-color)]">
                                                <div>
                                                    <span className="block text-[var(--text-muted)] mb-1">Resume</span>
                                                    <span className="text-[var(--text-primary)]">{disc.resume || <span className="text-[var(--text-2)] italic">None</span>}</span>
                                                </div>
                                                <div>
                                                    <span className="block text-[var(--text-muted)] mb-1">LinkedIn</span>
                                                    <span className="text-[var(--text-primary)]">{disc.linkedin || <span className="text-[var(--text-2)] italic">None</span>}</span>
                                                </div>
                                                <div>
                                                    <span className="block text-[var(--text-muted)] mb-1">Portfolio</span>
                                                    <span className="text-[var(--text-primary)]">{disc.portfolio || <span className="text-[var(--text-2)] italic">None</span>}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-[var(--text-muted)] border border-dashed border-[var(--border-color)] rounded-lg">
                                No discrepancies found. Good job!
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Skills Tab */}
            {activeTab === 'skills' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <SkillCard
                        title="Consistent Skills"
                        skills={report.skills_analysis?.matching_skills}
                        type="success"
                        description="Found in at least 2 sources"
                    />
                    <SkillCard
                        title="Missing from Resume"
                        skills={report.skills_analysis?.missing_from_resume}
                        type="warning"
                        description="Present in LinkedIn/Portfolio"
                    />
                    <SkillCard
                        title="Missing from LinkedIn"
                        skills={report.skills_analysis?.missing_from_linkedin}
                        type="warning"
                        description="Present in Resume/Portfolio"
                    />
                    <SkillCard
                        title="Missing from Portfolio"
                        skills={report.skills_analysis?.missing_from_portfolio}
                        type="warning"
                        description="Present in Resume/LinkedIn"
                    />
                </div>
            )}

            {/* Detailed Table Tab */}
            {activeTab === 'table' && (
                <div className="overflow-x-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-[var(--bg-secondary)] text-[var(--text-muted)] uppercase text-xs">
                            <tr>
                                <th className="px-4 py-3 rounded-tl-lg">Category</th>
                                <th className="px-4 py-3">Item</th>
                                <th className="px-4 py-3">Resume</th>
                                <th className="px-4 py-3">LinkedIn</th>
                                <th className="px-4 py-3 rounded-tr-lg">Portfolio</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-color)]">
                            {report.comparison_table?.map((item, i) => (
                                <tr key={i} className={`group hover:bg-[var(--bg-secondary)/50] transition-colors ${item.status === 'mismatch' ? 'bg-[var(--danger-dim)]' : ''
                                    }`}>
                                    <td className="px-4 py-3 font-medium text-[var(--text-secondary)] w-24">{item.category}</td>
                                    <td className="px-4 py-3 text-[var(--text-primary)] w-48">{item.field}</td>
                                    <td className="px-4 py-3">
                                        <ValueCell value={item.resume_value} status={item.status} source="resume" item={item} />
                                    </td>
                                    <td className="px-4 py-3">
                                        <ValueCell value={item.linkedin_value} status={item.status} source="linkedin" item={item} />
                                    </td>
                                    <td className="px-4 py-3">
                                        <ValueCell value={item.portfolio_value} status={item.status} source="portfolio" item={item} />
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function SkillCard({ title, skills, type, description }: { title: string, skills: string[], type: 'success' | 'warning', description: string }) {
    if (!skills || skills.length === 0) return null;

    return (
        <div className={`rounded-xl border p-4 ${type === 'success' ? 'bg-[var(--success-dim)] border-[var(--success-border)]' : 'bg-[var(--warning-dim)] border-[var(--warning-border)]'
            }`}>
            <h4 className={`font-bold mb-1 ${type === 'success' ? 'text-[var(--success)]' : 'text-[var(--warning)]'
                }`}>{title}</h4>
            <p className="text-xs text-[var(--text-muted)] mb-3">{description}</p>
            <div className="flex flex-wrap gap-2">
                {skills.map((skill, i) => (
                    <span key={i} className={`text-xs px-2 py-1 rounded bg-[var(--bg-primary)] border border-[var(--border-color)] ${type === 'success' ? 'text-[var(--success)]' : 'text-[var(--warning)]'
                        }`}>
                        {skill}
                    </span>
                ))}
            </div>
        </div>
    );
}

function ValueCell({ value, status, source, item }: { value: string | null, status: string, source: string, item: ProfileItem }) {
    const isMissing = !value;
    // Simple logic: if mismatch, highlight difference.
    // Ideally we comparing strictly but let's just show red text if status is mismatch

    return (
        <span className={`${isMissing ? 'text-[var(--text-2)] italic' : 'text-[var(--text-secondary)]'} ${status === 'mismatch' ? 'text-[var(--danger)]' : ''
            }`}>
            {value || 'Missing'}
        </span>
    );
}
