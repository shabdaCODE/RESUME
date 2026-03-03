import os
import json
import requests
import streamlit as st
from weasyprint import HTML
from dotenv import load_dotenv

load_dotenv()

# ===============================
# CONFIG
# ===============================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/generate"

# ===============================
# AI LAYER
# ===============================

def generate_with_openai(prompt):
    import openai
    openai.api_key = OPENAI_API_KEY
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    return response["choices"][0]["message"]["content"]


def generate_with_huggingface(prompt):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.7
        }
    }
    
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers=headers,
        json=payload,
    )
    
    return response.json()[0]["generated_text"]


def generate_with_ollama(prompt, model="mistral"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]


def generate_ai_response(prompt, provider):
    if provider == "OpenAI" and OPENAI_API_KEY:
        return generate_with_openai(prompt)
    elif provider == "HuggingFace" and HF_API_KEY:
        return generate_with_huggingface(prompt)
    elif provider == "Ollama":
        return generate_with_ollama(prompt)
    else:
        return "⚠️ No valid AI provider configured."


# ===============================
# PROMPT BUILDERS
# ===============================

def build_role_detection_prompt(jd):
    return f"""
    Analyze the following Job Description and identify:
    1. Target Role (e.g., SDE, Data Scientist, Consultant)
    2. Seniority Level
    3. Core Skills Required

    JD:
    {jd}

    Return output in structured JSON.
    """


def build_resume_generation_prompt(jd, user_info):
    return f"""
    Create an ATS-optimized resume based on:

    Candidate Info:
    {json.dumps(user_info, indent=2)}

    Job Description:
    {jd}

    Requirements:
    - Tailored bullet points
    - Quantified achievements
    - Relevant tech stack
    - Clean professional tone
    - No fluff

    Output in structured JSON format:
    {{
      "summary": "...",
      "experience": [...],
      "projects": [...],
      "skills": [...]
    }}
    """


# ===============================
# PDF GENERATION
# ===============================

def generate_pdf(html_content):
    HTML(string=html_content).write_pdf("resume.pdf")
    return "resume.pdf"


def build_html_resume(data, user_info):
    html = f"""
    <html>
    <head>
    <style>
    body {{ font-family: Arial; margin: 40px; }}
    h1 {{ margin-bottom: 5px; }}
    h2 {{ margin-top: 25px; }}
    ul {{ margin-left: 20px; }}
    </style>
    </head>
    <body>
    <h1>{user_info["name"]}</h1>
    <p>{user_info["email"]} | {user_info["phone"]}</p>

    <h2>Professional Summary</h2>
    <p>{data["summary"]}</p>

    <h2>Experience</h2>
    {"".join([f"<p><b>{exp}</b></p>" for exp in data["experience"]])}

    <h2>Projects</h2>
    {"".join([f"<p>{proj}</p>" for proj in data["projects"]])}

    <h2>Skills</h2>
    <p>{", ".join(data["skills"])}</p>
    </body>
    </html>
    """
    return html


# ===============================
# STREAMLIT UI
# ===============================

st.title("AI Resume Generator")

provider = st.selectbox(
    "Select AI Provider",
    ["OpenAI", "HuggingFace", "Ollama"]
)

st.subheader("Enter Personal Details")

name = st.text_input("Name")
email = st.text_input("Email")
phone = st.text_input("Phone")

st.subheader("Paste Job Description")
jd = st.text_area("Job Description", height=200)

if st.button("Generate Resume"):

    user_info = {
        "name": name,
        "email": email,
        "phone": phone
    }

    with st.spinner("Analyzing JD..."):
        role_prompt = build_role_detection_prompt(jd)
        role_analysis = generate_ai_response(role_prompt, provider)
        st.write("### Role Analysis")
        st.write(role_analysis)

    with st.spinner("Generating Resume..."):
        resume_prompt = build_resume_generation_prompt(jd, user_info)
        resume_output = generate_ai_response(resume_prompt, provider)

    try:
        resume_data = json.loads(resume_output)
    except:
        st.error("AI did not return valid JSON.")
        st.stop()

    st.subheader("Edit Resume Content")

    resume_data["summary"] = st.text_area(
        "Summary", value=resume_data["summary"]
    )

    st.write("### Experience")
    for i, exp in enumerate(resume_data["experience"]):
        resume_data["experience"][i] = st.text_area(
            f"Experience {i+1}", value=exp
        )

    st.write("### Projects")
    for i, proj in enumerate(resume_data["projects"]):
        resume_data["projects"][i] = st.text_area(
            f"Project {i+1}", value=proj
        )

    resume_data["skills"] = st.text_input(
        "Skills (comma separated)",
        value=", ".join(resume_data["skills"])
    ).split(",")

    if st.button("Download PDF"):
        html = build_html_resume(resume_data, user_info)
        pdf_path = generate_pdf(html)

        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download Resume",
                f,
                file_name="resume.pdf"
            )
