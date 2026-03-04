import streamlit as st
import requests
import json
import re
import subprocess
import os
import tempfile
import random

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG — Google Gemini API (Free Tier)
# ══════════════════════════════════════════════════════════════════════════════
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
# Gemini free models in priority order (verified working, March 2026)
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",   # fastest, free, most available
    "gemini-2.0-flash",        # slightly larger, also free
    "gemini-1.5-flash",        # stable fallback
]

# ══════════════════════════════════════════════════════════════════════════════
# CANDIDATE PROFILE — ANURAG LOKHANDE (sourced from actual resume PDF)
# ══════════════════════════════════════════════════════════════════════════════
ANURAG = {
    "name": "ANURAG LOKHANDE",
    "phone": "+91-770-927-1496",
    "email": "lokhandeag21.elec@coeptech.ac.in",
    "linkedin": "linkedin.com/in/anurag-lokhande-180a5a230",
    "education": {
        "degree": "B.Tech in Electrical Engineering",
        "university": "COEP Technological University, Pune",
        "years": "2021 – 2025",
        "coursework": "Data Structures & Algorithms, OOP, DBMS, Operating Systems, Computer Networks, Engineering Mathematics, Statistics & Probability"
    },
    "summary": (
        "Software Engineering graduate with strong foundations in data structures, algorithms, "
        "object-oriented programming, and relational databases. Hands-on experience designing backend "
        "systems, optimizing SQL workflows, and building automation pipelines using Python, C++, C#, and SQL. "
        "Demonstrated ownership across the software development lifecycle including design, implementation, "
        "debugging, and documentation."
    ),
    "experience": [
        {
            "title": "Software Engineering Intern",
            "company": "Baker Hughes",
            "duration": "01/2025 – 07/2025",
            "bullets": [
                "Designed and optimized backend data pipelines to process large datasets efficiently in a production environment.",
                "Refactored legacy SQL and Python scripts into modular, object-oriented components, improving maintainability and performance.",
                "Worked on data migration workflows with emphasis on data consistency, validation, and failure handling.",
                "Debugged performance bottlenecks and collaborated with cross-functional teams to improve system reliability.",
                "Authored technical documentation covering system design, data flows, and operational processes."
            ]
        },
        {
            "title": "Research Intern",
            "company": "Pune Metro Rail Corporation",
            "duration": "06/2024 – 07/2024",
            "bullets": [
                "Built data analysis and reporting solutions to monitor operational metrics across multiple metro stations.",
                "Developed Python-based automation for data cleaning, transformation, and validation.",
                "Performed exploratory analysis to identify trends, inefficiencies, and system-level patterns.",
                "Presented technical insights to stakeholders using structured reports and dashboards."
            ]
        }
    ],
    "projects": [
        {
            "name": "Data Migration & SQL Optimization System",
            "duration": "01/2025 – 04/2025",
            "bullets": [
                "Designed a modular data migration framework using C# and Python, applying object-oriented design principles.",
                "Optimized complex SQL queries and indexing strategies, reducing execution time by 30%.",
                "Implemented automated validation checks and error handling to ensure fault-tolerant data movement.",
                "Built reusable components to support scalability and future system extensions."
            ]
        },
        {
            "name": "Credit Card Fraud Detection System",
            "duration": "11/2024 – 12/2024",
            "bullets": [
                "Built an end-to-end fraud detection pipeline using Python with clear separation of concerns via OOP.",
                "Applied classification algorithms on imbalanced datasets and evaluated models using precision-recall metrics.",
                "Processed large transaction datasets efficiently using optimized data structures.",
                "Visualized system outputs to support debugging, monitoring, and model evaluation."
            ]
        }
    ],
    "skills": {
        "Programming Languages": ["Python", "C++", "C#", "Java", "SQL"],
        "Computer Science": ["Data Structures", "Algorithms", "OOP", "Complexity Analysis"],
        "Backend & Databases": ["MySQL", "Relational Databases", "Query Optimization", "PostgreSQL"],
        "Engineering Practices": ["Debugging", "Code Reviews", "CI/CD basics", "Technical Documentation"],
        "Tools": ["Git", "Power BI", "Pandas", "NumPy", "Postman"]
    },
    "leadership": [
        {
            "title": "Production & Backstage Head",
            "org": "COEP Drama and Films Club",
            "duration": "04/2023 – 05/2025",
            "detail": "Led cross-functional teams and managed operations under tight deadlines."
        },
        {
            "title": "Operations & Logistics Coordinator",
            "org": "Pune Startup Fest",
            "duration": "10/2022 – 03/2023",
            "detail": "Coordinated logistics and communication for a large-scale technical event."
        }
    ]
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
# GEMINI API CALL WITH MODEL FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
def call_gemini(prompt: str, max_tokens: int = 2500) -> str:
    import time
    last_error = "No model responded"
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": max_tokens
            }
        }
        try:
            r = requests.post(url, json=payload, timeout=90)
            if r.status_code == 200:
                data = r.json()
                try:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    if text and text.strip():
                        return text.strip()
                    last_error = f"{model}: empty response"
                except (KeyError, IndexError):
                    last_error = f"{model}: unexpected response structure"
                continue
            elif r.status_code == 429:
                time.sleep(3)
                last_error = f"{model}: rate limited"
            else:
                last_error = f"{model}: {r.status_code} — {r.text[:150]}"
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

CANDIDATE PROFILE (use ONLY facts from this — do not invent any experience or skills):
{profile_str}

JOB DESCRIPTION:
{jd}

═══ MANDATORY RULES — ALL MUST BE FOLLOWED ═══

━━ ACCURACY — MOST IMPORTANT RULE ━━
- NEVER fabricate experience, skills, companies, dates, or metrics not present in the profile
- Only use skills the candidate actually has; add "(basic)" qualifier for foundational ones
- You may rephrase and reorder bullet points to better match JD keywords — but facts must remain true

━━ CONTACT & HEADER ━━
- Phone "+91-770-927-1496" MUST appear as plain readable text
- Email "lokhandeag21.elec@coeptech.ac.in" MUST appear as plain readable text
- Extract the EXACT job title from the JD and add it as an italic subtitle line under the name

━━ KEYWORD INJECTION ━━
- Extract EVERY technical skill, tool, framework, soft skill from the JD
- Each JD keyword MUST appear at least once, woven in naturally from real experience
- Summary must contain top 6 JD keywords + role title
- Skills section must mirror JD keywords exactly where Anurag genuinely has them

━━ MEASURABLE RESULTS ━━
Use only real metrics from the profile:
- 30% SQL execution time reduction
- fault-tolerant data movement with validation
- 500+ attendee event coordination
- 20+ team members led
- multiple metro stations monitored
Add no invented numbers.

━━ WORD COUNT ━━
Minimum 600 words total — write rich, full bullet points

━━ DATE FORMAT ━━
ALL dates in MM/YYYY format: e.g. "01/2025 – 07/2025"

━━ ACTION VERBS ━━
Start EVERY bullet with a strong verb: Engineered, Architected, Delivered, Collaborated,
Optimized, Automated, Designed, Implemented, Streamlined, Refactored, Reduced, Developed, Adapted

━━ ONE PAGE A4 ━━
Max 5 bullets per job, max 3 bullets per project — pick 2 most relevant projects for this JD

━━ SECTION ORDER ━━
Header → Professional Summary → Work Experience → Projects →
Education (with Relevant Coursework line) → Technical Skills → Leadership & Activities

━━ LATEX OUTPUT RULES ━━
- Output LaTeX BODY CODE ONLY — no preamble, no \begin{{document}}, no markdown, no backticks
- Use these pre-defined environments:
  \section{{Title}}
  \begin{{joblong}}{{Title --- Company}}{{MM/YYYY – MM/YYYY}} ... \end{{joblong}}
  Skills: \begin{{tabularx}}{{\linewidth}}{{@{{}}l X@{{}}}} \textbf{{Label:}} & value \\\\ \end{{tabularx}}

━━ HEADER — COPY THIS EXACTLY (replace [EXACT JOB TITLE FROM JD]) ━━
\begin{{tabularx}}{{\linewidth}}{{@{{}} C @{{}}}}
{{\Huge \textbf{{ANURAG LOKHANDE}}}} \\\\[2pt]
\textit{{[EXACT JOB TITLE FROM JD]}} \\\\[3pt]
+91-770-927-1496 \quad | \quad lokhandeag21.elec@coeptech.ac.in \quad | \quad
\href{{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}}{{linkedin.com/in/anurag-lokhande}}
\end{{tabularx}}

OUTPUT: Pure LaTeX body only. No markdown. No backticks. No explanation."""

# ══════════════════════════════════════════════════════════════════════════════
# PDF COMPILER — local pdflatex → latexonline.cc → ytotech
# ══════════════════════════════════════════════════════════════════════════════
def compile_to_pdf(latex_body: str):
    full_latex = LATEX_PREAMBLE + "\n" + latex_body + "\n" + LATEX_SUFFIX
    # Try local pdflatex first
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
    # Fallback 1: latexonline.cc
    try:
        r = requests.post(
            "https://latexonline.cc/compile",
            files={"file": ("resume.tex", full_latex.encode("utf-8"), "text/plain")},
            timeout=90
        )
        if r.status_code == 200 and "application/pdf" in r.headers.get("content-type", ""):
            return r.content, None
    except Exception:
        pass
    # Fallback 2: ytotech
    try:
        r2 = requests.post(
            "https://latex.ytotech.com/builds/sync",
            json={"compiler": "pdflatex", "resources": [{"main": True, "content": full_latex}]},
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        if r2.status_code == 201:
            return r2.content, None
        return None, f"Compile error: {r2.status_code}"
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def safe_json(text: str):
    text = re.sub(r"```(json)?", "", text).strip().replace("```", "").strip()
    try:
        return json.loads(text)
    except Exception:
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1:
            chunk = re.sub(r",\s*}", "}", text[s:e+1])
            chunk = re.sub(r",\s*]", "]", chunk)
            try:
                return json.loads(chunk)
            except Exception:
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
.info-banner {
    background: #0d1a0d; border: 1px solid #1a3a1a; border-radius: 8px;
    padding: 10px 16px; margin: 10px 0;
    font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #3a7a3a;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="big-title">AI RESUME GENERATOR</div>
<div class="subtitle">⚡ ATS-optimized &nbsp;•&nbsp; keyword-injected &nbsp;•&nbsp; Gemini-powered &nbsp;•&nbsp; one-page PDF ⚡</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-banner">
    ✅ &nbsp;Profile loaded: <strong style="color:#06ffa5">Anurag Lokhande</strong> &nbsp;•&nbsp;
    B.Tech EE @ COEP &nbsp;•&nbsp;
    Baker Hughes SWE Intern &nbsp;•&nbsp;
    Pune Metro Research Intern<br>
    🤖 &nbsp;Powered by Google Gemini (free tier) &nbsp;•&nbsp;
    Paste any JD below → get a tailored ATS resume in seconds
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INPUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-head">// Paste Job Description</div>', unsafe_allow_html=True)
jd_input = st.text_area(
    "Job Description",
    height=280,
    placeholder=(
        "Paste the full job description here...\n\n"
        "Include everything — role title, skills, responsibilities, requirements, qualifications.\n"
        "More detail = better keyword extraction = higher ATS match score."
    ),
    label_visibility="collapsed"
)

generate_btn = st.button("🚀  GENERATE RESUME", use_container_width=True)

# Session state init
for k in ["latex", "pdf_bytes", "insights", "kw_count", "kw_total", "kw_missing"]:
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
    "🧠 Tailoring bullets to this specific role...",
]

if generate_btn:
    if not jd_input.strip():
        st.warning("⚠️ Please paste a Job Description first.")
        st.stop()

    with st.spinner("🔍 Analyzing job description..."):
        insights_raw = call_gemini(build_insights_prompt(jd_input), max_tokens=600)
        st.session_state.insights = safe_json(insights_raw)

    with st.spinner(random.choice(SPINNERS)):
        latex_raw = call_gemini(build_resume_prompt(jd_input), max_tokens=2500)
        if latex_raw.startswith("ERROR:"):
            st.error(f"AI Error: {latex_raw}\n\n💡 Check your GEMINI_API_KEY in Streamlit secrets.")
            st.stop()
        latex_body = clean_latex(latex_raw)
        st.session_state.latex = latex_body

        # Keyword match score
        jd_words     = set(re.findall(r'\b\w{4,}\b', jd_input.lower()))
        resume_words = set(re.findall(r'\b\w{4,}\b', latex_body.lower()))
        matched      = jd_words & resume_words
        st.session_state.kw_count   = len(matched)
        st.session_state.kw_total   = len(jd_words)
        st.session_state.kw_missing = list(jd_words - resume_words)[:10]

    with st.spinner("📄 Compiling PDF... (15–25 seconds)"):
        pdf, err = compile_to_pdf(latex_body)
        st.session_state.pdf_bytes = pdf
        if err:
            st.warning(f"PDF compile note: {err}")

# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.insights or st.session_state.latex:

    # ── Job Analysis ──────────────────────────────────────────────────────────
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
                    {matched} of {total} JD keywords matched &nbsp;•&nbsp; Active voice &nbsp;•&nbsp; One-page A4
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
            st.info("💡 PDF compile unavailable on this server — download the .tex file and compile at overleaf.com (free, 30 seconds)")

        # Always available .tex download
        full_tex = LATEX_PREAMBLE + "\n" + st.session_state.latex + "\n" + LATEX_SUFFIX
        st.download_button(
            label="⬇️  DOWNLOAD LaTeX SOURCE (.tex)",
            data=full_tex,
            file_name="Anurag_Lokhande_Resume.tex",
            mime="text/plain",
            use_container_width=True,
        )

        # View / Edit LaTeX toggle
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

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-txt">
─────────────────────────────────────────────<br>
Gemini-powered &nbsp;•&nbsp; ATS-optimized &nbsp;•&nbsp; One-page A4 &nbsp;•&nbsp; 100% accurate to your profile<br>
COEP Electrical Engineering 2025 → Software World<br>
─────────────────────────────────────────────
</div>""", unsafe_allow_html=True)
