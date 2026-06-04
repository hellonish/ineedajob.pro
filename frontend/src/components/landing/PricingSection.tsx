'use client';

import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  BRUTAL, CARD_BORDER, CARD_SHADOW, RADIUS, fontDisplay, fontBody, fontMono,
  Kicker, GoogleMark, MAXW, SECTION_PAD,
} from './brutal';

interface Tier {
  id: string;
  name: string;
  price: string;
  tagline: string;
  limits: string[];
  featured: boolean;
}

/** Same capabilities on every plan — limits only (aligned with billing PLAN_HELPER). */
function tierFeatures(limits: {
  analyses: string;
  letters: string;
  builds: string;
  processing: string;
}): string[] {
  return [
    limits.analyses,
    limits.letters,
    limits.builds,
    'Company intel',
    'Reachout contacts',
    limits.processing,
  ];
}

const TIERS: Tier[] = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    tagline: 'Start applying smarter.',
    limits: tierFeatures({
      analyses: '5 job analyses / month',
      letters: '3 cover letters / month',
      builds: '2 profile builds',
      processing: 'Priority processing',
    }),
    featured: false,
  },
  {
    id: 'starter',
    name: 'Starter',
    price: '$5.99',
    tagline: 'More volume for active seekers.',
    limits: tierFeatures({
      analyses: '15 job analyses / month',
      letters: '8 cover letters / month',
      builds: '1 profile build',
      processing: 'Priority processing',
    }),
    featured: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$14.99',
    tagline: 'Full firepower for serious candidates.',
    limits: tierFeatures({
      analyses: '35 job analyses / month',
      letters: '25 cover letters / month',
      builds: '3 profile builds',
      processing: 'Priority processing',
    }),
    featured: true,
  },
  {
    id: 'max',
    name: 'Max',
    price: '$24.99',
    tagline: 'Maximum throughput.',
    limits: tierFeatures({
      analyses: '60 job analyses / month',
      letters: '40 cover letters / month',
      builds: '5 profile builds',
      processing: 'Priority processing',
    }),
    featured: false,
  },
];

function PricingCard({
  tier,
  index,
  inView,
}: {
  tier: Tier;
  index: number;
  inView: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.4, delay: index * 0.06 }}
      style={{
        border: tier.featured ? `1.5px solid ${BRUTAL.accent}` : CARD_BORDER,
        borderRadius: RADIUS,
        background: BRUTAL.surface,
        boxShadow: tier.featured ? `0 0 0 4px ${BRUTAL.accentSoft}, ${CARD_SHADOW}` : CARD_SHADOW,
        padding: 24,
        display: 'flex',
        flexDirection: 'column',
        transform: tier.featured ? 'translateY(-6px)' : undefined,
      }}
    >
      {tier.featured && (
        <span
          style={{
            alignSelf: 'flex-start',
            fontFamily: fontMono,
            fontSize: 10,
            fontWeight: 600,
            letterSpacing: '0.08em',
            textTransform: 'uppercase',
            background: BRUTAL.accentSoft,
            color: BRUTAL.accentInk,
            border: `1px solid ${BRUTAL.accent}`,
            padding: '3px 10px',
            borderRadius: 999,
            marginBottom: 12,
          }}
        >
          Most popular
        </span>
      )}

      <div style={{ fontFamily: fontMono, fontSize: 11, fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: BRUTAL.ink3 }}>
        {tier.name}
      </div>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginTop: 8 }}>
        <span style={{ fontFamily: fontDisplay, fontSize: 36, fontWeight: 500, letterSpacing: '-0.02em', color: BRUTAL.ink }}>
          {tier.price}
        </span>
        <span style={{ fontFamily: fontBody, fontSize: 14, color: BRUTAL.ink3 }}>/ month</span>
      </div>
      <p style={{ fontFamily: fontBody, fontSize: 13, color: BRUTAL.ink2, margin: '8px 0 16px', lineHeight: 1.45 }}>{tier.tagline}</p>

      <ul style={{ listStyle: 'none', padding: 0, margin: 0, flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {tier.limits.map((label) => (
          <li key={label} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 13, color: BRUTAL.ink2 }}>
            <span style={{ color: BRUTAL.accent, fontWeight: 600, flexShrink: 0 }}>✓</span>
            {label}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

export default function PricingSection({ onGoogleLogin }: { onGoogleLogin: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '-60px' });

  return (
    <section id="pricing" style={{ background: BRUTAL.paper, padding: SECTION_PAD }}>
      <div ref={ref} style={{ maxWidth: MAXW, margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, y: 12 }} animate={inView ? { opacity: 1, y: 0 } : {}} style={{ textAlign: 'center', marginBottom: 40 }}>
          <Kicker chip style={{ marginBottom: 14 }}>I&apos;m down</Kicker>
          <h2
            style={{
              fontFamily: fontDisplay,
              fontSize: 'clamp(28px, 3.5vw, 40px)',
              fontWeight: 500,
              letterSpacing: '-0.025em',
              lineHeight: 1.15,
              color: BRUTAL.ink,
              margin: 0,
            }}
          >
            Start free. Scale when it clicks.
          </h2>
          <p style={{ fontFamily: fontBody, fontSize: 16, color: BRUTAL.ink2, maxWidth: 560, margin: '12px auto 0', lineHeight: 1.55 }}>
            Every plan includes the full product — job analysis, cover letters, company intel, reachout, and more. You only pay for higher limits.
          </p>
        </motion.div>

        <div className="pricing-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, alignItems: 'stretch' }}>
          {TIERS.map((tier, i) => (
            <PricingCard key={tier.id} tier={tier} index={i} inView={inView} />
          ))}
        </div>

        <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
          <button
            type="button"
            onClick={onGoogleLogin}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              fontFamily: fontBody,
              fontSize: 13,
              color: BRUTAL.ink3,
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              textDecoration: 'underline',
              textUnderlineOffset: 3,
              textDecorationColor: 'oklch(0.75 0.02 50)',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = BRUTAL.ink2; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = BRUTAL.ink3; }}
          >
            <GoogleMark size={16} />
            Continue with Google
          </button>
          <span style={{ fontFamily: fontBody, fontSize: 12, color: BRUTAL.ink3 }}>
            Free plan · no card required
          </span>
        </div>

        <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap', fontFamily: fontBody, fontSize: 13, color: BRUTAL.ink3 }}>
          {['Cancel anytime', 'No contracts', 'Instant access'].map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .pricing-grid { grid-template-columns: repeat(2, 1fr) !important; }
        }
        @media (max-width: 520px) {
          .pricing-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </section>
  );
}
