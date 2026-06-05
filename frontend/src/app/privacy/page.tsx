'use client';

import { SUPPORT_EMAIL, SUPPORT_MAILTO } from '@/config/support';
import {
    LegalPage, H2, H3, P, UL, LI, Strong, A, Note,
    LEGAL_COMPANY, LEGAL_ENTITY, LEGAL_EFFECTIVE_DATE,
} from '@/components/LegalDoc';

export default function PrivacyPage() {
    return (
        <LegalPage
            title="Privacy Policy"
            subtitle={`This policy explains what ${LEGAL_COMPANY} collects, how we use it, who we share it with, and the choices you have. Your career documents are sensitive — we treat them that way.`}
        >
            <Note>
                <Strong>The short version.</Strong> We collect the account details and career documents you give
                us so the Service can analyze jobs and generate results. To do that, your content is sent to
                third-party AI providers. We never sell your data and never use it to train AI models. You can
                delete any file, any job, or your whole account at any time.
            </Note>

            <H2>1. Who is responsible for your data</H2>
            <P>
                {LEGAL_COMPANY}, operated by {LEGAL_ENTITY}, is the controller of the personal data described
                here. For any privacy question or request, contact{' '}
                <A href={SUPPORT_MAILTO}>{SUPPORT_EMAIL}</A>.
            </P>

            <H2>2. Information we collect</H2>

            <H3>Information you provide</H3>
            <UL>
                <LI><Strong>Account information.</Strong> When you sign in with Google, we receive your name, email address, and profile picture.</LI>
                <LI><Strong>Career documents.</Strong> Resumes, LinkedIn exports, portfolios, and any other files you upload, along with the structured profile we extract from them.</LI>
                <LI><Strong>Job and application data.</Strong> Job postings you add, company websites, your notes, application statuses, and the analyses, resume suggestions, cover letters, and outreach drafts generated for you.</LI>
                <LI><Strong>Communications.</Strong> Messages you send us, such as support requests.</LI>
            </UL>

            <H3>Information collected automatically</H3>
            <UL>
                <LI><Strong>Usage data.</Strong> Actions you take in the app, the tasks you run, and token/credit usage used for billing and rate limiting.</LI>
                <LI><Strong>Technical data.</Strong> Device and browser information, IP address, and log data generated when you interact with the Service.</LI>
            </UL>

            <H3>Payment information</H3>
            <P>
                Payments are processed by Stripe. We do not store your full card details. We receive limited
                billing information from Stripe, such as your subscription status, plan, and invoice history.
            </P>

            <H2>3. How we use your information</H2>
            <UL>
                <LI>To provide the Service — analyzing jobs, parsing and optimizing resumes, generating cover letters and outreach, and tracking applications.</LI>
                <LI>To create and maintain your account and unified profile.</LI>
                <LI>To process payments, manage subscriptions and credits, and enforce usage limits.</LI>
                <LI>To operate, secure, debug, and improve the Service.</LI>
                <LI>To respond to your support requests and send service-related communications.</LI>
                <LI>To comply with legal obligations and enforce our <A href="/terms">Terms of Service</A>.</LI>
            </UL>
            <P>
                Our legal bases for processing (where applicable, e.g. under GDPR) include performing our
                contract with you, your consent, our legitimate interests in operating and improving the
                Service, and compliance with legal obligations.
            </P>

            <H2>4. AI processing of your content</H2>
            <P>
                A core part of the Service sends your career documents and job data to third-party large
                language model providers — currently <Strong>Google Gemini</Strong>, <Strong>xAI</Strong>, and{' '}
                <Strong>DeepSeek</Strong> — solely to generate your analysis and results. These providers process
                your content on our behalf to return output to you.
            </P>
            <Note>
                We do not use your content to train AI models, and we do not sell it. We instruct our providers
                to process content only to deliver your results. Provider data-handling practices are governed
                by their own terms; we select providers that support this use.
            </Note>

            <H2>5. How we share information</H2>
            <P>We share personal data only as needed to run the Service:</P>
            <UL>
                <LI><Strong>AI providers</Strong> (Google Gemini, xAI, DeepSeek) — to generate your results, as described above.</LI>
                <LI><Strong>Google</Strong> — for authentication when you sign in.</LI>
                <LI><Strong>Stripe</Strong> — to process payments and manage subscriptions.</LI>
                <LI><Strong>Infrastructure providers</Strong> — hosting, database, and related services used to operate the Service.</LI>
                <LI><Strong>Legal and safety</Strong> — when required by law, to enforce our terms, or to protect the rights, safety, and security of users and the Service.</LI>
                <LI><Strong>Business transfers</Strong> — in connection with a merger, acquisition, or sale of assets, subject to this policy.</LI>
            </UL>
            <P>We do not sell your personal information or share it for cross-context behavioral advertising.</P>

            <H2>6. Data retention and deletion</H2>
            <P>
                We keep your information for as long as your account is active or as needed to provide the
                Service. You can delete individual files, jobs, and generated content from within the app, and
                you can delete your entire account from Settings. Deletion is permanent and removes the
                associated analysis and generated content.
            </P>
            <P>
                After account deletion, we may retain limited records where required for legal, tax, accounting,
                or fraud-prevention purposes (for example, invoice records held by our payment processor), and
                residual copies may persist in backups for a limited time before being overwritten.
            </P>

            <H2>7. Security</H2>
            <P>
                We use reasonable technical and organizational measures to protect your data, including
                authenticated access controls and encryption in transit. No method of transmission or storage
                is completely secure, so we cannot guarantee absolute security. Please use a secure Google
                account and notify us promptly of any suspected unauthorized access.
            </P>

            <H2>8. Cookies and local storage</H2>
            <P>
                We use cookies and browser local storage for essential functions such as keeping you signed in,
                remembering preferences (like theme), and operating the Service. We do not use third-party
                advertising cookies.
            </P>

            <H2>9. International data transfers</H2>
            <P>
                We and our service providers may process your data in countries other than where you live,
                including the United States. Where required, we rely on appropriate safeguards for such
                transfers. By using the Service, you understand your data may be processed in these locations.
            </P>

            <H2>10. Your rights and choices</H2>
            <P>
                Depending on where you live, you may have rights to access, correct, export, restrict, or delete
                your personal data, to object to certain processing, and to withdraw consent. Many of these
                actions are available directly in the app; for others, contact{' '}
                <A href={SUPPORT_MAILTO}>{SUPPORT_EMAIL}</A> and we will respond as required by applicable law.
                You will not be discriminated against for exercising your rights. If you are in the EEA/UK, you
                also have the right to lodge a complaint with your local data-protection authority.
            </P>

            <H2>11. Children&rsquo;s privacy</H2>
            <P>
                The Service is not directed to children under 18, and we do not knowingly collect personal data
                from them. If you believe a child has provided us data, contact us and we will delete it.
            </P>

            <H2>12. Changes to this policy</H2>
            <P>
                We may update this Privacy Policy from time to time. We will update the &ldquo;Last updated&rdquo;
                date above and, for material changes, provide additional notice where appropriate.
            </P>

            <H2>13. Contact</H2>
            <P>
                Questions or requests about your privacy? Email us at{' '}
                <A href={SUPPORT_MAILTO}>{SUPPORT_EMAIL}</A>. This policy is effective as of {LEGAL_EFFECTIVE_DATE}.
            </P>
        </LegalPage>
    );
}
