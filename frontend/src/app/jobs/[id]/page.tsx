'use client';

import { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/utils/store';
import { api, Job, JobLensSession } from '@/utils/api';
import Header from '@/components/Header';
import { subscribeToJobLens } from '@/hooks/useGlobalWebSocket';
import ConfirmationModal from '@/components/ConfirmationModal';

// ─── Step metadata ────────────────────────────────────────────────────────────

const STEPS = [
    { key: 'profile_extract', label: 'Profile Extract', icon: '①' },
    { key: 'jd_parse',        label: 'JD Parse',        icon: '②' },
    { key: 'company_intel',   label: 'Company Intel',   icon: '③' },
    { key: 'match_analysis',  label: 'Match Analysis',  icon: '④' },
    { key: 'contact_strategy',label: 'Contact Strategy',icon: '⑤' },
    { key: 'action_plan',     label: 'Action Plan',     icon: '⑥' },
] as const;

type StepKey = typeof STEPS[number]['key'];
type StepStatus = 'idle' | 'running' | 'done' | 'error';

// Map session fields to step keys
const SESSION_FIELD: Record<StepKey, keyof JobLensSession> = {
    profile_extract: 'extracted_profile',
    jd_parse:        'parsed_jd',
    company_intel:   'company_intel',
    match_analysis:  'match_analysis',
    contact_strategy:'contact_strategy',
    action_plan:     'action_plan',
};

const STATUS_OPTIONS = [
    { value: 'tracked',   label: 'Tracked' },
    { value: 'applied',   label: 'Applied' },
    { value: 'interview', label: 'Interview' },
    { value: 'offer',     label: 'Offer' },
    { value: 'rejected',  label: 'Rejected' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Safely convert unknown to string for JSX rendering */
const s = (val: unknown, fallback = '—'): string =>
    val != null && val !== '' ? String(val) : fallback;

/** Array from unknown field */
function arr<T = unknown>(val: unknown): T[] {
    return Array.isArray(val) ? (val as T[]) : [];
}

// ─── Utility ──────────────────────────────────────────────────────────────────

function ScoreBadge({ score, label }: { score: number; label: string }) {
    const color = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : score >= 40 ? 'var(--accent)' : 'var(--danger)';
    return (
        <div className="flex flex-col items-center" style={{ minWidth: 52 }}>
            <div
                className="text-2xl font-semibold tabular-nums"
                style={{ color, fontVariantNumeric: 'tabular-nums' }}
            >
                {score}
            </div>
            <div className="text-xs uppercase tracking-wider mt-0.5" style={{ color: 'var(--text-3)' }}>
                {label}
            </div>
        </div>
    );
}

function TagList({ items, color }: { items: string[]; color?: string }) {
    return (
        <div className="flex flex-wrap gap-1.5 mt-2">
            {items.map((item, i) => (
                <span
                    key={i}
                    className="text-xs px-2 py-0.5 rounded"
                    style={{ background: 'var(--surface)', color: color || 'var(--text-2)', border: '1px solid var(--border)' }}
                >
                    {item}
                </span>
            ))}
        </div>
    );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="mb-4">
            <p className="text-xs uppercase tracking-widest mb-2" style={{ color: 'var(--text-3)' }}>{title}</p>
            {children}
        </div>
    );
}

function AIVerdict({ text }: { text: string }) {
    return (
        <div className="mt-4 p-3 rounded-lg" style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
            <p className="text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--accent)' }}>AI Verdict</p>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>{text}</p>
        </div>
    );
}

// ─── Step Content Renderers ───────────────────────────────────────────────────

function StepContent({ stepKey, data }: { stepKey: StepKey; data: Record<string, unknown> }) {
    switch (stepKey) {
        case 'profile_extract': return <ProfileExtractView data={data} />;
        case 'jd_parse':        return <JDParseView data={data} />;
        case 'company_intel':   return <CompanyIntelView data={data} />;
        case 'match_analysis':  return <MatchAnalysisView data={data} />;
        case 'contact_strategy':return <ContactStrategyView data={data} />;
        case 'action_plan':     return <ActionPlanView data={data} />;
        default:                return null;
    }
}

function ProfileExtractView({ data }: { data: Record<string, unknown> }) {
    const skills = data.technical_skills as Record<string, string[]> | undefined;
    const experiences = arr<Record<string, unknown>>(data.top_experiences);
    return (
        <div>
            <div className="flex gap-6 mb-4 flex-wrap">
                {[
                    ['Title', data.current_title],
                    ['Experience', data.years_of_experience != null ? s(data.years_of_experience) + 'y' : null],
                    ['Role Type', data.primary_role_type],
                ].filter(([, v]) => v != null).map(([label, val]) => (
                    <div key={s(label)}>
                        <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--text-3)' }}>{s(label)}</p>
                        <p className="text-sm font-medium mt-0.5" style={{ color: 'var(--text-1)' }}>{s(val)}</p>
                    </div>
                ))}
            </div>
            {Boolean(skills) && (
                <Section title="Technical Skills">
                    {Object.entries(skills!).filter(([, v]) => v.length > 0).map(([cat, items]) => (
                        <div key={cat} className="mb-2">
                            <p className="text-xs capitalize" style={{ color: 'var(--text-3)' }}>{cat.replace(/_/g, ' ')}</p>
                            <TagList items={items} />
                        </div>
                    ))}
                </Section>
            )}
            {experiences.length > 0 && (
                <Section title="Key Experiences">
                    {experiences.map((exp, i) => (
                        <div key={i} className="mb-3 p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                            <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{s(exp.title)} @ {s(exp.company)}</p>
                            <p className="text-xs mt-0.5 mb-2" style={{ color: 'var(--text-3)' }}>{s(exp.duration)}</p>
                            {arr<string>(exp.key_achievements).map((ach, j) => (
                                <p key={j} className="text-xs mb-1" style={{ color: 'var(--text-2)' }}>· {ach}</p>
                            ))}
                        </div>
                    ))}
                </Section>
            )}
            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

function JDParseView({ data }: { data: Record<string, unknown> }) {
    const greenFlags = arr<string>(data.green_flags);
    const redFlags = arr<string>(data.red_flags);
    return (
        <div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-3 mb-4">
                {[
                    ['Company', data.company_name],
                    ['Role', data.role_title],
                    ['Level', data.level],
                    ['Location', data.location],
                    ['Remote', data.remote_policy],
                    ['Experience', data.years_experience_required],
                    ['Salary', data.salary_range],
                ].map(([label, val]) => (
                    <div key={s(label)}>
                        <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--text-3)' }}>{s(label)}</p>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-1)' }}>{s(val)}</p>
                    </div>
                ))}
            </div>
            {arr<string>(data.required_skills).length > 0 && (
                <Section title="Required Skills">
                    <TagList items={arr<string>(data.required_skills)} color="var(--text-1)" />
                </Section>
            )}
            {arr<string>(data.tech_stack).length > 0 && (
                <Section title="Tech Stack">
                    <TagList items={arr<string>(data.tech_stack)} />
                </Section>
            )}
            {arr<string>(data.ats_keywords).length > 0 && (
                <Section title="ATS Keywords">
                    <TagList items={arr<string>(data.ats_keywords)} color="var(--accent)" />
                </Section>
            )}
            {greenFlags.length > 0 && (
                <Section title="Green Flags">
                    {greenFlags.map((f, i) => (
                        <p key={i} className="text-sm mb-1" style={{ color: 'var(--success)' }}>✓ {f}</p>
                    ))}
                </Section>
            )}
            {redFlags.length > 0 && (
                <Section title="Red Flags">
                    {redFlags.map((f, i) => (
                        <p key={i} className="text-sm mb-1" style={{ color: 'var(--danger)' }}>⚠ {f}</p>
                    ))}
                </Section>
            )}
            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

function CompanyIntelView({ data }: { data: Record<string, unknown> }) {
    const talkingPoints = arr<string>(data.talking_points);
    const watchOuts = arr<string>(data.watch_outs);
    return (
        <div>
            <div className="grid grid-cols-3 gap-3 mb-4">
                {[
                    ['Stage', data.funding_stage],
                    ['Size', data.company_size],
                    ['Market', data.market_position],
                ].map(([label, val]) => (
                    <div key={s(label)} className="p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                        <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--text-3)' }}>{s(label)}</p>
                        <p className="text-sm mt-0.5 font-medium" style={{ color: 'var(--text-1)' }}>{s(val)}</p>
                    </div>
                ))}
            </div>
            {Boolean(data.company_description) && (
                <Section title="About">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>{s(data.company_description)}</p>
                </Section>
            )}
            {Boolean(data.engineering_culture) && (
                <Section title="Engineering Culture">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>{s(data.engineering_culture)}</p>
                </Section>
            )}
            {talkingPoints.length > 0 && (
                <Section title="Talking Points for Interview">
                    {talkingPoints.map((p, i) => (
                        <p key={i} className="text-sm mb-1.5" style={{ color: 'var(--text-2)' }}>· {p}</p>
                    ))}
                </Section>
            )}
            {watchOuts.length > 0 && (
                <Section title="Watch Outs">
                    {watchOuts.map((w, i) => (
                        <p key={i} className="text-sm mb-1" style={{ color: 'var(--warning)' }}>⚠ {w}</p>
                    ))}
                </Section>
            )}
            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

function MatchAnalysisView({ data }: { data: Record<string, unknown> }) {
    const overallScore = (data.overall_score as number) ?? 0;
    const scores = [
        { label: 'Technical', score: (data.technical_score as number) ?? 0 },
        { label: 'Experience', score: (data.experience_score as number) ?? 0 },
        { label: 'Projects', score: (data.project_relevance_score as number) ?? 0 },
        { label: 'Culture', score: (data.culture_fit_score as number) ?? 0 },
    ];
    const strengths = arr<{ area: string; detail: string }>(data.strengths);
    const gaps = arr<{ area: string; severity: string; detail: string; quick_fix: string }>(data.gaps);
    const uniqueAngles = arr<string>(data.unique_angles);

    return (
        <div>
            {/* Score row */}
            <div className="flex items-center gap-6 p-4 rounded-lg mb-4" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                <div className="flex flex-col items-center">
                    <div className="text-3xl font-semibold" style={{ color: overallScore >= 70 ? 'var(--success)' : 'var(--accent)' }}>
                        {overallScore}
                    </div>
                    <div className="text-xs uppercase tracking-widest mt-0.5" style={{ color: 'var(--text-3)' }}>Overall</div>
                </div>
                <div className="w-px h-10" style={{ background: 'var(--border)' }} />
                <div className="flex gap-5 flex-wrap">
                    {scores.map(sc => <ScoreBadge key={sc.label} score={sc.score} label={sc.label} />)}
                </div>
                {Boolean(data.verdict) && (
                    <>
                        <div className="w-px h-10" style={{ background: 'var(--border)' }} />
                        <span className="text-sm font-medium px-2 py-1 rounded" style={{ background: 'var(--accent-dim)', color: 'var(--accent)', border: '1px solid var(--accent-border)' }}>
                            {s(data.verdict)}
                        </span>
                    </>
                )}
            </div>

            {Boolean(data.tailored_pitch) && (
                <Section title="Tailored Pitch">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)', fontStyle: 'italic' }}>&#34;{s(data.tailored_pitch)}&#34;</p>
                </Section>
            )}

            {strengths.length > 0 && (
                <Section title="Strengths">
                    {strengths.map((st, i) => (
                        <div key={i} className="mb-2 flex gap-2">
                            <span className="text-[var(--success)] mt-0.5 flex-shrink-0">✓</span>
                            <div>
                                <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{st.area}</p>
                                <p className="text-xs mt-0.5" style={{ color: 'var(--text-2)' }}>{st.detail}</p>
                            </div>
                        </div>
                    ))}
                </Section>
            )}

            {gaps.length > 0 && (
                <Section title="Gaps">
                    {gaps.map((g, i) => {
                        const severityColor = g.severity === 'critical' ? 'var(--danger)' : g.severity === 'moderate' ? 'var(--warning)' : 'var(--text-3)';
                        return (
                            <div key={i} className="mb-3 p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="text-xs font-medium" style={{ color: severityColor }}>{g.severity}</span>
                                    <span className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{g.area}</span>
                                </div>
                                <p className="text-xs mb-1" style={{ color: 'var(--text-2)' }}>{g.detail}</p>
                                <p className="text-xs" style={{ color: 'var(--accent)' }}>→ {g.quick_fix}</p>
                            </div>
                        );
                    })}
                </Section>
            )}

            {uniqueAngles.length > 0 && (
                <Section title="Unique Angles">
                    {uniqueAngles.map((a, i) => (
                        <p key={i} className="text-sm mb-1.5" style={{ color: 'var(--text-2)' }}>· {a}</p>
                    ))}
                </Section>
            )}

            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

function ContactStrategyView({ data }: { data: Record<string, unknown> }) {
    const contacts = arr<Record<string, unknown>>(data.contacts);
    return (
        <div>
            {Boolean(data.networking_importance) && (
                <div className="mb-4 flex items-center gap-2">
                    <span className="text-xs" style={{ color: 'var(--text-3)' }}>Networking importance:</span>
                    <span className="text-xs font-medium" style={{ color: 'var(--text-1)' }}>{s(data.networking_importance)}</span>
                </div>
            )}
            {contacts.length > 0 && (
                <Section title="Contacts to Reach">
                    {contacts.map((c, i) => (
                        <div key={i} className="mb-3 p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                            <div className="flex items-center justify-between mb-1">
                                <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>{s(c.title)}</p>
                                <span className="text-xs uppercase tracking-wider px-1.5 py-0.5 rounded" style={{
                                    background: c.priority === 'high' ? 'var(--accent-dim)' : 'var(--surface)',
                                    color: c.priority === 'high' ? 'var(--accent)' : 'var(--text-3)',
                                    border: '1px solid var(--border)',
                                }}>
                                    {s(c.priority)}
                                </span>
                            </div>
                            <p className="text-xs mb-2" style={{ color: 'var(--text-3)' }}>{s(c.where_to_find)}</p>
                            <p className="text-xs mb-2" style={{ color: 'var(--text-2)' }}>{s(c.why_they_matter)}</p>
                            <div className="p-2 rounded" style={{ background: 'var(--bg)', border: '1px solid var(--border)' }}>
                                <p className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-3)' }}>Message Template</p>
                                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-2)', fontFamily: 'monospace' }}>{s(c.outreach_message)}</p>
                            </div>
                        </div>
                    ))}
                </Section>
            )}
            {Boolean(data.referral_strategy) && (
                <Section title="Referral Strategy">
                    <p className="text-sm leading-relaxed" style={{ color: 'var(--text-2)' }}>{s(data.referral_strategy)}</p>
                </Section>
            )}
            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

function ActionPlanView({ data }: { data: Record<string, unknown> }) {
    const resumeEdits = arr<Record<string, unknown>>(data.resume_edits);
    const interviewPrep = arr<Record<string, unknown>>(data.interview_prep);
    const followUp = arr<Record<string, unknown>>(data.follow_up_strategy);
    const coverLetter = data.cover_letter_plan as Record<string, unknown> | undefined;
    const prepDays = data.prep_days_needed as number | undefined;
    return (
        <div>
            {prepDays != null && (
                <div className="mb-4 p-3 rounded-lg flex items-center gap-3" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                    <span className="text-2xl font-semibold" style={{ color: 'var(--accent)' }}>{prepDays}</span>
                    <div>
                        <p className="text-sm font-medium" style={{ color: 'var(--text-1)' }}>Days of prep recommended</p>
                        <p className="text-xs" style={{ color: 'var(--text-3)' }}>Based on your profile vs. job requirements</p>
                    </div>
                </div>
            )}
            {resumeEdits.length > 0 && (
                <Section title="Resume Edits">
                    {resumeEdits.map((e, i) => (
                        <div key={i} className="mb-2 flex gap-2 items-start">
                            <span className="text-xs px-1.5 py-0.5 rounded flex-shrink-0 mt-0.5" style={{
                                background: e.action === 'add' ? 'var(--success-dim)' : e.action === 'remove' ? 'var(--danger-dim)' : 'var(--warning-dim)',
                                color: e.action === 'add' ? 'var(--success)' : e.action === 'remove' ? 'var(--danger)' : 'var(--warning)',
                            }}>
                                {s(e.action)}
                            </span>
                            <div>
                                <p className="text-xs font-medium" style={{ color: 'var(--text-3)' }}>{s(e.section)}</p>
                                <p className="text-sm" style={{ color: 'var(--text-1)' }}>{s(e.detail)}</p>
                            </div>
                        </div>
                    ))}
                </Section>
            )}
            {Boolean(coverLetter) && (
                <Section title="Cover Letter Plan">
                    <div className="p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                        {Boolean(coverLetter?.opening_hook) && (
                            <p className="text-sm mb-2" style={{ color: 'var(--text-2)', fontStyle: 'italic' }}>&#34;{s(coverLetter?.opening_hook)}&#34;</p>
                        )}
                        {arr<string>(coverLetter?.key_points).map((p, i) => (
                            <p key={i} className="text-xs mb-1" style={{ color: 'var(--text-2)' }}>· {p}</p>
                        ))}
                    </div>
                </Section>
            )}
            {interviewPrep.length > 0 && (
                <Section title="Interview Prep Topics">
                    {interviewPrep.map((t, i) => (
                        <div key={i} className="mb-3 p-3 rounded-lg" style={{ background: 'var(--surface)', border: '1px solid var(--border)' }}>
                            <p className="text-sm font-medium mb-1" style={{ color: 'var(--text-1)' }}>{s(t.topic)}</p>
                            <p className="text-xs italic mb-1" style={{ color: 'var(--text-2)' }}>Q: {s(t.likely_question)}</p>
                            <p className="text-xs" style={{ color: 'var(--text-3)' }}>Testing: {s(t.what_theyre_testing)}</p>
                        </div>
                    ))}
                </Section>
            )}
            {followUp.length > 0 && (
                <Section title="Follow-up Strategy">
                    {followUp.map((f, i) => (
                        <div key={i} className="mb-2 flex gap-3 items-start">
                            <span className="text-xs px-2 py-0.5 rounded flex-shrink-0" style={{ background: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-3)' }}>
                                {s(f.day)}
                            </span>
                            <div>
                                <p className="text-sm" style={{ color: 'var(--text-1)' }}>{s(f.action)}</p>
                                <p className="text-xs mt-0.5" style={{ color: 'var(--text-3)' }}>→ {s(f.who)}</p>
                            </div>
                        </div>
                    ))}
                </Section>
            )}
            {Boolean(data.ai_verdict) && <AIVerdict text={s(data.ai_verdict)} />}
        </div>
    );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = use(params);
    const router = useRouter();
    const { token, _hasHydrated } = useStore();

    const [job, setJob] = useState<Job | null>(null);
    const [session, setSession] = useState<JobLensSession | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeStep, setActiveStep] = useState<StepKey>('action_plan');
    const [stepStatuses, setStepStatuses] = useState<Record<StepKey, StepStatus>>({
        profile_extract: 'idle',
        jd_parse: 'idle',
        company_intel: 'idle',
        match_analysis: 'idle',
        contact_strategy: 'idle',
        action_plan: 'idle',
    });
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [notes, setNotes] = useState('');
    const [savingNotes, setSavingNotes] = useState(false);

    // Load job + session
    useEffect(() => {
        if (!_hasHydrated || !token) return;
        if (!token) { router.push('/'); return; }
        load();
    }, [_hasHydrated, token, id]);

    const load = async () => {
        setLoading(true);
        try {
            const { job: j, session: s } = await api.getJobWithSession(id);
            if (!j) { router.push('/jobs'); return; }
            setJob(j);
            setNotes(j.user_notes || '');
            setSession(s);
            if (s) initStepStatuses(s);
        } finally {
            setLoading(false);
        }
    };

    const initStepStatuses = (s: JobLensSession) => {
        setStepStatuses({
            profile_extract: s.extracted_profile ? 'done' : 'idle',
            jd_parse:        s.parsed_jd        ? 'done' : 'idle',
            company_intel:   s.company_intel     ? 'done' : 'idle',
            match_analysis:  s.match_analysis    ? 'done' : 'idle',
            contact_strategy:s.contact_strategy  ? 'done' : 'idle',
            action_plan:     s.action_plan       ? 'done' : 'idle',
        });
        // Default to Action Plan; fall back to last completed step if not ready
        if (s.action_plan) {
            setActiveStep('action_plan');
        } else {
            const lastDone = [...STEPS].reverse().find(step => s[SESSION_FIELD[step.key]]);
            if (lastDone) setActiveStep(lastDone.key);
        }
    };

    // Subscribe to live pipeline events
    useEffect(() => {
        if (!session?.id) return;
        const unsub = subscribeToJobLens(session.id, (data) => {
            const type = data.type as string;
            const step = data.step as StepKey | undefined;

            if (type === 'joblens_step_started' && step) {
                setStepStatuses(prev => ({ ...prev, [step]: 'running' }));
                setActiveStep(step);
            } else if (type === 'joblens_step_complete' && step) {
                const stepData = data.data as Record<string, unknown>;
                setStepStatuses(prev => ({ ...prev, [step]: 'done' }));
                setSession(prev => {
                    if (!prev) return prev;
                    return { ...prev, [SESSION_FIELD[step]]: stepData };
                });
                // auto-select completed step
                setActiveStep(step);
            } else if (type === 'joblens_step_failed' && step) {
                setStepStatuses(prev => ({ ...prev, [step]: 'error' }));
            } else if (type === 'joblens_pipeline_complete') {
                // Reload to get final job data
                load();
            }
        });
        return unsub;
    }, [session?.id]);

    const handleStatusChange = async (newStatus: string) => {
        if (!job) return;
        try {
            const updated = await api.updateJob(job.id, { status: newStatus as Job['status'] });
            setJob(updated);
        } catch {}
    };

    const handleSaveNotes = async () => {
        if (!job) return;
        setSavingNotes(true);
        try {
            const updated = await api.updateJob(job.id, { user_notes: notes });
            setJob(updated);
        } finally {
            setSavingNotes(false);
        }
    };

    const handleDelete = async () => {
        if (!job) return;
        await api.deleteJob(job.id);
        router.push('/jobs');
    };

    if (!_hasHydrated || loading) {
        return (
            <div className="min-h-screen" style={{ background: 'var(--bg)' }}>
                <Header />
                <div className="flex items-center justify-center h-[80vh]">
                    <div className="w-6 h-6 rounded-full animate-spin" style={{ border: '2px solid var(--border-strong)', borderTopColor: 'var(--accent)' }} />
                </div>
            </div>
        );
    }

    if (!job) return null;

    const matchScore = session?.match_analysis
        ? (session.match_analysis as Record<string, unknown>).overall_score as number
        : job.analysis_result?.final_score;

    const companyName = (job.job_posting?.company_name as string) || 'Unknown';
    const jobTitle   = (job.job_posting?.job_title as string) || 'Untitled Position';
    const isAnalyzing = job.status === 'analyzing' && STEPS.some(s => stepStatuses[s.key] === 'running');

    return (
        <main className="min-h-screen" style={{ background: 'var(--bg)' }}>
            <Header />

            <div className="max-w-screen-xl mx-auto px-8 py-6">
                {/* Page Header */}
                <div className="flex items-start justify-between mb-6">
                    <div>
                        <button
                            onClick={() => router.push('/jobs')}
                            className="text-sm mb-2 cursor-pointer transition-colors"
                            style={{ color: 'var(--text-3)', background: 'none', border: 'none', padding: 0 }}
                            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-2)'; }}
                            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-3)'; }}
                        >
                            ← Jobs
                        </button>
                        <h1 className="text-lg font-semibold" style={{ color: 'var(--text-1)' }}>{jobTitle}</h1>
                        <p className="text-sm mt-0.5" style={{ color: 'var(--text-3)' }}>{companyName}</p>
                    </div>

                    {/* Right side: score + status + delete */}
                    <div className="flex items-center gap-4">
                        {matchScore != null && (
                            <div className="text-right">
                                <div className="text-2xl font-semibold tabular-nums" style={{ color: (matchScore as number) >= 70 ? 'var(--success)' : 'var(--accent)' }}>
                                    {matchScore as number}
                                </div>
                                <p className="text-xs uppercase tracking-widest" style={{ color: 'var(--text-3)' }}>Match</p>
                            </div>
                        )}

                        {/* Status selector */}
                        <select
                            value={job.status}
                            onChange={e => handleStatusChange(e.target.value)}
                            className="text-sm rounded-md px-2 py-1.5 cursor-pointer focus:outline-none"
                            style={{
                                background: 'var(--surface)',
                                border: '1px solid var(--border)',
                                color: 'var(--text-2)',
                            }}
                        >
                            {STATUS_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>

                        <button
                            onClick={() => setShowDeleteConfirm(true)}
                            className="p-1.5 rounded-md cursor-pointer transition-colors"
                            style={{ color: 'var(--text-3)', background: 'transparent', border: '1px solid var(--border)' }}
                            onMouseEnter={e => {
                                (e.currentTarget as HTMLButtonElement).style.color = 'var(--danger)';
                                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--danger-border)';
                            }}
                            onMouseLeave={e => {
                                (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-3)';
                                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)';
                            }}
                            title="Delete job"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Main layout: left step nav + right content */}
                <div className="flex gap-6">
                    {/* Step sidebar */}
                    <div className="flex-shrink-0 w-44">
                        <div className="rounded-lg overflow-hidden" style={{ border: '1px solid var(--border)' }}>
                            {STEPS.map((step, idx) => {
                                const status = stepStatuses[step.key];
                                const hasData = session?.[SESSION_FIELD[step.key]];
                                const isActive = activeStep === step.key;

                                return (
                                    <button
                                        key={step.key}
                                        onClick={() => hasData && setActiveStep(step.key)}
                                        disabled={!hasData}
                                        className="w-full flex items-center gap-2.5 px-3 py-2.5 text-left transition-colors"
                                        style={{
                                            background: isActive ? 'var(--card)' : 'var(--surface)',
                                            borderBottom: idx < STEPS.length - 1 ? '1px solid var(--border)' : 'none',
                                            cursor: hasData ? 'pointer' : 'default',
                                            borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
                                        }}
                                    >
                                        {/* Status dot */}
                                        <span className="flex-shrink-0">
                                            {status === 'running' ? (
                                                <span className="w-2 h-2 rounded-full inline-block animate-pulse" style={{ background: 'var(--accent)' }} />
                                            ) : status === 'done' ? (
                                                <span className="w-2 h-2 rounded-full inline-block" style={{ background: 'var(--success)' }} />
                                            ) : status === 'error' ? (
                                                <span className="w-2 h-2 rounded-full inline-block" style={{ background: 'var(--danger)' }} />
                                            ) : (
                                                <span className="w-2 h-2 rounded-full inline-block" style={{ background: 'var(--border-strong)' }} />
                                            )}
                                        </span>
                                        <span
                                            className="text-sm leading-snug"
                                            style={{ color: isActive ? 'var(--text-1)' : status === 'idle' ? 'var(--text-3)' : 'var(--text-2)' }}
                                        >
                                            {step.label}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Notes */}
                        <div className="mt-4">
                            <p className="text-xs uppercase tracking-widest mb-1.5" style={{ color: 'var(--text-3)' }}>Notes</p>
                            <textarea
                                value={notes}
                                onChange={e => setNotes(e.target.value)}
                                onBlur={handleSaveNotes}
                                placeholder="Your notes..."
                                rows={4}
                                className="w-full rounded-md px-2.5 py-2 text-sm resize-none focus:outline-none transition-colors"
                                style={{
                                    background: 'var(--card)',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-1)',
                                }}
                                onFocus={e => { (e.target as HTMLTextAreaElement).style.borderColor = 'var(--border-strong)'; }}
                            />
                        </div>
                    </div>

                    {/* Step content */}
                    <div className="flex-1 min-w-0">
                        {/* Analyzing banner */}
                        {isAnalyzing && (
                            <div className="mb-4 px-4 py-3 rounded-lg flex items-center gap-3" style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent-border)' }}>
                                <span className="w-2 h-2 rounded-full animate-pulse flex-shrink-0" style={{ background: 'var(--accent)' }} />
                                <p className="text-sm" style={{ color: 'var(--accent)' }}>
                                    JobLens pipeline is running — results appear as each step completes
                                </p>
                            </div>
                        )}

                        {/* Step card */}
                        {(() => {
                            const stepMeta = STEPS.find(s => s.key === activeStep)!;
                            const data = session?.[SESSION_FIELD[activeStep]] as Record<string, unknown> | undefined;

                            if (!data) {
                                const status = stepStatuses[activeStep];
                                return (
                                    <div
                                        className="rounded-lg p-8 flex flex-col items-center justify-center text-center"
                                        style={{ border: '1px solid var(--border)', background: 'var(--card)', minHeight: 200 }}
                                    >
                                        {status === 'running' ? (
                                            <>
                                                <div className="w-6 h-6 rounded-full animate-spin mb-3" style={{ border: '2px solid var(--border-strong)', borderTopColor: 'var(--accent)' }} />
                                                <p className="text-sm" style={{ color: 'var(--text-2)' }}>Running {stepMeta.label}...</p>
                                            </>
                                        ) : status === 'error' ? (
                                            <>
                                                <p className="text-sm mb-1" style={{ color: 'var(--danger)' }}>Step failed</p>
                                                <p className="text-xs" style={{ color: 'var(--text-3)' }}>Check that your profile and LLM settings are configured</p>
                                            </>
                                        ) : (
                                            <p className="text-sm" style={{ color: 'var(--text-3)' }}>
                                                Waiting for {stepMeta.label}...
                                            </p>
                                        )}
                                    </div>
                                );
                            }

                            return (
                                <div className="rounded-lg p-5" style={{ border: '1px solid var(--border)', background: 'var(--card)' }}>
                                    <p className="text-sm font-medium mb-4" style={{ color: 'var(--text-1)' }}>{stepMeta.label}</p>
                                    <StepContent stepKey={activeStep} data={data} />
                                </div>
                            );
                        })()}
                    </div>
                </div>
            </div>

            <ConfirmationModal
                isOpen={showDeleteConfirm}
                onClose={() => setShowDeleteConfirm(false)}
                onConfirm={handleDelete}
                title="Delete Job"
                message="Are you sure you want to delete this job and all its analysis data?"
                confirmLabel="Delete"
                isDestructive={true}
            />
        </main>
    );
}
