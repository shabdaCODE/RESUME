import os
import json
import re
import requests
import streamlit as st
from dotenv import load_dotenv

# PDF (Cloud Safe)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import LETTER

# ===============================
# LOAD ENV
# ===============================

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

# ===============================
# HUGGING FACE CONFIG
# ===============================

HF_MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

def generate_with_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 900,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    response = requests.post(HF_MODEL_URL, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]
    else:
        return str(result)

# ===============================
# SAFE JSON EXTRACTION
# ===============================

def extract_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None

# ===============================
# PROMPT
# ===============================

def build_resume_prompt(jd, user_info):
    return f"""
You are an expert resume writer.

Create an ATS-optimized resume tailored to this Job Description.

Candidate Info:
{json.dumps(user_info, indent=2)}

Job Description:
{jd}

Requirements:
- Quantified achievements
- Bullet format
- Professional tone
- Strong action verbs
- No extra explanation text

Return STRICT JSON only:
{{
  "summary": "text",
  "experience": ["bullet1", "bullet2"],
  "projects": ["bullet1", "bullet2"],
  "skills": ["skill1", "skill2"]
}}
"""

# ===============================
# PDF GENERATION
# ===============================

def generate_pdf(data, user_info):
    file_path = "resume.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=LETTER)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>{user_info['name']}</b>", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(
        Paragraph(f"{user_info['email']} | {user_info['phone']}", styles["Normal"])
    )
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Professional Summary</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(Paragraph(data["summary"], styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Experience</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))

    exp_list = [
        ListItem(Paragraph(exp.strip(), styles["Normal"]))
        for exp in data["experience"]
    ]
    elements.append(ListFlowable(exp_list, bulletType="bullet"))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))

    proj_list = [
        ListItem(Paragraph(proj.strip(), styles["Normal"]))
        for proj in data["projects"]
    ]
    elements.append(ListFlowable(proj_list, bulletType="bullet"))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("<b>Skills</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(
        Paragraph(", ".join([s.strip() for s in data["skills"]]),
        styles["Normal"])
    )

    doc.build(elements)
    return file_path

# ===============================
# STREAMLIT UI
# ===============================

st.title("AI Resume Generator")

# ===== Checkbox =====

is_me = st.checkbox("Are you me?")

if is_me:
    # Auto-fill your details
    user_info = {
        "name": "Anurag Lokhande",
        "email": "your_email@example.com",
        "phone": "your_phone_number"
    }
    st.success("Using saved profile details.")

else:
    st.subheader("Enter Personal Details")
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")

    user_info = {
        "name": name,
        "email": email,
        "phone": phone
    }

# ===== JD Input =====

st.subheader("Paste Job Description")
jd = st.text_area("Job Description", height=250)

# ===== Generate =====

if st.button("Generate Resume"):

    if not HF_API_KEY:
        st.error("HuggingFace API Key not found in environment.")
        st.stop()

    with st.spinner("Generating Resume..."):
        prompt = build_resume_prompt(jd, user_info)
        ai_output = generate_with_huggingface(prompt)

    resume_data = extract_json(ai_output)

    if not resume_data:
        st.error("AI did not return valid JSON.")
        st.write(ai_output)
        st.stop()

    st.subheader("Edit Resume")

    resume_data["summary"] = st.text_area(
        "Summary",
        value=resume_data["summary"]
    )

    st.write("### Experience")
    for i in range(len(resume_data["experience"])):
        resume_data["experience"][i] = st.text_area(
            f"Experience {i+1}",
            value=resume_data["experience"][i]
        )

    st.write("### Projects")
    for i in range(len(resume_data["projects"])):
        resume_data["projects"][i] = st.text_area(
            f"Project {i+1}",
            value=resume_data["projects"][i]
        )

    skills_input = st.text_input(
        "Skills (comma separated)",
        value=", ".join(resume_data["skills"])
    )
    resume_data["skills"] = skills_input.split(",")

    if st.button("Download PDF"):
        pdf_path = generate_pdf(resume_data, user_info)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Resume",
                f,
                file_name="resume.pdf"
            )
