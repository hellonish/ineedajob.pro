'use client';

import Header from '@/components/Header';
import { SUPPORT_EMAIL, SUPPORT_MAILTO } from '@/config/support';

const PHONE = '+91 817 818 3818';
const PHONE_HREF = 'tel:+918178183818';

export default function ContactPage() {
    return (
        <main style={{ minHeight: '100vh' }}>
            <Header />

            <div style={{ maxWidth: 560, margin: '0 auto', padding: '56px 24px 120px' }}>

                {/* Header */}
                <div style={{ marginBottom: 40 }}>
                    <div style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: 11, fontWeight: 500,
                        letterSpacing: '0.08em', textTransform: 'uppercase',
                        color: 'var(--text-3)', marginBottom: 12,
                    }}>
                        Support
                    </div>
                    <h1 style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: 'calc(var(--display-scale, 0.92) * 40px)',
                        fontWeight: 500, letterSpacing: '-0.02em',
                        color: 'var(--text)', lineHeight: 1.1, margin: 0,
                    }}>
                        Contact us
                    </h1>
                    <p style={{ marginTop: 12, fontSize: 15, color: 'var(--text-2)', lineHeight: 1.6 }}>
                        We&rsquo;re a small team. Email is the fastest way to reach us.
                    </p>
                </div>

                {/* Contact cards */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>

                    <ContactRow
                        icon={<EmailIcon />}
                        label="Email"
                        value={SUPPORT_EMAIL}
                        href={SUPPORT_MAILTO}
                        note="We typically respond within one business day."
                    />

                    <ContactRow
                        icon={<PhoneIcon />}
                        label="Phone"
                        value={PHONE}
                        href={PHONE_HREF}
                    />

                    <ContactRow
                        icon={<LocationIcon />}
                        label="Operating office"
                        value={'Balbir Nagar, Shahdara\nDelhi, India — 110032'}
                    />

                </div>
            </div>
        </main>
    );
}

// ── ContactRow ────────────────────────────────────────────────────────────────

function ContactRow({
    icon,
    label,
    value,
    href,
    note,
}: {
    icon: React.ReactNode;
    label: string;
    value: string;
    href?: string;
    note?: string;
}) {
    return (
        <div style={{
            display: 'flex', gap: 16, alignItems: 'flex-start',
            padding: '20px 0',
            borderBottom: '1px solid var(--border-soft)',
        }}>
            {/* Icon */}
            <div style={{
                width: 36, height: 36, flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'var(--surface)', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-3)',
            }}>
                {icon}
            </div>

            {/* Text */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: 10.5, fontWeight: 500,
                    letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--text-3)',
                }}>
                    {label}
                </span>
                {href ? (
                    <a href={href} style={{
                        fontSize: 15, fontWeight: 500, color: 'var(--text)',
                        textDecoration: 'none',
                    }}
                        onMouseEnter={e => { e.currentTarget.style.textDecoration = 'underline'; e.currentTarget.style.textUnderlineOffset = '3px'; }}
                        onMouseLeave={e => { e.currentTarget.style.textDecoration = 'none'; }}
                    >
                        {value}
                    </a>
                ) : (
                    <span style={{ fontSize: 15, fontWeight: 500, color: 'var(--text)', whiteSpace: 'pre-line' }}>
                        {value}
                    </span>
                )}
                {note && (
                    <span style={{ fontSize: 12.5, color: 'var(--text-3)', lineHeight: 1.5 }}>
                        {note}
                    </span>
                )}
            </div>
        </div>
    );
}

// ── Icons ─────────────────────────────────────────────────────────────────────

function EmailIcon() {
    return (
        <svg width={16} height={16} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
        </svg>
    );
}

function PhoneIcon() {
    return (
        <svg width={16} height={16} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.07 12 19.79 19.79 0 0 1 1 3.18 2 2 0 0 1 2.99 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 5.99 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
        </svg>
    );
}

function LocationIcon() {
    return (
        <svg width={16} height={16} viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z" />
            <circle cx="12" cy="10" r="3" />
        </svg>
    );
}
