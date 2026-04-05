import { Job, AnalysisResult, CoverLetter } from './api';
import { QueueItem } from './store';

/**
 * Demo data matching the actual API schemas.
 * Fully populated to satisfy strict TypeScript interfaces.
 */

const defaultAnalysis: AnalysisResult = {
    required_qualifications: [],
    preferred_qualifications: [],
    technical_skills: [],
    soft_skills: [],
    chronological_issues: [],
    resume_formatting_score: 100,
    keyword_match_score: 100,
    qualification_match_score: 100,
    skill_match_score: 100,
    final_score: 85,
    resume_suggestions: [],
    compensation_and_benefits: ["Health insurance", "401k", "Remote work"],
    salary_range: "$120,000 - $180,000",
    required_matched: 0, required_total: 0,
    preferred_matched: 0, preferred_total: 0,
    technical_matched: 0, technical_total: 0,
    soft_matched: 0, soft_total: 0
};

export const demoJobs: Job[] = [
    {
        id: "550e8400-e29b-41d4-a716-446655440001",
        job_posting: {
            job_title: "Senior Software Engineer",
            company_name: "TechCorp Inc.",
            location: "San Francisco, CA",
            required_qualifications: ["5+ years of experience", "Bachelor's in CS or related field"],
            preferred_qualifications: ["Experience with distributed systems", "Startup experience"],
            technical_skills: ["Python", "React", "TypeScript", "PostgreSQL", "Docker", "AWS"],
            soft_skills: ["Leadership", "Communication", "Problem Solving"],
            salary_range: "$150,000 - $200,000",
            compensation_and_benefits: ["Health insurance", "401k matching", "Stock options", "Remote work"],
        },
        status: "applied",
        created_at: "2026-01-15T10:30:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 85,
            required_qualifications: [
                { name: "5+ years of experience", matched: true, evidence: "7 years at various tech companies" },
                { name: "Bachelor's in CS or related field", matched: true, evidence: "B.S. Computer Science, Stanford University" }
            ],
            preferred_qualifications: [
                { name: "Experience with distributed systems", matched: true, evidence: "Built microservices at scale" },
                { name: "Startup experience", matched: false, evidence: "" }
            ],
            technical_skills: [
                { name: "Python", matched: true, evidence: "Primary language for 5 years" },
                { name: "React", matched: true, evidence: "Built multiple production apps" },
                { name: "TypeScript", matched: true, evidence: "Used in recent projects" },
                { name: "PostgreSQL", matched: true, evidence: "Database design experience" },
                { name: "Docker", matched: true, evidence: "Containerization experience" },
                { name: "AWS", matched: false, evidence: "" }
            ],
            soft_skills: [
                { name: "Leadership", matched: true, evidence: "Led team of 5 engineers" },
                { name: "Communication", matched: true, evidence: "Regular stakeholder presentations" },
                { name: "Problem Solving", matched: true, evidence: "Reduced latency by 60%" }
            ],
            resume_suggestions: [
                { action: "ADD", section: "skills", target: "AWS", suggestion: "Add AWS certifications or project experience", keyword: "AWS" }
            ],
            required_matched: 2, required_total: 2,
            preferred_matched: 1, preferred_total: 2,
            technical_matched: 5, technical_total: 6,
            soft_matched: 3, soft_total: 3
        }
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440002",
        job_posting: {
            job_title: "Full Stack Developer",
            company_name: "StartupXYZ",
            location: "Remote",
            required_qualifications: ["3+ years web development"],
            preferred_qualifications: ["GraphQL experience"],
            technical_skills: ["Node.js", "React", "MongoDB", "GraphQL"],
            soft_skills: ["Collaboration", "Adaptability"],
            salary_range: "$120,000 - $160,000",
            compensation_and_benefits: ["Unlimited PTO", "Remote first", "Learning budget"],
        },
        status: "interview",
        created_at: "2026-01-14T14:00:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 78,
            required_qualifications: [
                { name: "3+ years web development", matched: true, evidence: "5 years of web development experience" }
            ],
            preferred_qualifications: [
                { name: "GraphQL experience", matched: false, evidence: "" }
            ],
            technical_skills: [
                { name: "Node.js", matched: true, evidence: "Backend development experience" },
                { name: "React", matched: true, evidence: "Frontend framework of choice" },
                { name: "MongoDB", matched: true, evidence: "NoSQL database experience" },
                { name: "GraphQL", matched: false, evidence: "" }
            ],
            soft_skills: [
                { name: "Collaboration", matched: true, evidence: "Cross-functional team experience" },
                { name: "Adaptability", matched: true, evidence: "Worked in fast-paced environments" }
            ],
            required_matched: 1, required_total: 1,
            preferred_matched: 0, preferred_total: 1,
            technical_matched: 3, technical_total: 4,
            soft_matched: 2, soft_total: 2
        }
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440003",
        job_posting: {
            job_title: "Backend Engineer",
            company_name: "DataFlow Analytics",
            location: "New York, NY",
            required_qualifications: ["5+ years backend development", "Experience with data pipelines"],
            preferred_qualifications: ["Kafka experience", "Kubernetes experience"],
            technical_skills: ["Python", "FastAPI", "Redis", "Kafka", "Kubernetes"],
            soft_skills: ["Analytical Thinking", "Attention to Detail"],
            salary_range: "$170,000 - $220,000",
            compensation_and_benefits: ["RSUs", "Annual bonus", "Relocation package"],
        },
        status: "offer",
        created_at: "2026-01-12T09:15:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 92,
            required_qualifications: [
                { name: "5+ years backend development", matched: true, evidence: "7 years of backend engineering" },
                { name: "Experience with data pipelines", matched: true, evidence: "Built ETL pipelines processing 10M+ records" }
            ],
            preferred_qualifications: [
                { name: "Kafka experience", matched: true, evidence: "Event streaming architecture" },
                { name: "Kubernetes experience", matched: true, evidence: "Managed K8s clusters in production" }
            ],
            technical_skills: [
                { name: "Python", matched: true, evidence: "Primary language" },
                { name: "FastAPI", matched: true, evidence: "API framework of choice" },
                { name: "Redis", matched: true, evidence: "Caching layer implementation" },
                { name: "Kafka", matched: true, evidence: "Event streaming" },
                { name: "Kubernetes", matched: true, evidence: "Container orchestration" }
            ],
            soft_skills: [
                { name: "Analytical Thinking", matched: true, evidence: "Data-driven decision making" },
                { name: "Attention to Detail", matched: true, evidence: "Quality-focused engineering" }
            ],
            required_matched: 2, required_total: 2,
            preferred_matched: 2, preferred_total: 2,
            technical_matched: 5, technical_total: 5,
            soft_matched: 2, soft_total: 2
        }
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440004",
        job_posting: {
            job_title: "Frontend Developer",
            company_name: "DesignHub Creative",
            location: "Austin, TX",
            required_qualifications: ["3+ years frontend experience", "Strong portfolio"],
            preferred_qualifications: ["Animation experience"],
            technical_skills: ["Vue.js", "Tailwind CSS", "Figma"],
            soft_skills: ["Creativity", "UI/UX Sense"],
            salary_range: "$90,000 - $120,000",
            compensation_and_benefits: ["Creative environment", "Flexible hours"],
        },
        status: "rejected",
        created_at: "2026-01-10T16:45:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 65,
            required_qualifications: [
                { name: "3+ years frontend experience", matched: true, evidence: "4 years of frontend work" },
                { name: "Strong portfolio", matched: false, evidence: "" }
            ],
            technical_skills: [
                { name: "Vue.js", matched: false, evidence: "" },
                { name: "Tailwind CSS", matched: true, evidence: "Used in recent projects" },
                { name: "Figma", matched: true, evidence: "Design collaboration" }
            ],
            soft_skills: [
                { name: "Creativity", matched: true, evidence: "Creative problem solving" },
                { name: "UI/UX Sense", matched: false, evidence: "" }
            ],
            required_matched: 1, required_total: 2,
            preferred_matched: 0, preferred_total: 1,
            technical_matched: 2, technical_total: 3,
            soft_matched: 1, soft_total: 2
        }
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440005",
        job_posting: {
            job_title: "DevOps Engineer",
            company_name: "CloudScale Systems",
            location: "Seattle, WA",
            required_qualifications: ["CI/CD expertise", "Cloud infrastructure experience"],
            preferred_qualifications: ["Terraform certification"],
            technical_skills: ["Terraform", "AWS", "CI/CD", "Linux", "Python"],
            soft_skills: ["Automation Mindset", "Problem Solving"],
            salary_range: "$140,000 - $180,000",
            compensation_and_benefits: ["AWS credits", "Conference budget", "Home office stipend"],
        },
        status: "tracked",
        created_at: "2026-01-15T08:00:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 71,
            required_qualifications: [
                { name: "CI/CD expertise", matched: true, evidence: "Built CI/CD pipelines with GitHub Actions" },
                { name: "Cloud infrastructure experience", matched: true, evidence: "AWS and GCP experience" }
            ],
            preferred_qualifications: [
                { name: "Terraform certification", matched: false, evidence: "" }
            ],
            technical_skills: [
                { name: "Terraform", matched: false, evidence: "" },
                { name: "AWS", matched: true, evidence: "EC2, S3, Lambda experience" },
                { name: "CI/CD", matched: true, evidence: "GitHub Actions, Jenkins" },
                { name: "Linux", matched: true, evidence: "Linux administration" },
                { name: "Python", matched: true, evidence: "Scripting and automation" }
            ],
            soft_skills: [
                { name: "Automation Mindset", matched: true, evidence: "Automated deployment processes" },
                { name: "Problem Solving", matched: true, evidence: "Debugging production issues" }
            ],
            required_matched: 2, required_total: 2,
            preferred_matched: 0, preferred_total: 1,
            technical_matched: 4, technical_total: 5,
            soft_matched: 2, soft_total: 2
        }
    },
    {
        id: "550e8400-e29b-41d4-a716-446655440006",
        job_posting: {
            job_title: "Machine Learning Engineer",
            company_name: "AILabs Research",
            location: "Boston, MA",
            required_qualifications: ["ML/AI experience", "Strong Python skills", "Experience deploying ML models"],
            preferred_qualifications: ["PhD or research background"],
            technical_skills: ["Python", "PyTorch", "TensorFlow", "MLOps", "SQL"],
            soft_skills: ["Research Skills", "Critical Thinking"],
            salary_range: "$180,000 - $250,000",
            compensation_and_benefits: ["Research time", "Conference attendance", "Publication bonus"],
        },
        status: "applied",
        created_at: "2026-01-13T11:30:00Z",
        analysis_result: {
            ...defaultAnalysis,
            final_score: 88,
            required_qualifications: [
                { name: "ML/AI experience", matched: true, evidence: "3 years of ML development" },
                { name: "Strong Python skills", matched: true, evidence: "Advanced Python proficiency" },
                { name: "Experience deploying ML models", matched: true, evidence: "Production ML pipelines" }
            ],
            preferred_qualifications: [
                { name: "PhD or research background", matched: false, evidence: "" }
            ],
            technical_skills: [
                { name: "Python", matched: true, evidence: "Primary language" },
                { name: "PyTorch", matched: true, evidence: "Deep learning framework" },
                { name: "TensorFlow", matched: true, evidence: "Model training" },
                { name: "MLOps", matched: true, evidence: "ML infrastructure" },
                { name: "SQL", matched: true, evidence: "Data querying" }
            ],
            soft_skills: [
                { name: "Research Skills", matched: true, evidence: "Experimentation and analysis" },
                { name: "Critical Thinking", matched: true, evidence: "Problem decomposition" }
            ],
            required_matched: 3, required_total: 3,
            preferred_matched: 0, preferred_total: 1,
            technical_matched: 5, technical_total: 5,
            soft_matched: 2, soft_total: 2
        }
    }
];

export const demoQueue: QueueItem[] = [
    {
        id: "queue-001",
        jobTitle: "Software Engineer at Google",
        status: "analyzing",
        startTime: Date.now() - 45000,
    },
    {
        id: "queue-002",
        jobTitle: "Product Manager at Meta",
        status: "pending",
        startTime: Date.now() - 20000,
    },
    {
        id: "queue-003",
        jobTitle: "Data Scientist at Netflix",
        status: "pending",
        startTime: Date.now() - 10000,
    }
];

export const demoUser = {
    id: "550e8400-e29b-41d4-a716-446655440000",
    email: "demo@example.com",
    name: "Demo User",
    profile_picture: "https://ui-avatars.com/api/?name=Demo+User&background=6366f1&color=fff",
    created_at: "2026-01-01T00:00:00Z"
};

export const demoCoverLetters: CoverLetter[] = [
    {
        id: "cl-001",
        job_id: "550e8400-e29b-41d4-a716-446655440001",
        mode: "professional",
        content: {
            full_letter: `Dear Hiring Manager,

I am writing to express my strong interest in the Senior Software Engineer position at TechCorp Inc. With over 7 years of experience in distributed systems and a proven track record of building scalable microservices, I am confident in my ability to contribute effectively to your team.

My background includes extensive work with Python, React, and AWS, aligning perfectly with your technical stack. At my previous role, I led a team of 5 engineers and successfully reduced system latency by 60%, demonstrating both my technical expertise and leadership capabilities.

I am particularly excited about TechCorp Inc.'s mission and the opportunity to work on challenging problems in the fintech space. Thank you for considering my application.

Sincerely,
[Your Name]`
        },
        created_at: "2026-01-16T09:00:00Z",
        updated_at: "2026-01-16T09:00:00Z"
    },
    {
        id: "cl-002",
        job_id: "550e8400-e29b-41d4-a716-446655440003",
        mode: "conversational",
        content: {
            full_letter: `Hi Team at DataFlow Analytics,

I've been following DataFlow's work on real-time data pipelines for a while now, so when I saw the opening for a Backend Engineer, I knew I had to apply!

I've spent the last 5+ years deep in the trenches of backend development, wrestling with Kafka streams and keeping Kubernetes clusters happy. I love building systems that can handle massive scale without breaking a sweat.

Ideally, I'm looking for a team that values clean code and isn't afraid to tackle complex data challenges. It looks like you folks are doing exactly that.

I'd love to chat more about how I can help build the next generation of data tools at DataFlow.

Best,
[Your Name]`
        },
        created_at: "2026-01-15T14:30:00Z",
        updated_at: "2026-01-15T14:30:00Z"
    },
    {
        id: "cl-003",
        job_id: "550e8400-e29b-41d4-a716-446655440001",
        mode: "creative",
        content: {
            full_letter: `Hey TechCorp Team!

Imagine a world where distributed systems never fail and microservices sing in perfect harmony. That's the world I build.

I'm not just a Senior Software Engineer; I'm a digital architect with 7 years of experience turning chaotic codebases into streamlined masterpieces. I saw your opening and thought, "Finally, a place that appreciates the art of clean code."

My palette includes Python, React, and a whole lot of AWS cloud magic. I once optimized a system so well it reduced latency by 60%—it was like watching a race car shed its heavy frame mid-lap.

I'm ready to bring my unique blend of technical wizardry and creative problem-solving to TechCorp. Let's build something legendary together.

In code we trust,
[Your Name]`
        },
        created_at: "2026-01-14T10:00:00Z",
        updated_at: "2026-01-14T10:00:00Z"
    }
];
