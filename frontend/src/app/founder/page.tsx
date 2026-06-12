'use client';

import React from 'react';
import Link from 'next/link';

/**
 * Founder page - personal story and background behind iNeedaJob.pro.
 */

export default function FounderPage() {
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
                    <Link href="/about" style={{ fontSize: 13, color: 'var(--text-2)', textDecoration: 'none' }}>
                        About
                    </Link>
                    <Link href="/dashboard" style={{ fontSize: 13, color: 'var(--text-2)', textDecoration: 'none' }}>
                        Back to app →
                    </Link>
                </div>
            </nav>

            <article
                style={{
                    maxWidth: 760,
                    margin: '0 auto',
                    padding: '56px 24px 120px',
                    color: 'var(--text-2)',
                    fontSize: 15,
                    lineHeight: 1.7,
                }}
            >
                {/* Header */}
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
                        Founder
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
                        About the Founder
                    </h1>
                </header>

                {/* Founder image and intro */}
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 32,
                    marginBottom: 48,
                }}>
                    {/* Founder image */}
                    <div style={{
                        width: '100%',
                        maxWidth: 400,
                        aspectRatio: '1 / 1',
                        margin: '0 auto',
                        borderRadius: 'var(--radius, 10px)',
                        overflow: 'hidden',
                        border: '1px solid var(--border-soft)',
                    }}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                            src="/founder.jpg"
                            alt="Founder"
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover'
                            }}
                        />
                    </div>
                </div>

                {/* Story sections */}
                <Section>
                    <H2>Hi, I'm [Your Name]</H2>
                    <P>
                        I built iNeedaJob.pro because I've been on both sides of the hiring process — as a candidate sending dozens of tailored applications into the void, and as a hiring manager reviewing hundreds of resumes that didn't quite match what we were looking for.
                    </P>
                    <P>
                        The frustration is the same on both sides: candidates don't know where they stand, and recruiters don't have time to give personalized feedback. That information gap is what this tool exists to solve.
                    </P>
                </Section>

                <Section>
                    <H2>The Backstory</H2>
                    <P>
                        I started my career in [your background — e.g., software engineering, product, design, etc.], and I've worked at [types of companies — e.g., startups, mid-sized tech companies, Fortune 500s]. Along the way, I've applied to hundreds of jobs and helped hire dozens of people.
                    </P>
                    <P>
                        One pattern kept coming up: the best candidates often didn't make it past the first screen because their resume didn't surface the right keywords or didn't frame their experience in the language the job description used. Meanwhile, less-qualified candidates who knew how to "speak recruiter" got through.
                    </P>
                    <P>
                        It wasn't about merit. It was about information asymmetry.
                    </P>
                </Section>

                <Section>
                    <H2>Why Now</H2>
                    <P>
                        AI has gotten good enough to do structured analysis at scale — and more importantly, it's accessible. You can bring your own API key for a few dollars a month and run as many analyses as you need.
                    </P>
                    <P>
                        I didn't want to build a black-box SaaS that charges per analysis or locks your data behind a paywall. I wanted a tool that you can own, inspect, modify, and self-host. Open source felt like the right way to do that.
                    </P>
                    <P>
                        The hosted version at <a href="https://ineedajob.pro" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>ineedajob.pro</a> is free to use, but if you want full control, you can clone the repo and run it yourself. No tracking, no lock-in, no surprises.
                    </P>
                </Section>

                <Section>
                    <H2>What I Believe</H2>
                    <ul style={{ margin: '16px 0', paddingLeft: 22, display: 'flex', flexDirection: 'column', gap: 10 }}>
                        <li style={{ paddingLeft: 4 }}>
                            <strong style={{ color: 'var(--text)', fontWeight: 600 }}>Job hunting should be informed, not guesswork.</strong> You should know where you stand before you apply, not after you get rejected.
                        </li>
                        <li style={{ paddingLeft: 4 }}>
                            <strong style={{ color: 'var(--text)', fontWeight: 600 }}>AI should amplify your judgment, not replace it.</strong> The tool shows you what the ATS and recruiter will see, but you decide what to do with that information.
                        </li>
                        <li style={{ paddingLeft: 4 }}>
                            <strong style={{ color: 'var(--text)', fontWeight: 600 }}>Tools should be transparent and ownable.</strong> You should be able to inspect the code, understand the logic, and modify it if you want. No black boxes.
                        </li>
                        <li style={{ paddingLeft: 4 }}>
                            <strong style={{ color: 'var(--text)', fontWeight: 600 }}>Your data is yours.</strong> We don't sell it, we don't train on it, and we don't hold it hostage. You can delete it anytime.
                        </li>
                    </ul>
                </Section>

                <Section>
                    <H2>What's Next</H2>
                    <P>
                        I'm continuing to improve iNeedaJob.pro based on feedback from people using it. Some things I'm working on:
                    </P>
                    <ul style={{ margin: '16px 0', paddingLeft: 22, display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <li style={{ paddingLeft: 4 }}>Better support for non-traditional career paths (bootcamp grads, career switchers, freelancers).</li>
                        <li style={{ paddingLeft: 4 }}>More granular resume editing suggestions tied to specific job requirements.</li>
                        <li style={{ paddingLeft: 4 }}>Enhanced company intelligence with team structure and hiring patterns.</li>
                        <li style={{ paddingLeft: 4 }}>Interview prep mode that generates questions based on the job and your gaps.</li>
                    </ul>
                    <P>
                        If you have ideas or feedback, I'd love to hear from you. You can reach me at{' '}
                        <a href="mailto:hello@ineedajob.pro" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            hello@ineedajob.pro
                        </a>{' '}
                        or open an issue on{' '}
                        <a href="https://github.com/hellonish/ineedajob.pro" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            GitHub
                        </a>.
                    </P>
                </Section>

                {/* Footer CTA */}
                <div style={{
                    marginTop: 56,
                    paddingTop: 24,
                    borderTop: '1px solid var(--border-soft)',
                }}>
                    <P>
                        Want to learn more?{' '}
                        <Link href="/about" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            Read about the product
                        </Link>{' '}
                        or{' '}
                        <Link href="/dashboard" style={{ color: 'var(--accent, var(--text))', textDecoration: 'underline', textUnderlineOffset: 2 }}>
                            try it yourself
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
