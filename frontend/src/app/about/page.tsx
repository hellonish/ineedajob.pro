'use client';

import React from 'react';
import Link from 'next/link';

/**
 * About page - public view explaining what iNeedaJob.pro is and why it exists.
 */

export default function AboutPage() {
    return (
        <main style={{ minHeight: '100vh' }}>
            {/* Minimal public nav */}
            <nav style={{
                position: 'sticky', top: 0, zIndex: 40,
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 24px', height: 52,
                background: 'var(--bg)', borderBottom: '1px solid var(--border-soft)',
            }}>
                <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 8, textDecoration: 'none', color: 'var(--text)' }}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src="/logo.svg" alt="iNeedaJob.pro" style={{ width: 26, height: 26, borderRadius: 'var(--radius)', display: 'block' }} />
                    <span style={{ fontFamily: 'var(--font-display)', fontSize: 14, fontWeight: 500, letterSpacing: '-0.02em' }}>iNeedaJob.pro</span>
                </Link>
                <div style={{ display: 'flex', gap: 20, alignItems: 'center' }}>
                    <Link href="/founder" style={{ fontSize: 13, color: 'var(--text-2)', textDecoration: 'none' }}>
                        Founder
                    </Link>
                    <Link href="/dashboard" style={{ fontSize: 13, color: 'var(--text-2)', textDecoration: 'none' }}>
                        Back to app →
                    </Link>
                </div>
            </nav>

            <article
                style={{
                    maxWidth: 820,
                    margin: '0 auto',
                    padding: '56px 24px 120px',
                    color: 'var(--text-2)',
                    fontSize: 15,
                    lineHeight: 1.7,
                }}
            >
                {/* Hero section */}
                <header style={{ marginBottom: 48 }}>
                    <div
                        style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: 11,
                            fontWeight: 500,
                            letterSpacing: '0.08em',
                            textTransform: 'uppercase',
                            color: 'var(--text-3)',
                            marginBottom: 12,
                        }}
                    >
                        About
                    </div>
                    <h1
                        style={{
                            fontFamily: 'var(--font-display)',
                            fontSize: 'calc(var(--display-scale, 0.92) * 48px)',
                            fontWeight: 500,
                            letterSpacing: '-0.02em',
                            color: 'var(--text)',
                            lineHeight: 1.1,
                            margin: 0,
                        }}
                    >
                        Know your fit before you apply
                    </h1>
                    <p style={{ marginTop: 16, fontSize: 17, color: 'var(--text-2)', lineHeight: 1.6, maxWidth: 680 }}>
                        iNeedaJob.pro is an open-source, AI-powered job application assistant. Paste a job link, upload your resume, and get a match score, gap analysis, tailored resume suggestions, a cover letter, and a list of people to reach out to — all in one run.
                    </p>
                </header>

                {/* The Problem */}
                <Section>
                    <H2>The Problem</H2>
                    <P>
                        Job hunting is broken. You spend hours tailoring resumes, writing cover letters, and researching companies — only to hear nothing back. Most rejections happen because your application doesn't clearly match what the job description asks for, not because you're unqualified.
                    </P>
                    <P>
                        The worst part? You don't know where you stand until it's too late. Was it the missing keyword? The gap in your experience? The lack of a warm intro? You're flying blind.
                    </P>
                </Section>

                {/* The Solution */}
                <Section>
                    <H2>The Solution</H2>
                    <P>
                        iNeedaJob.pro gives you <strong style={{ color: 'var(--text)', fontWeight: 600 }}>instant career intelligence</strong> before you hit submit. Here's what happens when you add a job:
                    </P>
                    <FeatureList>
                        <Feature
                            title="Job Analysis"
                            description="Extracts requirements, skills, responsibilities, and salary signals from any job posting — even if the description is vague or poorly written."
                        />
                        <Feature
                            title="Match Score"
                            description="Scores your profile against the job and explains exactly what you're missing. No guessing, no generic advice."
                        />
                        <Feature
                            title="Resume Actions"
                            description="Specific Add / Update / Remove suggestions to close the gaps. Each action is tied to a requirement from the job description."
                        />
                        <Feature
                            title="Cover Letter Generation"
                            description="Professional, Creative, or Storytelling tone modes. Each one is tailored to the job and your background — not generic AI slop."
                        />
                        <Feature
                            title="Company Intelligence"
                            description="Summarizes the company from public sources before you apply, so you understand the context and culture."
                        />
                        <Feature
                            title="Reachout Discovery"
                            description="Finds LinkedIn contacts at the target company to cold-message. A warm intro beats a cold application every time."
                        />
                    </FeatureList>
                </Section>

                {/* How It Works */}
                <Section>
                    <H2>How It Works</H2>
                    <P>
                        You bring your own AI provider API key (Anthropic, OpenAI, Google Gemini, xAI, or DeepSeek). Your resume and job data are sent to your chosen provider to generate the analysis — we never use your data to train models, and we never sell it.
                    </P>
                    <P>
                        The whole pipeline runs client-side where possible and server-side only when needed for structured extraction. Results stream back in real-time via WebSockets so you can watch the analysis unfold.
                    </P>
                    <P>
                        Everything is stored in your private workspace. You can edit, delete, or export at any time. The application tracking board lets you manage your pipeline from "Need to Apply" to "Offer."
                    </P>
                </Section>

                {/* Open Source */}
                <Section>
                    <H2>Open Source</H2>
                    <P>
                        iNeedaJob.pro is <strong style={{ color: 'var(--text)', fontWeight: 600 }}>fully open source</strong> under MIT + Commons Clause. That means:
                    </P>
                    <ul style={{ margin: '16px 0', paddingLeft: 22, display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <li style={{ paddingLeft: 4 }}>You can self-host it for free — no login required on the <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9em', background: 'var(--surface-2)', padding: '2px 6px', borderRadius: 4 }}>main</code> branch.</li>
                        <li style={{ paddingLeft: 4 }}>You can inspect every line of code, modify it, and contribute back.</li>
                        <li style={{ paddingLeft: 4 }}>You can't sell it as a hosted service or build a commercial product whose value derives substantially from its functionality.</li>
                    </ul>
                    <P>
                        The hosted version at <a href="https://ineedajob.pro" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>ineedajob.pro</a> is free to use. Sign in with Google, add your API key, and start analyzing jobs.
                    </P>
                </Section>

                {/* Who It's For */}
                <Section>
                    <H2>Who It's For</H2>
                    <P>
                        This tool is built for people who want to apply smarter, not harder. If you're:
                    </P>
                    <ul style={{ margin: '16px 0', paddingLeft: 22, display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <li style={{ paddingLeft: 4 }}>Tired of tailoring resumes manually and not knowing if it made a difference.</li>
                        <li style={{ paddingLeft: 4 }}>Looking for honest feedback about where you stand before you apply.</li>
                        <li style={{ paddingLeft: 4 }}>Trying to break into a new field and need to understand the gaps in your profile.</li>
                        <li style={{ paddingLeft: 4 }}>Managing multiple applications and want a single place to track everything.</li>
                    </ul>
                    <P>
                        ...then this is for you.
                    </P>
                </Section>

                {/* Why I Built This */}
                <Section>
                    <H2>Why I Built This</H2>
                    <P>
                        I built iNeedaJob.pro because I was frustrated by the disconnect between effort and results in job hunting. You can spend hours on an application and still get ghosted — not because you're unqualified, but because your resume didn't match the keyword scan or you didn't highlight the right experience.
                    </P>
                    <P>
                        AI is good at structured analysis, and it's getting better every month. Why not use it to give yourself an edge? Not to replace your judgment, but to show you what the ATS and recruiter will see before you hit submit.
                    </P>
                    <P>
                        This tool exists to close the information gap. It won't get you a job on its own, but it will help you apply with confidence and clarity.
                    </P>
                </Section>

                {/* Footer CTA */}
                <div style={{
                    marginTop: 56,
                    paddingTop: 24,
                    borderTop: '1px solid var(--border-soft)',
                }}>
                    <P>
                        Ready to get started?{' '}
                        <Link href="/dashboard" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            Go to the dashboard
                        </Link>{' '}
                        or{' '}
                        <Link href="/founder" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            learn more about the founder
                        </Link>.
                    </P>
                </div>
            </article>
        </main>
    );
}

// ── Layout components ───────────────────────────────────────────────────────

function Section({ children }: { children: React.ReactNode }) {
    return <section style={{ marginBottom: 40 }}>{children}</section>;
}

function H2({ children }: { children: React.ReactNode }) {
    return (
        <h2
            style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'calc(var(--display-scale, 0.92) * 28px)',
                fontWeight: 500,
                letterSpacing: '-0.01em',
                color: 'var(--text)',
                margin: '0 0 16px',
                lineHeight: 1.2,
            }}
        >
            {children}
        </h2>
    );
}

function P({ children }: { children: React.ReactNode }) {
    return <p style={{ margin: '0 0 16px' }}>{children}</p>;
}

function FeatureList({ children }: { children: React.ReactNode }) {
    return (
        <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: 20,
            margin: '24px 0',
        }}>
            {children}
        </div>
    );
}

function Feature({ title, description }: { title: string; description: string }) {
    return (
        <div style={{
            padding: 16,
            background: 'var(--surface-2, var(--surface))',
            border: '1px solid var(--border-soft, var(--border))',
            borderRadius: 'var(--radius, 10px)',
        }}>
            <div style={{
                fontSize: 15,
                fontWeight: 600,
                color: 'var(--text)',
                marginBottom: 6,
            }}>
                {title}
            </div>
            <div style={{
                fontSize: 14,
                color: 'var(--text-2)',
                lineHeight: 1.5,
            }}>
                {description}
            </div>
        </div>
    );
}
