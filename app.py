import streamlit as st
import requests
import json
import re

# =========================
# CONFIG
# =========================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

# ✅ Free models that actually work on OpenRouter
# Free models — tries each one in order until one works
MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",   # Best free model (March 2026)
    "mistralai/mistral-7b-instruct:free",         # Reliable fallback
    "google/gemma-3-12b-it:free",                 # Google fallback
    "openrouter/auto",                            # Let OpenRouter pick any free model
]

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://streamlit.io",
    "X-Title": "AI Resume Generator"
}

# =========================
# API CALL
# =========================

def generate_with_openrouter(prompt):
    """Try each free model in order — first one that works wins."""
    last_error = "No models available"
    for model in MODELS:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1200
            }
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                last_error = f"{model} → {response.status_code}: {response.text[:200]}"
        except Exception as e:
            last_error = f"{model} → {str(e)}"
    return {"error": last_error}

# =========================
# SAFE JSON EXTRACTION
# =========================

def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass
    # Strip markdown fences
    text = re.sub(r"```(json)?", "", text).strip()
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1:
        candidate = text[start:end+1]
        candidate = re.sub(r",\s*}", "}", candidate)
        candidate = re.sub(r",\s*]", "]", candidate)
        try:
            return json.loads(candidate)
        except:
            return None
    return None

# =========================
# PROMPT BUILDER
# =========================

def build_resume_prompt(jd, user_info):
    return f"""You are a professional ATS resume writer.

Create an ATS-optimized resume tailored to this job description.

Job Description:
{jd}

Candidate Info:
{json.dumps(user_info, indent=2)}

STRICT RULES:
- Return ONLY valid JSON, nothing else
- No explanation, no markdown, no extra text before or after
- Extract keywords from the JD and use them naturally

Return this exact format:
{{
  "summary": "3-4 line professional summary tailored to JD",
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "duration": "Start – End",
      "points": ["bullet with metric", "bullet with metric"]
    }}
  ]
}}"""

# =========================
# STREAMLIT UI
# =========================

st.set_page_config(page_title="AI Resume Generator", page_icon="📄", layout="centered")
st.title("📄 AI Resume Generator")
st.caption("Powered by OpenRouter — free LLM API")

jd = st.text_area("📋 Paste Job Description", height=250,
                   placeholder="Paste the full job description here...")

is_me = st.checkbox("Are you Anurag? (Load saved profile)")

if is_me:
    user_info = {
        "name": "Anurag Lokhande",
        "email": "lokhandeag21.elec@coeptech.ac.in",
        "phone": "+91 77092 71496",
        "linkedin": "linkedin.com/in/anurag-lokhande-180a5a230",
        "education": "B.Tech Electrical Engineering, COEP Technological University, Pune (2021-2025)",
        "experience": [
            {
                "title": "Account Manager – Technology Platforms",
                "company": "BeyondWalls",
                "duration": "2025 – Present",
                "details": "CRM workflows, data validation, system monitoring, stakeholder management"
            },
            {
                "title": "Software Developer Intern (.NET)",
                "company": "Baker Hughes",
                "duration": "Jan 2025 – Jul 2025",
                "details": "C#/.NET backend development, SQL optimization, Python automation, data migration"
            },
            {
                "title": "Research Intern – Data Analytics",
                "company": "Pune Metro",
                "duration": "Jun 2024 – Jul 2024",
                "details": "SQL, Power BI dashboards, data analysis, operational reporting"
            }
        ],
        "skills": ["Python", "SQL", "C#", ".NET", "Power BI", "Data Analysis",
                   "Backend Development", "API Integration", "Git"]
    }
    st.success("✅ Anurag's profile loaded!")
else:
    st.subheader("Your Details")
    name       = st.text_input("Name")
    email      = st.text_input("Email")
    phone      = st.text_input("Phone")
    education  = st.text_area("Education", height=80)
    experience = st.text_area("Experience (describe your roles)", height=150)
    skills     = st.text_input("Skills (comma separated)")

    user_info = {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience": experience,
        "skills": [s.strip() for s in skills.split(",") if s]
    }

# =========================
# GENERATE
# =========================

if st.button("✨ Generate Resume", type="primary", use_container_width=True):
    if not jd.strip():
        st.error("⚠️ Please paste a Job Description first.")
        st.stop()

    with st.spinner("🤖 AI is writing your resume..."):
        prompt     = build_resume_prompt(jd, user_info)
        ai_output  = generate_with_openrouter(prompt)

    if isinstance(ai_output, dict) and "error" in ai_output:
        st.error(f"API Error: {ai_output['error']}")
        st.stop()

    resume_data = extract_json(ai_output)

    # Retry once if JSON parsing failed
    if not resume_data:
        with st.spinner("🔄 Retrying with stricter prompt..."):
            ai_output   = generate_with_openrouter(prompt + "\nRETURN ONLY JSON. NO OTHER TEXT.")
            resume_data = extract_json(ai_output)

    if not resume_data:
        st.error("❌ AI returned invalid format. Raw output below:")
        st.code(ai_output)
        st.stop()

    st.success("✅ Resume Generated!")

    # ── Display ──────────────────────────────────────────────────────────────
    st.subheader("📝 Professional Summary")
    st.write(resume_data.get("summary", ""))

    st.subheader("🛠️ Skills")
    skills_list = resume_data.get("skills", [])
    st.write(" • ".join(skills_list))

    st.subheader("💼 Experience")
    for exp in resume_data.get("experience", []):
        with st.expander(f"{exp.get('title', '')} — {exp.get('company', '')} ({exp.get('duration', '')})", expanded=True):
            for point in exp.get("points", []):
                st.write(f"• {point}")
