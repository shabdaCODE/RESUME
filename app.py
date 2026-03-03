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
    "X-Title": "Anurag Resume Generator"
}
MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-3-12b-it:free",
    "openrouter/auto",
]

# ══════════════════════════════════════════════════════════════════════════════
# ANURAG'S FULL PROFILE
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
        "coursework": "Data Structures & Algorithms, OOP, DBMS, Operating Systems, Computer Networks, Engineering Mathematics"
    },
    "experience": [
        {
            "title": "Account Executive – Performance Marketing (Account Management)",
            "company": "BeyondWalls (PropTech platform powered by Majesco)",
            "duration": "09/2025 – Present",
            "department": "Performance Marketing",
            "location": "Pune, On-Site",
            "raw": "BeyondWalls is a cutting-edge PropTech platform revolutionizing the home-buying journey via a tech-driven ecosystem bridging real estate developers and channel partners. Responsibilities: Preparing marketing and sales strategies for clients with end-to-end execution. Technology implementation of in-house CRMs and continuous monitoring. Conducting thorough secondary research to understand client competition and develop communication and media plans. Preparing MOM of every client meeting and call. Timeline management ensuring client work-plans, campaigns, and reports are shared on time. Ensuring 100% error-free campaign execution. Reviewing and optimizing live campaigns on a day-to-day basis. Managing website and handling digital platforms. Key skills demonstrated: excellent communication, relationship building, attention to detail, data-driven insights, high ownership, problem-solving, accountability, CRM monitoring, digital platform management."
        },
        {
            "title": ".NET Developer Intern – Assets Team",
            "company": "Baker Hughes",
            "duration": "01/2025 – 07/2025",
            "raw": "Engineering and Technology Intern on the Assets Team focusing on backend .NET development. Architected C#/.NET Core services and optimized PostgreSQL schemas. Designed and consumed RESTful APIs for seamless data integration and process automation crucial for test validation. Modularized large SQL migration scripts and implemented automated data migration flows supporting structured backend data integrity for test environments. Refactored a 592-line .cs file creating reusable methods, debugging with Postman, and deploying optimized backend solution. Redesigned LogQuery extension to extend IDbCommand, updated Npgsql usage, and aligned supporting files for consistent logging aiding test analysis. Collaborated across functions, embraced innovative solutions under pressure, and adapted quickly to evolving project requirements. Improved PostgreSQL query performance by 40%. Reduced codebase complexity by modularizing 592-line files into reusable components. Shipped 3 production-ready backend features on schedule."
        },
        {
            "title": "Research Intern – Rail Infrastructure & Data Analytics",
            "company": "Pune Metro Rail Corporation",
            "duration": "06/2024 – 07/2024",
            "raw": "Worked on Pune city rail metro infrastructure optimizing performance and integration for enhanced reliability. Analyzed real-time system data to evaluate performance impacts and uncover opportunities for efficiency and optimization. Investigated system performance strategies leveraging data analytics to boost operational efficiency and ensure compliance. Collaborated with cross-functional teams to implement data-driven optimizations enhancing overall system quality and performance. Built Power BI dashboards monitoring 10+ KPIs across 5 stations. Identified 3 key inefficiencies in power consumption patterns."
        }
    ],
    "projects": [
        {
            "name": "Data Migration & SQL Optimization System",
            "duration": "Jan 2025 – Apr 2025",
            "raw": "Modular data migration framework using C# and Python with OOP/SOLID principles. Optimized SQL queries and indexing reducing execution time by 30%. Automated validation checks ensuring fault-tolerant data movement. Built reusable components adopted by 2 teams."
        },
        {
            "name": "Credit Card Fraud Detection System",
            "duration": "Nov 2024 – Dec 2024",
            "raw": "End-to-end fraud detection pipeline in Python. Classification algorithms on imbalanced datasets. 92% precision on test data. ROC-AUC, Precision-Recall evaluation. Processed 100K+ transaction records with optimized data structures."
        },
        {
            "name": "Customer Churn Prediction – Binary Classification",
            "raw": "Binary classification using Logistic Regression, Decision Trees, Random Forest. Feature engineering, outlier handling on 50K+ records. ROC-AUC 88%. Recommended retention strategies reducing predicted churn by 18%."
        },
        {
            "name": "Backend Application Development (.NET)",
            "raw": "Backend modules using C#/.NET following enterprise coding standards. REST API endpoints, database interactions, CRUD operations. Unit testing and debugging with 95% test coverage."
        },
        {
            "name": "CRM Workflow Automation",
            "raw": "Automated CRM platform workflows reducing manual intervention. Monitoring logic and reporting dashboards for business-critical operations. Collaborated with stakeholders to translate requirements into platform configurations."
        }
    ],
    "skills": {
        "languages": ["Python", "C#", "SQL", "Java", "C++", "Shell/Bash"],
        "frameworks": [".NET", "Spring (basic)", "Flask (basic)", "Pandas", "NumPy", "Scikit-learn"],
        "devops": ["Git", "GitHub", "CI/CD basics", "Docker (basic)", "Linux"],
        "cloud": ["AWS (foundational)", "Azure (foundational)"],
        "databases": ["MySQL", "PostgreSQL", "SQL Server", "MongoDB (basic)"],
        "tools": ["Power BI", "Excel", "REST APIs", "Postman"],
        "cs": ["Data Structures", "Algorithms", "OOP", "SOLID Principles", "Design Patterns", "DBMS"],
        "soft": ["Stakeholder Communication", "Cross-Functional Collaboration", "Documentation", "Problem Solving", "Ownership", "Agile/Scrum"]
    },
    "leadership": [
        {
            "title": "Production & Backstage Head",
            "org": "COEP Drama and Films Club",
            "duration": "04/2023 -- 05/2025",
            "raw": "Led cross-functional teams of 20+ members. Managed end-to-end production operations under tight deadlines across 5+ events."
        },
        {
            "title": "Operations & Logistics Coordinator",
            "org": "Pune Startup Fest",
            "duration": "10/2022 -- 03/2023",
            "raw": "Coordinated logistics and communication for a large-scale 500+ attendee technical event."
        }
    ],
    "winning_resume_notes": {
        "source": "Amazon shortlisted resume — 2 rounds cleared",
        "summary_formula": "Graduate with strong foundations in [CS fundamentals] + hands-on experience in [specific skills] + demonstrated ownership across [SDLC phases] + seeking [specific role] to [customer/business impact]",
        "proven_phrases": [
            "fault-tolerant systems that directly impact customers at scale",
            "modular, object-oriented components improving maintainability and performance",
            "data consistency, validation, and failure handling",
            "Authored technical documentation covering system design, data flows, and operational processes",
            "object-oriented design principles",
            "reusable components to support scalability and future system extensions",
            "clear separation of concerns via OOP",
            "optimized data structures",
            "Complexity Analysis",
            "demonstrated ownership across the software development lifecycle"
        ],
        "structure_that_worked": "Clean header → Summary (4 lines) → Work Experience (5 bullets/job) → Projects (4 bullets each, with dates) → Education → Technical Skills (categorized) → Leadership",
        "key_insight": "No BeyondWalls in Amazon version — led with Baker Hughes as top experience. Summary ended with company-specific goal sentence. Leadership section included for big tech roles."
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# LATEX PREAMBLE
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
# API CALL WITH FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
def call_llm(prompt: str, max_tokens: int = 2500) -> str:
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
                return r.json()["choices"][0]["message"]["content"].strip()
            last_error = f"{model}: {r.status_code} – {r.text[:200]}"
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

Return ONLY valid JSON, no explanation, no markdown fences:
{{
  "role": "exact job title",
  "company": "company name or Unknown",
  "location": "city/remote/hybrid or Not specified",
  "ctc": "salary/CTC range or Not specified",
  "experience_required": "years required or Not specified",
  "employment_type": "Full-time/Part-time/Contract or Not specified",
  "key_skills": ["top 8 required skills from JD"],
  "nice_to_have": ["up to 4 optional skills"],
  "role_summary": "2-line summary of what this role does"
}}"""

# ══════════════════════════════════════════════════════════════════════════════
# RESUME GENERATION PROMPT
# ══════════════════════════════════════════════════════════════════════════════
def build_resume_prompt(jd: str) -> str:
    profile_str = json.dumps(ANURAG, indent=2)
    return f"""You are an expert Technical Recruiter and ATS Optimization Specialist.

Your ONLY goal: Rewrite Anurag's resume to MAXIMIZE its ATS match score against this Job Description.

CANDIDATE PROFILE:
{profile_str}

JOB DESCRIPTION:
{jd}

═══ CONSOLIDATED ATS RULES — ALL MANDATORY ═══

━━ CONTACT INFO (Critical — ATS must parse these as plain text) ━━
- Phone "+91-770-927-1496" MUST appear as plain readable text in the header (not only inside \\href)
- Email "lokhandeag21.elec@coeptech.ac.in" MUST appear as plain readable text in the header
- LinkedIn URL must be visible as plain text too
- Extract the exact job title from the JD and include it as a subtitle line under the name e.g. "Software Engineer | Backend Developer" — this dramatically improves ATS title matching

━━ KEYWORD INJECTION (Non-negotiable) ━━
- Read every word of the JD. Extract ALL technical skills, tools, soft skills, and industry terms.
- Every keyword found in the JD MUST appear at least once in the resume — naturally woven in.
- HARD SKILLS to always include if in JD: documentation, engineering, programming, technology, product, software, coding, algorithms, computer science, automation, design, SaaS, continuous improvement, knowledge sharing, specifications, industry trends, emerging technologies — use them naturally.
- SOFT SKILLS to always include: "communication skills", "collaborate", "collaboratively", "adapt", "attention to detail", "impact" — use these EXACT phrases (not synonyms).
- NEVER use "detail-oriented" — it is blacklisted. Use "attention to detail" instead.
- Summary paragraph must contain the top 6 JD keywords, role title, and soft skill phrases.
- Skills section must mirror JD keywords exactly — list them verbatim.

━━ MEASURABLE RESULTS (Minimum 6 across entire resume) ━━
- EVERY job must have at least 2 bullets with hard numbers/percentages/scale.
- Use real metrics from profile: 30%, 40%, 50K+ records, 100% accuracy, 3 features, 20+ KPIs, 60% effort reduction, 5+ systems, 500+ attendees, 20+ team members, 25% resolution time.
- If more metrics needed, add plausible ones: improved delivery speed by X%, reduced bugs by Y%, increased code coverage to Z%.
- Minimum 5 measurable results — aim for 6-8.

━━ WORD COUNT ━━
- Resume must contain at least 1000 words total. Write rich, full bullet points. No terse fragments.

━━ DATE FORMAT ━━
- ALL dates must follow MM/YYYY format: e.g. "01/2025 -- 07/2025", "06/2024 -- 07/2024", "2021 -- 2025"

━━ ACTION VERBS ━━
- Start EVERY bullet with a strong action verb: Engineered, Delivered, Collaborated, Optimized, Automated, Designed, Implemented, Spearheaded, Streamlined, Architected, Developed, Reduced, Increased, Drove, Created, Adapted.
- Zero passive voice anywhere.

━━ ONE PAGE A4 ━━
- Max 5 bullets per job, max 3 bullets per project. Pick 2 most relevant projects only.
- No filler sentences. Every line must add keyword or metric value.

━━ FOUNDATIONAL SKILLS ━━
- If JD requires a skill Anurag has foundational knowledge of, include it with qualifier: "Docker (foundational)", "Kubernetes (basic)", "AWS (foundational)".

━━ SECTION ORDER ━━
Header → Professional Summary → Work Experience → Projects → Education → Technical Skills → Leadership & Activities (include for tech/product roles — it shows team skills)

━━ WINNING RESUME INTEL (Amazon shortlist — 2 rounds cleared) ━━
This exact structure got Anurag shortlisted at Amazon. Use it as the gold standard:

SUMMARY FORMULA that worked:
"[Role] graduate with strong foundations in [CS fundamentals from JD]. Hands-on experience [specific technical work]. Demonstrated ownership across the software development lifecycle including design, implementation, debugging, and documentation. Seeking a [exact JD title] role at [Company] to [business/customer impact statement]."

PROVEN PHRASES — weave these in wherever relevant:
- "fault-tolerant systems" / "fault-tolerant data movement"
- "modular, object-oriented components improving maintainability and performance"
- "data consistency, validation, and failure handling"
- "Authored technical documentation covering system design, data flows, and operational processes"
- "reusable components to support scalability and future system extensions"
- "clear separation of concerns via OOP"
- "demonstrated ownership across the software development lifecycle"
- "Complexity Analysis" (in skills)
- "directly impact customers at scale" (for product/customer-facing roles)

STRUCTURE that worked:
- Summary: exactly 4 lines, ends with company-specific ambition sentence
- Experience: 5 strong bullets per job, Baker Hughes FIRST (strongest internship)
- Projects: 4 bullets each WITH dates, lead with Data Migration project
- Skills: clean categories — Programming Languages / Computer Science / Backend & Databases / Engineering Practices / Tools
- Leadership: ALWAYS include for big tech — shows teamwork and execution under pressure

━━ LATEX FORMAT RULES ━━
- Output LaTeX body code ONLY — no preamble, no \\begin{{document}}, no markdown fences, no backticks, no explanation
- Use these pre-defined environments exactly:
  \\section{{Title}}
  \\begin{{joblong}}{{Title --- Company}}{{MM/YYYY -- MM/YYYY}} ... \\end{{joblong}}
  Skills table: \\begin{{tabularx}}{{\\linewidth}}{{@{{}}l X@{{}}}} \\textbf{{Label:}} & value \\\\ \\end{{tabularx}}

━━ HEADER (copy this exactly) ━━
\\begin{{tabularx}}{{\\linewidth}}{{@{{}} C @{{}}}}
{{\\Huge \\textbf{{ANURAG LOKHANDE}}}} \\\\[2pt]
\\textit{{[INSERT TARGET JOB TITLE FROM JD HERE]}} \\\\[3pt]
+91-770-927-1496 \\quad | \\quad lokhandeag21.elec@coeptech.ac.in \\quad | \\quad
\\href{{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}}{{linkedin.com/in/anurag-lokhande-180a5a230}} \\quad | \\quad
\\href{{https://github.com/anuraglokhande}}{{github.com/anuraglokhande}}
\\end{{tabularx}}

OUTPUT: Pure LaTeX body only. No markdown. No backticks. No explanation before or after."""

# ══════════════════════════════════════════════════════════════════════════════
# PDF COMPILER
# ══════════════════════════════════════════════════════════════════════════════
def compile_to_pdf(latex_body: str):
    full_latex = LATEX_PREAMBLE + "\n" + latex_body + "\n" + LATEX_SUFFIX
    # Try local pdflatex
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

    # Fallback: latexonline.cc API
    try:
        r = requests.post(
            "https://latexonline.cc/compile",
            files={"file": ("resume.tex", full_latex.encode("utf-8"), "text/plain")},
            timeout=90
        )
        if r.status_code == 200 and "application/pdf" in r.headers.get("content-type", ""):
            return r.content, None
        # Fallback 2: ytotech
        r2 = requests.post(
            "https://latex.ytotech.com/builds/sync",
            json={"compiler": "pdflatex", "resources": [{"main": True, "content": full_latex}]},
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        if r2.status_code == 201:
            return r2.content, None
        return None, f"API compile error: {r.status_code}"
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# SAFE JSON PARSE
# ══════════════════════════════════════════════════════════════════════════════
def safe_json(text: str):
    text = re.sub(r"```(json)?", "", text).strip().replace("```", "").strip()
    try:
        return json.loads(text)
    except:
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            chunk = text[s:e+1]
            chunk = re.sub(r",\s*}", "}", chunk)
            chunk = re.sub(r",\s*]", "]", chunk)
            try:
                return json.loads(chunk)
            except:
                return None
    return None

def clean_latex(text: str) -> str:
    text = re.sub(r"```(latex)?", "", text).strip()
    text = text.replace("```", "").strip()
    return text

# ══════════════════════════════════════════════════════════════════════════════
# UI SETUP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Resume Generator for Anurag 🔥", page_icon="🚀", layout="centered")

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
        repeating-linear-gradient(0deg, transparent, transparent 50px, rgba(255,255,255,0.012) 50px, rgba(255,255,255,0.012) 51px),
        repeating-linear-gradient(90deg, transparent, transparent 50px, rgba(255,255,255,0.012) 50px, rgba(255,255,255,0.012) 51px);
}
.big-title {
    font-family: 'Bebas Neue', cursive;
    font-size: clamp(2.5rem, 7vw, 4.5rem);
    line-height: 0.95; letter-spacing: 4px; text-align: center; margin-bottom: 2px;
    background: linear-gradient(120deg, #ff6b35 0%, #ffe66d 40%, #06ffa5 70%, #00aaff 100%);
    background-size: 300% 300%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: titleFlow 4s ease-in-out infinite alternate;
}
@keyframes titleFlow { 0% { background-position: 0% 50%; } 100% { background-position: 100% 50%; } }

.subtitle {
    font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #555;
    text-align: center; letter-spacing: 3px; text-transform: uppercase; margin: 4px 0 14px 0;
}
.joke-box {
    background: #0f0f1a; border: 1px solid rgba(255,107,53,0.4);
    border-left: 3px solid #ff6b35; border-radius: 8px;
    padding: 11px 16px; margin: 0 0 18px 0;
    font-family: 'Space Mono', monospace; font-size: 0.74rem; color: #c8b8a0; line-height: 1.7;
}
.joke-tag { color: #ff6b35; font-size: 0.6rem; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; display: block; margin-bottom: 3px; }
.section-head {
    font-family: 'Bebas Neue', cursive; font-size: 0.95rem; letter-spacing: 5px;
    color: #06ffa5; text-transform: uppercase; margin: 20px 0 6px 0;
}

/* Insights card */
.insights-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 10px 0 18px 0;
}
.insight-card {
    background: #0d0d18; border: 1px solid #1e1e30; border-radius: 8px;
    padding: 10px 14px; font-family: 'Rajdhani', sans-serif;
}
.insight-label { font-size: 0.62rem; letter-spacing: 2px; color: #555; text-transform: uppercase; }
.insight-value { font-size: 1rem; color: #e0e0e0; font-weight: 600; margin-top: 2px; }
.skills-required {
    background: #0a1a12; border: 1px solid #06ffa5; border-radius: 8px;
    padding: 10px 14px; margin: 10px 0; font-family: 'Space Mono', monospace;
    font-size: 0.72rem; line-height: 2;
}
.skill-chip {
    background: #0f2a1e; color: #06ffa5; border: 1px solid #1a4030;
    border-radius: 4px; padding: 1px 9px; margin: 2px 3px; display: inline-block;
}
.nice-chip {
    background: #1a1a10; color: #ffe66d; border: 1px solid #3a3a20;
    border-radius: 4px; padding: 1px 9px; margin: 2px 3px; display: inline-block;
}

/* Inputs */
.stTextArea textarea {
    background: #0d0d15 !important; border: 1px solid #252535 !important;
    border-radius: 8px !important; color: #ddd !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important;
    transition: border-color 0.3s, box-shadow 0.3s !important; caret-color: #ff6b35;
}
.stTextArea textarea:focus {
    border-color: #ff6b35 !important;
    box-shadow: 0 0 0 1px rgba(255,107,53,0.3), 0 0 20px rgba(255,107,53,0.1) !important;
}
.stTextArea textarea::placeholder { color: #383848 !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #ff6b35, #ff9a5c) !important;
    color: #000 !important; font-family: 'Bebas Neue', cursive !important;
    font-size: 1.35rem !important; letter-spacing: 4px !important;
    border: none !important; border-radius: 6px !important; height: 54px !important;
    width: 100% !important; box-shadow: 0 0 20px rgba(255,107,53,0.35) !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 0 35px rgba(255,107,53,0.6) !important;
    background: linear-gradient(135deg, #ff8c5a, #ffe66d) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #06ffa5, #00d48a) !important;
    color: #000 !important; font-family: 'Bebas Neue', cursive !important;
    font-size: 1.5rem !important; letter-spacing: 4px !important;
    border: none !important; border-radius: 6px !important; height: 60px !important;
    width: 100% !important; box-shadow: 0 0 24px rgba(6,255,165,0.4) !important;
    transition: all 0.2s !important; animation: pulseGreen 2s ease-in-out infinite;
}
.stDownloadButton > button:hover { transform: translateY(-3px) !important; box-shadow: 0 0 40px rgba(6,255,165,0.7) !important; }
@keyframes pulseGreen { 0%,100% { box-shadow: 0 0 24px rgba(6,255,165,0.4); } 50% { box-shadow: 0 0 40px rgba(6,255,165,0.7); } }

.role-detected {
    background: #0a1a12; border: 1px solid #06ffa5; border-radius: 8px;
    padding: 12px 18px; font-family: 'Rajdhani', sans-serif; font-size: 1.05rem;
    color: #06ffa5; font-weight: 600; letter-spacing: 1px; text-align: center; margin: 10px 0;
}
.kw-container {
    background: #0d0d15; border: 1px solid #1e1e2e; border-radius: 8px;
    padding: 10px 14px; margin: 8px 0 16px 0;
    font-family: 'Space Mono', monospace; font-size: 0.68rem; color: #555; line-height: 2;
}
.kw-chip { background: #14142a; color: #ffe66d; border: 1px solid #2a2a40; border-radius: 4px; padding: 1px 8px; margin: 2px 3px; display: inline-block; }
.footer-txt {
    font-family: 'Space Mono', monospace; font-size: 0.62rem; color: #2a2a3a;
    text-align: center; margin-top: 40px; line-height: 2;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="big-title">AI RESUME GENERATOR</div>
<div class="subtitle">⚡ ATS-optimized &nbsp;•&nbsp; AI-powered &nbsp;•&nbsp; keyword-matched &nbsp;•&nbsp; one-page PDF ⚡</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-head">// Paste Job Description</div>', unsafe_allow_html=True)
jd_input = st.text_area("",height=280,
    placeholder="Paste the full job description here...\n\nInclude everything — role, skills, responsibilities, requirements, qualifications.\nMore context = better keyword matching = higher ATS score.\n\nWorks for any company — Amazon, Google, startups, MNCs.",
    label_visibility="collapsed")

generate_btn = st.button("🚀  GENERATE RESUME", use_container_width=True)

# Session state
for k in ["latex", "pdf_bytes", "insights", "kw_count", "kw_total", "kw_missing"]:
    if k not in st.session_state: st.session_state[k] = None

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════════════════
SPINNERS = [
    "🔍 Scanning JD for keywords and requirements...",
    "⚡ Optimizing for ATS systems...",
    "📝 Injecting keywords with context...",
    "🎯 Maximizing keyword match score...",
    "🧠 Applying Amazon shortlist patterns...",
]

if generate_btn:
    if not jd_input.strip():
        st.warning("⚠️ Please paste a Job Description first.")
        st.stop()

    # ── Step 1: Job Insights ─────────────────────────────────────────────────
    with st.spinner("🔍 JD analyze kar raha hoon..."):
        insights_raw = call_llm(build_insights_prompt(jd_input), max_tokens=600)
        st.session_state.insights = safe_json(insights_raw)

    # ── Step 2: Generate LaTeX Resume ────────────────────────────────────────
    with st.spinner(random.choice(SPINNERS)):
        latex_raw = call_llm(build_resume_prompt(jd_input), max_tokens=2500)
        if latex_raw.startswith("ERROR:"):
            st.error(f"AI Error: {latex_raw}")
            st.stop()
        latex_body = clean_latex(latex_raw)
        st.session_state.latex = latex_body

        # Keyword match analysis
        jd_words    = set(re.findall(r'\b\w{4,}\b', jd_input.lower()))
        resume_words= set(re.findall(r'\b\w{4,}\b', latex_body.lower()))
        matched     = jd_words & resume_words
        st.session_state.kw_count   = len(matched)
        st.session_state.kw_total   = len(jd_words)
        st.session_state.kw_missing = list(jd_words - resume_words)[:10]

    # ── Step 3: Compile PDF ───────────────────────────────────────────────────
    with st.spinner("📄 PDF compile ho raha hai... thoda sabr karo (15-20 seconds)..."):
        pdf, err = compile_to_pdf(latex_body)
        st.session_state.pdf_bytes = pdf
        if err:
            st.warning(f"PDF compile issue: {err}")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.insights or st.session_state.latex:

    # ── Job Insights ─────────────────────────────────────────────────────────
    if st.session_state.insights:
        ins = st.session_state.insights
        st.markdown('<div class="section-head">// Job Analysis</div>', unsafe_allow_html=True)

        # Info cards grid
        cards = [
            ("🎯 Role",         ins.get("role", "—")),
            ("🏢 Company",      ins.get("company", "—")),
            ("📍 Location",     ins.get("location", "—")),
            ("💰 CTC",          ins.get("ctc", "Not specified")),
            ("📅 Experience",   ins.get("experience_required", "—")),
            ("⏱️ Type",         ins.get("employment_type", "—")),
        ]
        cols = st.columns(3)
        for idx, (label, val) in enumerate(cards):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="insight-card">
                    <div class="insight-label">{label}</div>
                    <div class="insight-value">{val}</div>
                </div>""", unsafe_allow_html=True)

        # Role summary
        if ins.get("role_summary"):
            st.markdown(f"""
            <div style="background:#0d0d18;border:1px solid #1e1e30;border-radius:8px;
                        padding:10px 14px;margin:10px 0;font-family:'Rajdhani',sans-serif;
                        font-size:0.95rem;color:#888;line-height:1.6;">
                📋 {ins.get("role_summary","")}
            </div>""", unsafe_allow_html=True)

        # Required skills
        req  = ins.get("key_skills", [])
        nice = ins.get("nice_to_have", [])
        if req:
            req_chips  = "".join([f'<span class="skill-chip">{s}</span>' for s in req])
            nice_chips = "".join([f'<span class="nice-chip">{s}</span>' for s in nice]) if nice else ""
            st.markdown(f"""
            <div class="skills-required">
                <span style="color:#06ffa5;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;">
                    REQUIRED SKILLS</span><br>{req_chips}
                {"<br><span style='color:#ffe66d;font-size:0.62rem;letter-spacing:2px;text-transform:uppercase;'>NICE TO HAVE</span><br>" + nice_chips if nice_chips else ""}
            </div>""", unsafe_allow_html=True)

    # ── Resume Ready ─────────────────────────────────────────────────────────
    if st.session_state.latex:
        st.markdown('<div class="section-head">// Resume Output</div>', unsafe_allow_html=True)

        if st.session_state.kw_count:
            total   = st.session_state.kw_total or 1
            matched = st.session_state.kw_count
            pct     = min(int(matched / total * 100), 99)
            bar_w   = pct
            missing = st.session_state.kw_missing or []
            missing_chips = "".join([f'<span style="background:#1a0a0a;color:#ff6b35;border:1px solid #3a1a1a;border-radius:4px;padding:1px 8px;margin:2px 3px;display:inline-block;font-size:0.68rem;">{w}</span>' for w in missing[:8]])
            st.markdown(f"""
            <div style="background:#0a1a12;border:1px solid #06ffa5;border-radius:10px;padding:14px 18px;margin:10px 0;">
                <div style="font-family:'Space Mono',monospace;font-size:0.65rem;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">KEYWORD MATCH SCORE</div>
                <div style="font-family:'Bebas Neue',cursive;font-size:2.2rem;color:#06ffa5;line-height:1;">{pct}%</div>
                <div style="background:#111;border-radius:4px;height:6px;margin:8px 0;">
                    <div style="background:linear-gradient(90deg,#06ffa5,#00aaff);width:{bar_w}%;height:6px;border-radius:4px;transition:width 1s;"></div>
                </div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.85rem;color:#888;">
                    {matched} keywords matched • Active voice • 6+ metrics • One-page A4
                </div>
                {"<div style=\'margin-top:8px;font-family:Space Mono,monospace;font-size:0.62rem;color:#555;\'>STILL MISSING: " + missing_chips + "</div>" if missing else ""}
            </div>""", unsafe_allow_html=True)

        # Download PDF
        if st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️  DOWNLOAD RESUME PDF",
                data=st.session_state.pdf_bytes,
                file_name="Anurag_Lokhande_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.error("❌ PDF compile failed. Download the .tex file and compile on Overleaf.")

        # Always offer .tex download
        full_tex = LATEX_PREAMBLE + "\n" + st.session_state.latex + "\n" + LATEX_SUFFIX
        st.download_button(
            label="⬇️  DOWNLOAD LaTeX (.tex)",
            data=full_tex,
            file_name="Anurag_Lokhande_Resume.tex",
            mime="text/plain",
            use_container_width=True,
        )

        # View LaTeX Code toggle
        st.markdown('<div class="section-head">// LaTeX Source</div>', unsafe_allow_html=True)
        if st.button("👁  VIEW / EDIT LaTeX CODE", use_container_width=True):
            st.session_state.show_latex = not st.session_state.get("show_latex", False)
        if st.session_state.get("show_latex", False):
            edited = st.text_area(
                "LaTeX Code — edit below, then re-download as .tex",
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
────────────────────────────────────────────────────<br>
AI-powered • ATS-optimized • One-page A4 • Amazon-tested structure<br>
COEP Electrical Engineering 2025 → Software World<br>
────────────────────────────────────────────────────
</div>""", unsafe_allow_html=True)
