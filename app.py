import streamlit as st
import google.generativeai as genai
import subprocess
import os
import tempfile
import re

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Anurag's Resume Generator", page_icon="📄", layout="centered")

st.title("📄 JD → ATS Resume Generator")
st.caption("Paste a Job Description → get a tailored, ATS-friendly resume as a PDF")

# ── Sidebar: API Key ──────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("Gemini API key loaded ✅")
else:
    api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password",
                                     help="Get your free key at aistudio.google.com")

# ── Fixed candidate info ──────────────────────────────────────────────────────
CANDIDATE_INFO = """
Name: Anurag Lokhande
Phone: +91 77092 71496
Email: lokhandeag21.elec@coeptech.ac.in
LinkedIn: https://www.linkedin.com/in/anurag-lokhande-180a5a230/

Education:
- B.Tech in Electrical Engineering, COEP Technological University, Pune (2021-2025)

Experience:
1. Account Manager - Technology Platforms | BeyondWalls (2025 - Present)
   - Worked with engineering, product, and operations teams to support in-house CRM and platform workflows.
   - Backend configuration, data validation, and system monitoring.
   - Managed data flows, reporting logic, and documentation for business-critical systems.
   - Prepared MOMs, system notes, and operational documentation aligned with enterprise standards.
   - Bridge between business users and technical teams, translating requirements into system tasks.

2. Software Developer Intern (.NET) | Baker Hughes (Jan 2025 - Jul 2025)
   - Backend application development using C#/.NET in enterprise environment.
   - Refactored and optimized backend logic and SQL queries for performance.
   - Implemented Python scripts for data processing, automation, and validation.
   - Supported integration of multiple data sources.
   - Testing, debugging, change documentation, and production support.

3. Research Intern - Systems & Data Analytics | Pune Metro (Jun 2024 - Jul 2024)
   - Systems analysis and data exploration on operational and power generation datasets.
   - Built reports and dashboards using SQL and Power BI.
   - Validated data accuracy and improved reporting reliability.
   - Documented analytical logic and findings for cross-functional teams.

Projects:
1. Data Migration and Backend Optimization Project
   - Migrated structured datasets across environments using SQL and backend logic.
   - Optimized queries and backend scripts for execution efficiency.
   - Ensured data integrity through validation checks and reconciliation.
   - Maintained technical documentation for audit and handover.

2. Backend Application Development Project
   - Developed backend modules using C#/.NET following enterprise coding standards.
   - Implemented database interactions and basic API endpoints.
   - Performed unit testing, debugging, and documentation.

Technical Skills:
- Backend & Programming: C#/.NET, Python, SQL
- Platform & Systems: ServiceNow (Foundational), CRM Platforms, Enterprise Systems
- Data & Integration: SQL Databases, API Integration, Data Validation, Data Migration
- Development Practices: System Analysis, Backend Optimization, Debugging, Documentation
- Enterprise Practices: Change Management, Secure Coding Awareness, Production Support
- Professional: Stakeholder Communication, Cross-Functional Collaboration, Attention to Detail
"""

LATEX_PREAMBLE = r"""
\documentclass[a4paper,11pt]{article}
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

\newenvironment{joblong}[2]
{
\begin{tabularx}{\linewidth}{@{}l X r@{}}
\textbf{#1} & & #2 \\[1pt]
\end{tabularx}
\begin{itemize}[leftmargin=1em, itemsep=2pt, topsep=2pt, label=--]
}
{
\end{itemize}
}

\begin{document}
\pagestyle{empty}
"""

LATEX_SUFFIX = r"""
\end{document}
"""

def build_prompt(jd: str) -> str:
    return f"""You are an expert ATS resume writer specializing in LaTeX resumes.

TASK: Generate the BODY of a LaTeX resume (everything between \\begin{{document}} and \\end{{document}}, but do NOT include those tags or the preamble).

CANDIDATE INFO (use ALL of this, do not invent new info):
{CANDIDATE_INFO}

JOB DESCRIPTION:
{jd}

STRICT RULES:
1. Use ONLY the candidate's real info - do NOT fabricate anything.
2. Extract important keywords from the JD and naturally weave them into the resume where genuinely applicable.
3. Resume MUST fit on ONE A4 page - keep bullet points concise (max 1 line each).
4. Use these LaTeX environments (already defined in preamble):
   - \\section{{Title}} for sections
   - \\begin{{joblong}}{{Job Title | Company}}{{Date}} ... \\end{{joblong}} for experience/projects
5. Header: centered tabularx with name, phone, email, LinkedIn using fontawesome5 icons and hyperlinks.
6. Section order: Header -> Professional Summary -> Professional Experience -> Projects -> Education -> Technical Skills
7. Professional Summary: 3-4 lines tailored to JD with relevant keywords.
8. Output ONLY raw LaTeX code - no markdown, no backticks, no explanation.
9. Escape & as \\& except inside \\href{{}} URLs.

OUTPUT: Pure LaTeX body code only."""

def compile_latex_to_pdf(latex_body: str):
    full_latex = LATEX_PREAMBLE + "\n" + latex_body + "\n" + LATEX_SUFFIX
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(full_latex)
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                capture_output=True, text=True
            )
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                return f.read()
        else:
            st.error("LaTeX compilation failed. See log below:")
            st.code(result.stdout[-3000:], language="text")
            return None

jd_input = st.text_area(
    "📋 Paste the Job Description here",
    height=280,
    placeholder="Paste the full job description including required skills, responsibilities, and qualifications..."
)

col1, col2 = st.columns([2, 1])
with col1:
    generate_btn = st.button("✨ Generate Resume", type="primary", use_container_width=True)
with col2:
    show_latex = st.checkbox("Show LaTeX code", value=False)

if "latex_body" not in st.session_state:
    st.session_state.latex_body = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if generate_btn:
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not jd_input.strip():
        st.warning("Please paste a Job Description.")
    else:
        with st.spinner("🤖 Generating ATS-optimized resume..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(build_prompt(jd_input))
                latex_body = response.text.strip()
                latex_body = re.sub(r"```(latex)?", "", latex_body).strip()
                latex_body = latex_body.replace("```", "").strip()
                st.session_state.latex_body = latex_body
            except Exception as e:
                st.error(f"Gemini API error: {e}")
                st.stop()

        with st.spinner("📄 Compiling PDF..."):
            check = subprocess.run(["which", "pdflatex"], capture_output=True)
            if check.returncode != 0:
                st.warning("pdflatex not available. Copy the LaTeX code below and paste it at overleaf.com to get your PDF.")
                st.session_state.pdf_bytes = None
            else:
                st.session_state.pdf_bytes = compile_latex_to_pdf(st.session_state.latex_body)

if st.session_state.latex_body:
    st.success("✅ Resume generated!")
    if st.session_state.pdf_bytes:
        st.download_button(
            label="⬇️ Download Resume (PDF)",
            data=st.session_state.pdf_bytes,
            file_name="Anurag_Lokhande_Resume.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    else:
        st.info("Copy the LaTeX code below and paste it into overleaf.com to download your PDF.")

    if show_latex or not st.session_state.pdf_bytes:
        st.subheader("📝 LaTeX Source Code")
        full_code = LATEX_PREAMBLE + "\n" + st.session_state.latex_body + "\n" + LATEX_SUFFIX
        st.code(full_code, language="latex")
        st.download_button(
            label="⬇️ Download LaTeX (.tex)",
            data=full_code,
            file_name="Anurag_Lokhande_Resume.tex",
            mime="text/plain",
            use_container_width=True
        )
