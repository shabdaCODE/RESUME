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
            "title": "Account Manager – Technology Platforms",
            "company": "BeyondWalls",
            "duration": "2025 – Present",
            "raw": "Managed CRM and platform workflows. Backend configuration, data validation, system monitoring. Managed data flows and reporting logic for business-critical systems. Prepared MOMs, system notes, operational documentation. Bridge between business users and technical teams. Tracked 20+ KPIs monthly. Monitored 5+ enterprise systems. Reduced resolution time by 25%."
        },
        {
            "title": "Software Developer Intern (.NET)",
            "company": "Baker Hughes",
            "duration": "Jan 2025 – Jul 2025",
            "raw": "Backend development using C#/.NET in enterprise environment. Refactored and optimized SQL queries improving performance by 40%. Implemented Python scripts for data processing, automation, validation. Designed data pipelines processing 50K+ records/day. Reduced execution time by 30% via query optimization. Worked on data migration ensuring 100% data consistency. Debugged performance bottlenecks reducing error rate by 40%. Shipped 3 production features on schedule. Used Git, CI/CD, REST APIs."
        },
        {
            "title": "Research Intern – Systems & Data Analytics",
            "company": "Pune Metro Rail Corporation",
            "duration": "Jun 2024 – Jul 2024",
            "raw": "Systems analysis and data exploration on operational datasets. Built Power BI dashboards monitoring 10+ KPIs across 5 stations. Python automation for data cleaning reducing manual effort by 60%. SQL-driven reporting. Identified 3 key inefficiencies. Presented structured insights to stakeholders."
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
            "duration": "Apr 2023 – May 2025",
            "raw": "Led cross-functional team of 20+ members. Managed end-to-end production operations under tight deadlines across 5+ events."
        },
        {
            "title": "Operations & Logistics Coordinator",
            "org": "Pune Startup Fest",
            "duration": "Oct 2022 – Mar 2023",
            "raw": "Coordinated logistics for 500+ attendee technical event. Managed vendor relationships, scheduling, on-ground execution."
        }
    ]
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

Your goal: Rewrite Anurag's resume to MAXIMIZE match score against this Job Description.

CANDIDATE PROFILE:
{profile_str}

JOB DESCRIPTION:
{jd}

EXPERT RULES:
1. IDENTIFY HOT KEYWORDS: Extract ALL hard skills, tools, frameworks, industry terms from the JD.
2. ATS-FRIENDLY: No graphics, tables in bullet points. Use standard bullet points only.
3. CONTEXTUAL INTEGRATION: Weave keywords naturally using Action Verb + Task + Result format.
4. QUANTIFY EVERYTHING: Use numbers, percentages, scale wherever possible.
5. ONE PAGE A4: Keep it tight. Max 4 bullets per job, max 3 bullets per project.
6. RELEVANCE FIRST: Only include experience/projects most relevant to JD. Pick best 2 projects.
7. KEYWORD DENSITY: Summary must contain top 5-6 JD keywords. Skills section must mirror JD exactly.
8. YOU CAN ADD: If JD needs a skill Anurag has foundational knowledge of, include it with "basic/foundational" qualifier.
9. ACTIVE VOICE: Start every bullet with a strong action verb. No passive voice.
10. LATEX FORMAT: Output LaTeX body code only (no preamble, no \\begin{{document}}).

LaTeX environments available (pre-defined):
- \\section{{Title}}
- \\begin{{joblong}}{{Title --- Company}}{{Date}} ... \\end{{joblong}} for experience/projects
- \\begin{{tabularx}}{{\\linewidth}}{{@{{}}l X@{{}}}} for skills table (\\textbf{{Label:}} & value \\\\)
- Header uses tabularx with C column type and fontawesome5 icons

SECTION ORDER: Header → Professional Summary → Work Experience → Projects → Education → Technical Skills → Leadership (only if relevant)

HEADER FORMAT (use exactly):
\\begin{{tabularx}}{{\\linewidth}}{{@{{}} C @{{}}}}
{{\\Huge \\textbf{{ANURAG LOKHANDE}}}} \\\\[3pt]
\\href{{tel:+917709271496}}{{\\faMobile\\ +91-770-927-1496}} \\quad | \\quad
\\href{{mailto:lokhandeag21.elec@coeptech.ac.in}}{{\\faEnvelope\\ lokhandeag21.elec@coeptech.ac.in}} \\quad | \\quad
\\href{{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}}{{\\faLinkedin\\ LinkedIn}} \\quad | \\quad
\\href{{https://github.com/anuraglokhande}}{{\\faGithub\\ GitHub}}
\\end{{tabularx}}

OUTPUT: Pure LaTeX body code only. No markdown, no backticks, no explanation."""

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
JOKES = [
    ("RECRUITER SCIENCE 🔬", "They say 'we'll get back to you.' Spoiler: nahi karte. Resume better karo, wait karo, repeat."),
    ("ANURAG'S PLAN 📈", "Baker Hughes → BeyondWalls → Amazon SDE-I → retire in Goa. Last step TBD. 🚀"),
    ("ATS REALITY 🤖", "75% resumes machine se reject hote hain. Tu aaj algorithm se lad raha hai. Aur jeetega."),
    ("COEP PRIDE 💛", "Electrical engineer applying for software roles. 'But why not CS?' — every uncle ever. Bhai, kaam chalta hai."),
    ("HONEST DISCLAIMER ⚠️", "Job guarantee nahi. Better resume guarantee hai. Apply karo, bhagwan bharose."),
    ("FUN FACT 📊", "Recruiters spend 7 seconds on a resume. Pehle 7 seconds mein keywords dikhne chahiye. Done. ✅"),
    ("PRO TIP 💡", "Pura JD paste karo. Jitna zyada, utna zyada keywords. AI samajhdar hai, tera bhi bhala hoga."),
]
tag, joke = random.choice(JOKES)
st.markdown(f"""
<div class="big-title">RESUME GENERATOR<br>FOR ANURAG</div>
<div class="subtitle">⚡ AI-powered &nbsp;•&nbsp; ATS-optimized &nbsp;•&nbsp; sirf JD daalo &nbsp;•&nbsp; PDF ready ⚡</div>
<div class="joke-box"><span class="joke-tag">// {tag}</span>{joke}</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-head">// Step 1 — JD Yahan Daalo</div>', unsafe_allow_html=True)
jd_input = st.text_area("",height=280,
    placeholder="Yahan job description paste karo...\n\nPura JD dalo — role, skills, responsibilities, requirements sab kuch.\nJitna zyada doge, utna zyada keywords match hoga.\n\nAmazon? Google? Startups? Sab supported. 🚀",
    label_visibility="collapsed")

generate_btn = st.button("🚀  GENERATE KARO — AI LIKHEGA, TU APPLY KAREGA", use_container_width=True)

# Session state
for k in ["latex", "pdf_bytes", "insights", "kw_count"]:
    if k not in st.session_state: st.session_state[k] = None

# ══════════════════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════════════════
SPINNERS = [
    "☕ Chai ban raha hai aur resume bhi...",
    "🔍 JD padh raha hoon, keywords dhoondh raha hoon...",
    "⚡ ATS ke liye optimize kar raha hoon...",
    "📝 Bullet points likh raha hoon with authority...",
    "🎯 Recruiter ka attention capture ho raha hai...",
]

if generate_btn:
    if not jd_input.strip():
        st.warning("⚠️ Bhai JD toh daalo pehle. Blank se resume nahi banta.")
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

        # Rough keyword count
        jd_words = set(re.findall(r'\b\w{4,}\b', jd_input.lower()))
        resume_words = set(re.findall(r'\b\w{4,}\b', latex_body.lower()))
        st.session_state.kw_count = len(jd_words & resume_words)

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
        st.markdown('<div class="section-head">// Job Insights</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="section-head">// Resume Ready Hai</div>', unsafe_allow_html=True)

        if st.session_state.kw_count:
            st.markdown(f"""
            <div class="role-detected">
                ✅ &nbsp; ~{st.session_state.kw_count} JD keywords resume mein inject ho gaye
                <br><span style="font-size:0.8rem;color:#888;font-weight:400;">
                ATS ke liye optimized • Active voice • Quantified bullets • One-page A4
                </span>
            </div>""", unsafe_allow_html=True)

        # Download PDF
        if st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️  DOWNLOAD RESUME PDF — PAKAD LO",
                data=st.session_state.pdf_bytes,
                file_name="Anurag_Lokhande_Resume.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown("""<div style="font-family:'Space Mono',monospace;font-size:0.68rem;
                color:#444;text-align:center;margin-top:6px;">
                PDF ready. Apply karo. Rejection aaye toh fir se aana. 💪
            </div>""", unsafe_allow_html=True)
        else:
            # Offer .tex download as fallback
            st.error("❌ PDF compile nahi hua. LaTeX file download karo aur Overleaf pe compile karo.")
            full_tex = LATEX_PREAMBLE + "\n" + st.session_state.latex + "\n" + LATEX_SUFFIX
            st.download_button(
                label="⬇️ Download LaTeX (.tex) — Overleaf pe daalo",
                data=full_tex,
                file_name="Anurag_Lokhande_Resume.tex",
                mime="text/plain",
                use_container_width=True,
            )

# Footer
st.markdown("""
<div class="footer-txt">
────────────────────────────────────────────────────<br>
Made with ☕ + sarcasm + genuine hope for Anurag's job hunt<br>
COEP Electrical 2025 → Software World → 🚀<br>
No API keys were harmed in the making of this resume.<br>
────────────────────────────────────────────────────
</div>""", unsafe_allow_html=True)
