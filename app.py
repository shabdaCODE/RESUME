import streamlit as st
import requests
import json
import re
import subprocess
import os
import tempfile
import random

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://streamlit.io",
    "X-Title": "Resume Generator"
}
# Verified working free models on OpenRouter — tries each in order
MODELS = [
    "deepseek/deepseek-r1:free",          # confirmed free long-term
    "deepseek/deepseek-chat:free",         # confirmed free long-term  
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "openrouter/free",                     # auto-picks any available free model — never 404s
]

# ══════════════════════════════════════════════════════════════════════════════
# CANDIDATE PROFILE — ANURAG LOKHANDE (permanent, accurate)
# ══════════════════════════════════════════════════════════════════════════════
ANURAG = {
    "name": "ANURAG LOKHANDE",
    "phone": "+91-770-927-1496",
    "email": "lokhandeag21.elec@coeptech.ac.in",
    "linkedin": "linkedin.com/in/anurag-lokhande-180a5a230",
    "github": "github.com/anuraglokhande",
    "education": {
        "degree": "B.Tech in Electrical Engineering",
        "university": "COEP Technological University, Pune",
        "years": "2021 – 2025",
        "coursework": "Data Structures & Algorithms, OOP, DBMS, Operating Systems, Computer Networks, Engineering Mathematics, Statistics & Probability"
    },
    "experience": [
        {
            "title": "Account Executive – Performance Marketing (Account Management)",
            "company": "BeyondWalls – PropTech platform powered by Majesco",
            "duration": "09/2025 – Present",
            "location": "Pune, On-Site",
            "raw": """BeyondWalls is a cutting-edge PropTech platform revolutionizing the home-buying journey
            via a tech-driven ecosystem bridging real estate developers and channel partners (brokers).
            Responsibilities:
            - Preparing marketing and sales strategies for clients with end-to-end execution
            - Technology implementation of in-house CRMs and continuous monitoring
            - Conducting thorough secondary research on client competition to develop communication and media plans
            - Taking detailed client briefs (objectives, budgets, plans) via meetings, calls, and email
            - Preparing MOM of every client meeting and call
            - Timeline management ensuring work-plans, campaigns, reports delivered on time
            - Ensuring 100% error-free campaign execution and live campaign optimization on a daily basis
            - Monitoring in-house CRMs, managing website, handling digital platforms
            - Keeping updated on client industry trends to suggest personalized solutions
            Key achievements: Tracked 20+ KPIs monthly, managed 5+ concurrent client accounts,
            ensured 100% on-time delivery, collaborated with cross-functional teams across tech and product."""
        },
        {
            "title": ".NET Developer Intern – Assets Team",
            "company": "Baker Hughes",
            "duration": "01/2025 – 07/2025",
            "raw": """Engineering and Technology Intern on the Assets Team focused on backend .NET development.
            - Architected C#/.NET Core backend services and optimized PostgreSQL database schemas
            - Designed and consumed RESTful APIs ensuring seamless data integration and process automation for test validation
            - Modularized large SQL migration scripts and implemented automated data migration flows
              supporting structured backend data integrity for test environments
            - Refactored a 592-line .cs file creating reusable methods, debugging with Postman,
              and deploying an optimized backend solution — reduced code complexity by 40%
            - Redesigned LogQuery extension to extend IDbCommand, updated Npgsql usage,
              and aligned supporting files for consistent logging aiding test analysis
            - Improved PostgreSQL query performance by 40% through indexing and query optimization
            - Collaborated across cross-functional teams, adapted quickly to evolving requirements,
              and shipped 3 production-ready backend features on schedule
            - Used Git for version control, followed CI/CD practices, documented all system changes"""
        },
        {
            "title": "Research Intern – Rail Infrastructure & Data Analytics",
            "company": "Pune Metro Rail Corporation",
            "duration": "06/2024 – 07/2024",
            "raw": """Research internship focused on Pune city metro rail infrastructure performance optimization.
            - Analyzed real-time system data to evaluate performance impacts and identify efficiency opportunities
            - Investigated system performance strategies leveraging data analytics to boost operational efficiency
            - Built Power BI dashboards monitoring 10+ KPIs across 5 operational stations
            - Collaborated with cross-functional teams to implement data-driven optimizations
              enhancing overall system quality, performance, and compliance
            - Identified 3 key inefficiencies in power consumption patterns
            - Reduced manual data processing effort by 60% through Python-based automation
            - Documented analytical findings and presented structured insights to senior stakeholders"""
        }
    ],
    "projects": [
        {
            "name": "Data Migration & SQL Optimization System",
            "duration": "01/2025 – 04/2025",
            "raw": """Designed modular data migration framework using C# and Python applying OOP/SOLID principles.
            Optimized complex SQL queries and indexing strategies reducing execution time by 30%.
            Implemented automated validation checks ensuring fault-tolerant data movement with 100% accuracy.
            Built reusable components adopted by 2 additional teams. Modularized 592-line legacy scripts."""
        },
        {
            "name": "Credit Card Fraud Detection System",
            "duration": "11/2024 – 12/2024",
            "raw": """End-to-end fraud detection pipeline in Python achieving 92% precision on test data.
            Applied classification algorithms on imbalanced datasets. Evaluated using ROC-AUC and Precision-Recall metrics.
            Processed 100K+ transaction records using optimized data structures.
            Clear separation of concerns via OOP. Visualized outputs for debugging and model evaluation."""
        },
        {
            "name": "Customer Churn Prediction – Binary Classification",
            "raw": """Binary classification models using Logistic Regression, Decision Trees, Random Forest.
            Feature engineering and outlier handling on 50K+ customer records.
            Achieved ROC-AUC 88%. Recommended retention strategies reducing predicted churn by 18%.
            Used Python (Pandas, NumPy, Scikit-learn) for full pipeline."""
        },
        {
            "name": "Backend Application Development (.NET)",
            "raw": """Backend modules using C#/.NET Core following enterprise coding standards.
            Designed and implemented REST API endpoints with proper error handling.
            CRUD operations with PostgreSQL. Unit testing achieving 95% test coverage.
            Debugging with Postman, documented all API specifications."""
        },
        {
            "name": "CRM Workflow Automation",
            "raw": """Automated CRM platform workflows reducing manual intervention by 40%.
            Built monitoring logic and reporting dashboards for business-critical operations.
            Collaborated with stakeholders to translate requirements into platform configurations.
            Ensured 100% error-free execution of automated campaign flows."""
        }
    ],
    "skills": {
        "languages": ["C#", "Python", "SQL", "Java", "C++", "Shell/Bash", "JavaScript (basic)"],
        "frameworks_and_tools": [".NET Core", ".NET Framework", "RESTful APIs", "Postman", "Pandas", "NumPy", "Scikit-learn", "Flask (basic)"],
        "databases": ["PostgreSQL", "MySQL", "SQL Server", "MongoDB (basic)", "Npgsql"],
        "devops_and_tools": ["Git", "GitHub", "CI/CD (basic)", "Docker (basic)", "Linux", "Power BI", "Excel"],
        "cloud": ["AWS (foundational)", "Azure (foundational)"],
        "cs_fundamentals": ["Data Structures", "Algorithms", "OOP", "SOLID Principles", "Design Patterns", "DBMS", "Complexity Analysis"],
        "soft_skills": ["Stakeholder Communication", "Cross-Functional Collaboration", "Attention to Detail",
                        "Problem Solving", "Ownership", "Accountability", "Continuous Improvement", "Documentation"]
    },
    "leadership": [
        {
            "title": "Production & Backstage Head",
            "org": "COEP Drama and Films Club",
            "duration": "04/2023 – 05/2025",
            "raw": "Led cross-functional teams of 20+ members. Managed end-to-end production operations across 5+ events under tight deadlines."
        },
        {
            "title": "Operations & Logistics Coordinator",
            "org": "Pune Startup Fest",
            "duration": "10/2022 – 03/2023",
            "raw": "Coordinated logistics and communication for a 500+ attendee large-scale technical event. Managed vendors, scheduling, and on-ground execution."
        }
    ],
    "amazon_shortlist_notes": {
        "note": "The following structure and phrases got Anurag shortlisted at Amazon for 2 rounds. Use as gold standard.",
        "summary_formula": "Graduate with strong foundations in [CS fundamentals] + hands-on experience [technical work] + demonstrated ownership across SDLC + seeking [role] at [company] to [customer/business impact]",
        "proven_phrases": [
            "fault-tolerant systems that directly impact customers at scale",
            "modular, object-oriented components improving maintainability and performance",
            "data consistency, validation, and failure handling",
            "Authored technical documentation covering system design, data flows, and operational processes",
            "reusable components to support scalability and future system extensions",
            "clear separation of concerns via OOP",
            "demonstrated ownership across the software development lifecycle",
            "Complexity Analysis",
            "directly impact customers at scale"
        ]
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# LATEX PREAMBLE + SUFFIX
# ══════════════════════════════════════════════════════════════════════════════
LATEX_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}
\usepackage{parskip}
\usepackage{xcolor}
\usepackage[scale=0.92, top=0.65cm, bottom=0.65cm]{geometry}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{array}
\newcolumntype{C}{>{\centering\arraybackslash}X}
\definecolor{linkcolour}{rgb}{0,0.2,0.6}
\hypersetup{colorlinks=true, urlcolor=linkcolour}
\titleformat{\section}{\Large\scshape\raggedright}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{3pt}{3pt}
\newenvironment{joblong}[2]{
\begin{tabularx}{\linewidth}{@{}l X r@{}}
\textbf{#1} & & #2 \\[1pt]
\end{tabularx}
\begin{itemize}[leftmargin=1em, itemsep=1pt, topsep=1pt, label=--]
}{\end{itemize}}
\begin{document}
\pagestyle{empty}
"""
LATEX_SUFFIX = r"\end{document}"

# ══════════════════════════════════════════════════════════════════════════════
# LLM CALL WITH FALLBACK CHAIN
# ══════════════════════════════════════════════════════════════════════════════
def call_llm(prompt: str, max_tokens: int = 2500) -> str:
    import time
    last_error = "No model responded"
    for model in MODELS:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": max_tokens
            }
            r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=90)
            if r.status_code == 200:
                data = r.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content")
                if text and text.strip():
                    return text.strip()
                last_error = f"{model}: empty response"
                continue
            elif r.status_code == 429:
                time.sleep(3)
                last_error = f"{model}: rate limited, skipping"
            else:
                last_error = f"{model}: {r.status_code} - {r.text[:150]}"
        except Exception as e:
            last_error = f"{model}: {str(e)}"
    return f"ERROR: {last_error}"

# ══════════════════════════════════════════════════════════════════════════════
# JOB INSIGHTS PROMPT
# ══════════════════════════════════════════════════════════════════════════════
def build_insights_prompt(jd: str) -> str:
    return f"""You are a Technical Recruiter. Analyze this Job Description and extract key information.

Job Description:
{jd}

Return ONLY valid JSON, no explanation, no markdown fences, no extra text:
{{
  "role": "exact job title from JD",
  "company": "company name or Unknown",
  "location": "city/remote/hybrid or Not specified",
  "ctc": "salary or CTC range or Not specified",
  "experience_required": "years required or Not specified",
  "employment_type": "Full-time/Part-time/Contract or Not specified",
  "key_skills": ["top 8 required hard skills from JD"],
  "nice_to_have": ["up to 4 optional or preferred skills"],
  "role_summary": "2-line summary of what this role does day-to-day"
}}"""

# ══════════════════════════════════════════════════════════════════════════════
# RESUME GENERATION PROMPT
# ══════════════════════════════════════════════════════════════════════════════
def build_resume_prompt(jd: str) -> str:
    profile_str = json.dumps(ANURAG, indent=2)
    return f"""You are an expert Technical Recruiter and ATS Optimization Specialist.

GOAL: Rewrite Anurag's resume to MAXIMIZE ATS keyword match score for this specific Job Description.

CANDIDATE PROFILE:
{profile_str}

JOB DESCRIPTION:
{jd}

═══ MANDATORY RULES — ALL MUST BE FOLLOWED ═══

━━ CONTACT & HEADER ━━
- Phone "+91-770-927-1496" MUST appear as plain readable text (not just inside href)
- Email "lokhandeag21.elec@coeptech.ac.in" MUST appear as plain readable text
- Extract the EXACT job title from the JD and add it as an italic subtitle line under the name
- This dramatically improves ATS title matching

━━ KEYWORD INJECTION ━━
- Extract EVERY technical skill, tool, framework, soft skill, and industry term from the JD
- Each JD keyword MUST appear at least once in the resume, woven in naturally
- Hard skills to always inject if in JD: documentation, engineering, programming, technology,
  product, software, coding, algorithms, computer science, automation, design, SaaS,
  continuous improvement, knowledge sharing, specifications, industry trends, emerging technologies
- Soft skills — use EXACT phrases: "communication skills", "collaborate", "collaboratively",
  "adapt", "attention to detail", "impact" — never use "detail-oriented" (blacklisted)
- Summary must contain top 6 JD keywords + role title + soft skill phrases
- Skills section must mirror JD keywords exactly — list verbatim

━━ MEASURABLE RESULTS — MINIMUM 6 ACROSS RESUME ━━
Use real numbers from profile: 30%, 40%, 50K+ records, 100% accuracy, 3 features,
20+ KPIs, 60% effort reduction, 5 stations, 500+ attendees, 20+ members,
592-line refactor, 95% test coverage, 92% precision, 88% ROC-AUC, 18% churn reduction
Add more plausible metrics where needed to reach minimum 6

━━ WORD COUNT ━━
Minimum 1000 words total — write rich, full bullet points, not terse fragments

━━ DATE FORMAT ━━
ALL dates in MM/YYYY format: e.g. "01/2025 – 07/2025", "06/2024 – 07/2024"

━━ ACTION VERBS ━━
Start EVERY bullet with a strong verb: Engineered, Architected, Delivered, Collaborated,
Optimized, Automated, Designed, Implemented, Spearheaded, Streamlined, Refactored,
Reduced, Increased, Drove, Developed, Adapted — zero passive voice

━━ ONE PAGE A4 ━━
Max 5 bullets per job, max 3 bullets per project — pick 2 most relevant projects for this JD

━━ FOUNDATIONAL SKILLS ━━
If JD requires a skill Anurag has basic knowledge of, include with qualifier:
"Docker (foundational)", "Kubernetes (basic)", "AWS (foundational)"

━━ AMAZON GOLD STANDARD ━━
This structure + these phrases got Anurag shortlisted at Amazon for 2 rounds.
Use them wherever relevant:
- "fault-tolerant systems" / "fault-tolerant data movement"
- "modular, object-oriented components improving maintainability and performance"
- "data consistency, validation, and failure handling"
- "reusable components to support scalability and future system extensions"
- "demonstrated ownership across the software development lifecycle"
- "clear separation of concerns via OOP"
- "directly impact customers at scale" (for product/customer-facing roles)
- Summary: 4 lines ending with company-specific ambition sentence

━━ SECTION ORDER ━━
Header → Professional Summary → Work Experience → Projects →
Education (with Relevant Coursework line) → Technical Skills →
Leadership & Activities (include for tech/big-company roles)

━━ LATEX OUTPUT RULES ━━
- Output LaTeX BODY CODE ONLY — no preamble, no \begin{{document}}, no markdown, no backticks
- Pre-defined environments to use:
  \section{{Title}}
  \begin{{joblong}}{{Title --- Company}}{{MM/YYYY – MM/YYYY}} ... \end{{joblong}}
  Skills: \begin{{tabularx}}{{\linewidth}}{{@{{}}l X@{{}}}} \textbf{{Label:}} & value \\\\ \end{{tabularx}}

━━ HEADER — COPY THIS EXACTLY ━━
\begin{{tabularx}}{{\linewidth}}{{@{{}} C @{{}}}}
{{\Huge \textbf{{ANURAG LOKHANDE}}}} \\\\[2pt]
\textit{{[EXACT JOB TITLE FROM JD]}} \\\\[3pt]
+91-770-927-1496 \quad | \quad lokhandeag21.elec@coeptech.ac.in \quad | \quad
\href{{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}}{{linkedin.com/in/anurag-lokhande}} \quad | \quad
\href{{https://github.com/anuraglokhande}}{{github.com/anuraglokhande}}
\end{{tabularx}}

OUTPUT: Pure LaTeX body only. No markdown. No backticks. No explanation."""

# ══════════════════════════════════════════════════════════════════════════════
# PDF COMPILER — local → latexonline.cc → ytotech
# ══════════════════════════════════════════════════════════════════════════════
def compile_to_pdf(latex_body: str):
    full_latex = LATEX_PREAMBLE + "\n" + latex_body + "\n" + LATEX_SUFFIX
    check = subprocess.run(["which", "pdflatex"], capture_output=True)
    if check.returncode == 0:
        with tempfile.TemporaryDirectory() as tmpdir:
            tex = os.path.join(tmpdir, "resume.tex")
            pdf = os.path.join(tmpdir, "resume.pdf")
            with open(tex, "w", encoding="utf-8") as f:
                f.write(full_latex)
            for _ in range(2):
                res = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex],
                    capture_output=True, text=True
                )
            if os.path.exists(pdf):
                with open(pdf, "rb") as f:
                    return f.read(), None
            return None, res.stdout[-2000:]
    try:
        r = requests.post(
            "https://latexonline.cc/compile",
            files={"file": ("resume.tex", full_latex.encode("utf-8"), "text/plain")},
            timeout=90
        )
        if r.status_code == 200 and "application/pdf" in r.headers.get("content-type", ""):
            return r.content, None
        r2 = requests.post(
            "https://latex.ytotech.com/builds/sync",
            json={"compiler": "pdflatex", "resources": [{"main": True, "content": full_latex}]},
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        if r2.status_code == 201:
            return r2.content, None
        return None, f"Compile error: {r.status_code}"
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def safe_json(text: str):
    text = re.sub(r"```(json)?", "", text).strip().replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            chunk = re.sub(r",\s*}", "}", text[s:e+1])
            chunk = re.sub(r",\s*]", "]", chunk)
            try:
                return json.loads(chunk)
            except:
                return None
    return None

def clean_latex(text: str) -> str:
    return re.sub(r"```(latex)?", "", text).strip().replace("```", "").strip()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & CSS
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="AI Resume Generator", page_icon="🚀", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Mono:wght@400;700&family=Rajdhani:wght@500;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; max-width: 820px; }

.stApp {
    background: #080810;
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(120,0,255,0.08) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 85%, rgba(0,200,150,0.07) 0%, transparent 55%),
        repeating-linear-gradient(0deg, transparent, transparent 50px,
            rgba(255,255,255,0.012) 50px, rgba(255,255,255,0.012) 51px),
        repeating-linear-gradient(90deg, transparent, transparent 50px,
            rgba(255,255,255,0.012) 50px, rgba(255,255,255,0.012) 51px);
}

.big-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(2.4rem, 6vw, 4.2rem);
    line-height: 0.95; letter-spacing: 4px; text-align: center; margin-bottom: 2px;
    background: linear-gradient(120deg, #ff6b35 0%, #ffe66d 40%, #06ffa5 70%, #00aaff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: titleFlow 4s ease-in-out infinite alternate;
}
@keyframes titleFlow { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

.subtitle {
    font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #444;
    text-align: center; letter-spacing: 3px; text-transform: uppercase; margin: 4px 0 22px 0;
}
.section-head {
    font-family: 'Bebas Neue', cursive; font-size: 0.9rem; letter-spacing: 5px;
    color: #06ffa5; text-transform: uppercase; margin: 22px 0 8px 0;
    border-bottom: 1px solid #1a2a20; padding-bottom: 4px;
}
.insight-card {
    background: #0d0d18; border: 1px solid #1e1e30; border-radius: 8px;
    padding: 10px 14px; font-family: 'Rajdhani', sans-serif; margin-bottom: 4px;
}
.insight-label { font-size: 0.6rem; letter-spacing: 2px; color: #444; text-transform: uppercase; }
.insight-value { font-size: 0.98rem; color: #e0e0e0; font-weight: 600; margin-top: 2px; line-height: 1.3; }
.skill-chip {
    background: #0f2a1e; color: #06ffa5; border: 1px solid #1a4030;
    border-radius: 4px; padding: 1px 9px; margin: 2px 3px; display: inline-block; font-size: 0.72rem;
}
.nice-chip {
    background: #1a1a10; color: #ffe66d; border: 1px solid #3a3a20;
    border-radius: 4px; padding: 1px 9px; margin: 2px 3px; display: inline-block; font-size: 0.72rem;
}
.stTextArea textarea {
    background: #0d0d15 !important; border: 1px solid #252535 !important;
    border-radius: 8px !important; color: #ddd !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important;
    transition: border-color 0.3s !important; caret-color: #ff6b35;
}
.stTextArea textarea:focus {
    border-color: #ff6b35 !important;
    box-shadow: 0 0 0 1px rgba(255,107,53,0.3), 0 0 20px rgba(255,107,53,0.1) !important;
}
.stTextArea textarea::placeholder { color: #303040 !important; }
.stTextArea label { color: #555 !important; font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; }

.stButton > button {
    background: linear-gradient(135deg, #ff6b35, #ff9a5c) !important;
    color: #000 !important; font-family: 'Bebas Neue', cursive !important;
    font-size: 1.3rem !important; letter-spacing: 4px !important;
    border: none !important; border-radius: 6px !important; height: 52px !important;
    width: 100% !important; box-shadow: 0 0 20px rgba(255,107,53,0.3) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 35px rgba(255,107,53,0.55) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #06ffa5, #00d48a) !important;
    color: #000 !important; font-family: 'Bebas Neue', cursive !important;
    font-size: 1.2rem !important; letter-spacing: 3px !important;
    border: none !important; border-radius: 6px !important; height: 50px !important;
    width: 100% !important; transition: all 0.2s !important;
    box-shadow: 0 0 18px rgba(6,255,165,0.3) !important;
    animation: pulseGreen 2.5s ease-in-out infinite;
}
.stDownloadButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 0 32px rgba(6,255,165,0.6) !important; }
@keyframes pulseGreen { 0%,100% { box-shadow: 0 0 18px rgba(6,255,165,0.3); } 50% { box-shadow: 0 0 32px rgba(6,255,165,0.55); } }

.kw-score-box {
    background: #0a1a12; border: 1px solid #1a4028; border-radius: 10px;
    padding: 14px 18px; margin: 10px 0;
}
.footer-txt {
    font-family: 'Space Mono', monospace; font-size: 0.6rem; color: #222;
    text-align: center; margin-top: 50px; line-height: 2;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="big-title">AI RESUME GENERATOR</div>
<div class="subtitle">⚡ ATS-optimized &nbsp;•&nbsp; keyword-injected &nbsp;•&nbsp; Amazon-tested &nbsp;•&nbsp; one-page PDF ⚡</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-head">// Paste Job Description</div>', unsafe_allow_html=True)
jd_input = st.text_area(
    "Job Description",
    height=280,
    placeholder="Paste the full job description here...\n\nInclude everything — role title, skills, responsibilities, requirements, qualifications.\nMore detail = better keyword extraction = higher ATS match score.",
    label_visibility="collapsed"
)

generate_btn = st.button("🚀  GENERATE RESUME", use_container_width=True)

# Session state init
for k in ["latex", "pdf_bytes", "insights", "kw_count", "kw_total", "kw_missing", "show_latex"]:
    if k not in st.session_state:
        st.session_state[k] = None
if "show_latex" not in st.session_state:
    st.session_state.show_latex = False

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════════════════
SPINNERS = [
    "🔍 Scanning JD for keywords and requirements...",
    "⚡ Optimizing for ATS systems...",
    "📝 Injecting keywords with context and metrics...",
    "🎯 Maximizing keyword match score...",
    "🧠 Applying Amazon shortlist patterns...",
]

if generate_btn:
    if not jd_input.strip():
        st.warning("⚠️ Please paste a Job Description first.")
        st.stop()

    with st.spinner("🔍 Analyzing job description..."):
        insights_raw = call_llm(build_insights_prompt(jd_input), max_tokens=600)
        st.session_state.insights = safe_json(insights_raw)

    with st.spinner(random.choice(SPINNERS)):
        latex_raw = call_llm(build_resume_prompt(jd_input), max_tokens=2500)
        if latex_raw.startswith("ERROR:"):
            st.error(f"AI Error: {latex_raw}")
            st.stop()
        latex_body = clean_latex(latex_raw)
        st.session_state.latex = latex_body
        jd_words     = set(re.findall(r'\b\w{4,}\b', jd_input.lower()))
        resume_words = set(re.findall(r'\b\w{4,}\b', latex_body.lower()))
        matched      = jd_words & resume_words
        st.session_state.kw_count   = len(matched)
        st.session_state.kw_total   = len(jd_words)
        st.session_state.kw_missing = list(jd_words - resume_words)[:10]

    with st.spinner("📄 Compiling PDF... (15–20 seconds)"):
        pdf, err = compile_to_pdf(latex_body)
        st.session_state.pdf_bytes = pdf
        if err:
            st.warning(f"PDF compile note: {err}")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.insights or st.session_state.latex:

    # ── Job Analysis ─────────────────────────────────────────────────────────
    if st.session_state.insights:
        ins = st.session_state.insights
        st.markdown('<div class="section-head">// Job Analysis</div>', unsafe_allow_html=True)

        cards = [
            ("🎯 Role",       ins.get("role", "—")),
            ("🏢 Company",    ins.get("company", "—")),
            ("📍 Location",   ins.get("location", "—")),
            ("💰 CTC",        ins.get("ctc", "Not specified")),
            ("📅 Experience", ins.get("experience_required", "—")),
            ("⏱️ Type",       ins.get("employment_type", "—")),
        ]
        cols = st.columns(3)
        for idx, (label, val) in enumerate(cards):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-label">{label}</div>
                    <div class="insight-value">{val}</div>
                </div>""", unsafe_allow_html=True)

        if ins.get("role_summary"):
            st.markdown(f"""
            <div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:8px;
                        padding:10px 14px;margin:10px 0 4px 0;font-family:'Rajdhani',sans-serif;
                        font-size:0.92rem;color:#888;line-height:1.6;">
                📋 &nbsp;{ins["role_summary"]}
            </div>""", unsafe_allow_html=True)

        req  = ins.get("key_skills", [])
        nice = ins.get("nice_to_have", [])
        if req:
            req_chips  = "".join([f'<span class="skill-chip">{s}</span>' for s in req])
            nice_chips = "".join([f'<span class="nice-chip">{s}</span>' for s in nice]) if nice else ""
            st.markdown(f"""
            <div style="background:#0a1a12;border:1px solid #1a3028;border-radius:8px;
                        padding:10px 14px;margin:8px 0;font-family:'Space Mono',monospace;
                        font-size:0.72rem;line-height:2.2;">
                <span style="color:#06ffa5;font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;">
                    REQUIRED SKILLS</span><br>{req_chips}
                {"<br><span style='color:#ffe66d;font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;'>NICE TO HAVE</span><br>" + nice_chips if nice_chips else ""}
            </div>""", unsafe_allow_html=True)

    # ── Resume Output ─────────────────────────────────────────────────────────
    if st.session_state.latex:
        st.markdown('<div class="section-head">// Resume Output</div>', unsafe_allow_html=True)

        # Keyword match score
        if st.session_state.kw_count:
            total   = st.session_state.kw_total or 1
            matched = st.session_state.kw_count
            pct     = min(int(matched / total * 100), 99)
            missing = st.session_state.kw_missing or []
            missing_html = "".join([
                f'<span style="background:#1a0a0a;color:#ff6b35;border:1px solid #3a1010;'
                f'border-radius:4px;padding:1px 7px;margin:2px 3px;display:inline-block;'
                f'font-size:0.65rem;">{w}</span>' for w in missing[:8]
            ])
            st.markdown(f"""
            <div class="kw-score-box">
                <div style="font-family:'Space Mono',monospace;font-size:0.6rem;color:#3a5a4a;
                            letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">
                    KEYWORD MATCH SCORE</div>
                <div style="font-family:'Bebas Neue',cursive;font-size:2.4rem;
                            color:#06ffa5;line-height:1;">{pct}%</div>
                <div style="background:#0a1208;border-radius:4px;height:5px;margin:8px 0;">
                    <div style="background:linear-gradient(90deg,#06ffa5,#00aaff);
                                width:{pct}%;height:5px;border-radius:4px;"></div>
                </div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:#556a58;">
                    {matched} of {total} JD keywords matched &nbsp;•&nbsp;
                    Active voice &nbsp;•&nbsp; 6+ metrics &nbsp;•&nbsp; One-page A4
                </div>
                {"<div style='margin-top:8px;font-family:Space Mono,monospace;font-size:0.62rem;color:#3a3a2a;'>STILL MISSING: " + missing_html + "</div>" if missing else ""}
            </div>""", unsafe_allow_html=True)

        # Download PDF
        if st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️  DOWNLOAD RESUME — PDF",
                data=st.session_state.pdf_bytes,
                file_name="Anurag_Lokhande_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.error("❌ PDF compile failed — download the .tex file and compile on overleaf.com")

        # Always available .tex download
        full_tex = LATEX_PREAMBLE + "\n" + st.session_state.latex + "\n" + LATEX_SUFFIX
        st.download_button(
            label="⬇️  DOWNLOAD LaTeX SOURCE (.tex)",
            data=full_tex,
            file_name="Anurag_Lokhande_Resume.tex",
            mime="text/plain",
            use_container_width=True,
        )

        # View / Edit LaTeX code
        st.markdown('<div class="section-head">// LaTeX Source</div>', unsafe_allow_html=True)
        if st.button("👁  VIEW / EDIT LaTeX CODE", use_container_width=True):
            st.session_state.show_latex = not st.session_state.show_latex

        if st.session_state.show_latex:
            edited = st.text_area(
                "LaTeX Code",
                value=full_tex,
                height=500,
                key="latex_editor"
            )
            st.download_button(
                label="⬇️  DOWNLOAD EDITED LaTeX",
                data=edited,
                file_name="Anurag_Lokhande_Resume_edited.tex",
                mime="text/plain",
                use_container_width=True,
            )

# Footer
st.markdown("""
<div class="footer-txt">
─────────────────────────────────────────────<br>
AI-powered &nbsp;•&nbsp; ATS-optimized &nbsp;•&nbsp; One-page A4 &nbsp;•&nbsp; Amazon-tested structure<br>
COEP Electrical Engineering 2025 → Software World<br>
─────────────────────────────────────────────
</div>""", unsafe_allow_html=True)
