import streamlit as st
import requests
import json
import re

# =========================
# CONFIG
# =========================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

MODEL = "mistralai/mistral-7b-instruct"

API_URL = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://streamlit.io",  # required by OpenRouter
    "X-Title": "AI Resume Generator"
}

# =========================
# HUGGING FACE CALL
# =========================

def generate_with_openrouter(prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()
    return data["choices"][0]["message"]["content"]

# =========================
# SAFE JSON EXTRACTION
# =========================

def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        candidate = text[start:end + 1]
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
    return f"""
You are a professional resume writer.

Create an ATS-optimized resume tailored to this job description.

Job Description:
{jd}

Candidate Info:
{json.dumps(user_info)}

IMPORTANT:
- Return ONLY valid JSON
- No explanation
- No markdown
- No extra text

Format:

{{
  "summary": "text",
  "skills": ["skill1", "skill2"],
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "points": ["bullet1", "bullet2"]
    }}
  ]
}}
"""

# =========================
# STREAMLIT UI
# =========================

st.title("AI Resume Generator")

jd = st.text_area("Paste Job Description")

is_me = st.checkbox("Are you me?")

if is_me:
    user_info = {
        "name": "Anurag Lokhande",
        "email": "your_email@example.com",
        "experience": "5+ years in marketing & real estate strategy",
        "skills": ["Marketing Strategy", "Meta Ads", "Real Estate Sales"]
    }
    st.success("Using saved profile details.")
else:
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    experience = st.text_area("Your Experience")
    skills = st.text_input("Your Skills (comma separated)")

    user_info = {
        "name": name,
        "email": email,
        "experience": experience,
        "skills": [s.strip() for s in skills.split(",") if s]
    }

# =========================
# GENERATE BUTTON
# =========================

if st.button("Generate Resume"):

    if not jd.strip():
        st.error("Please paste a Job Description.")
        st.stop()

    with st.spinner("Generating Resume..."):
        prompt = build_resume_prompt(jd, user_info)
        ai_output = generate_with_openrouter(prompt)

    if isinstance(ai_output, dict) and "error" in ai_output:
        st.error("API Error:")
        st.code(ai_output["error"])
        st.stop()

    resume_data = extract_json(ai_output)

    if not resume_data:
        stricter_prompt = prompt + "\nREMEMBER: RETURN VALID JSON ONLY."
        ai_output = generate_with_openrouter(stricter_prompt)
        resume_data = extract_json(ai_output)

    if not resume_data:
        st.error("AI failed to generate valid JSON.")
        st.code(ai_output)
        st.stop()

    st.success("Resume Generated Successfully!")

    st.subheader("Professional Summary")
    st.write(resume_data.get("summary", ""))

    st.subheader("Skills")
    st.write(", ".join(resume_data.get("skills", [])))

    st.subheader("Experience")
    for exp in resume_data.get("experience", []):
        st.markdown(f"### {exp.get('title')} - {exp.get('company')}")
        for point in exp.get("points", []):
            st.write(f"- {point}")
