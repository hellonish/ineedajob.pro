'use client';

import { SUPPORT_EMAIL, SUPPORT_MAILTO } from '@/config/support';
import {
    LegalPage, H2, P, UL, LI, Strong, A, Note,
    LEGAL_COMPANY, LEGAL_EFFECTIVE_DATE,
} from '@/components/LegalDoc';

export default function RefundsPage() {
    return (
        <LegalPage
            title="Refund Policy"
            subtitle={`How billing, cancellations, and refunds work at ${LEGAL_COMPANY}. We want billing to feel fair — here's exactly what to expect.`}
        >
            <Note>
                <Strong>In short.</Strong> There&rsquo;s a free tier so you can try {LEGAL_COMPANY} before
                paying. Subscriptions are billed in advance and are generally non-refundable, but you can cancel
                anytime and keep access until the end of the period you&rsquo;ve paid for. If something went
                wrong with a charge, email us — we&rsquo;ll make it right.
            </Note>

            <H2>1. Try before you buy</H2>
            <P>
                {LEGAL_COMPANY} offers a free plan with enough capacity to evaluate the Service before
                purchasing. Because you can assess the Service at no cost, paid plans are sold on the
                understanding described below.
            </P>

            <H2>2. Subscriptions</H2>
            <P>
                Paid plans (Starter, Pro, and Max) are billed in advance on a recurring monthly basis through
                Stripe. Except where required by law or expressly stated here, subscription payments are{' '}
                <Strong>non-refundable</Strong>, including for partial billing periods and for unused monthly
                capacity.
            </P>
            <UL>
                <LI><Strong>Cancellation.</Strong> You can cancel anytime from the billing section or the Stripe customer portal. Cancellation stops future renewals — it does not generate a refund for the current period. You keep access to paid features until the end of the period you&rsquo;ve already paid for.</LI>
                <LI><Strong>Downgrades.</Strong> Downgrades take effect at your next billing period. You keep your current plan&rsquo;s limits until then; no partial refund is issued for the difference.</LI>
                <LI><Strong>Upgrades.</Strong> Upgrades take effect immediately and are charged a prorated amount for the rest of the current period. That prorated charge is non-refundable.</LI>
            </UL>

            <H2>3. Usage top-ups</H2>
            <P>
                One-time top-up credits are <Strong>non-refundable</Strong> once purchased. Because top-up
                credits never expire and are available for immediate use as soon as they&rsquo;re added to your
                account, we cannot refund them, including any unused balance.
            </P>

            <H2>4. When we will issue a refund</H2>
            <P>We will review and, where appropriate, issue a refund in cases such as:</P>
            <UL>
                <LI><Strong>Duplicate or accidental charges</Strong> — for example, being billed twice for the same period.</LI>
                <LI><Strong>Billing errors</Strong> — a charge that does not match the plan or price you selected.</LI>
                <LI><Strong>Failure of the Service</Strong> — a sustained, verifiable outage that prevented you from using paid features, where we were unable to resolve it.</LI>
                <LI><Strong>Where required by law</Strong> — including any non-waivable statutory rights that apply to you.</LI>
            </UL>

            <H2>5. Discretionary refunds</H2>
            <P>
                Outside the cases above, refunds are granted at our discretion. If you&rsquo;re unhappy with the
                Service, contact us — we&rsquo;ll do our best to find a fair resolution, which may include a
                credit or a partial or full refund depending on the circumstances.
            </P>

            <H2>6. How to request a refund</H2>
            <P>
                Email <A href={SUPPORT_MAILTO}>{SUPPORT_EMAIL}</A> from the email address on your account within
                30 days of the charge. Please include the date and amount of the charge and a brief description
                of the issue. We aim to respond within a few business days. Approved refunds are returned to
                your original payment method via Stripe and may take several business days to appear, depending
                on your bank or card issuer.
            </P>

            <H2>7. Statutory rights (EU / UK and others)</H2>
            <P>
                Nothing in this policy limits any non-waivable rights you have under the consumer-protection laws
                of your country. If you are a consumer in the EEA or UK, you may have a statutory right to
                withdraw from a purchase within 14 days. However, because the Service is digital content and AI
                processing delivered immediately, by purchasing and using paid features you request immediate
                performance and acknowledge that you lose this right of withdrawal once the digital content or
                processing has begun.
            </P>

            <H2>8. Chargebacks</H2>
            <P>
                If you believe a charge is incorrect, please contact us first so we can resolve it quickly.
                Initiating a chargeback or payment dispute without contacting us may result in suspension of
                your account while the dispute is investigated.
            </P>

            <H2>9. Changes to this policy</H2>
            <P>
                We may update this Refund Policy from time to time. We&rsquo;ll update the &ldquo;Last
                updated&rdquo; date above; changes apply to purchases made after the change takes effect.
            </P>

            <H2>10. Contact</H2>
            <P>
                Questions about billing or refunds? Email{' '}
                <A href={SUPPORT_MAILTO}>{SUPPORT_EMAIL}</A>. This policy is effective as of {LEGAL_EFFECTIVE_DATE} and
                should be read together with our <A href="/terms">Terms of Service</A>.
            </P>
        </LegalPage>
    );
}
