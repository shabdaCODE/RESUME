import streamlit as st
import requests
import json
import re
import os

HF_API_KEY = os.getenv("HF_API_KEY")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json",
}

# ----------------------------
# Hugging Face Generation
# ----------------------------
def generate_with_huggingface(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.4
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return {"error": response.text}

    data = response.json()

    if isinstance(data, list):
        return data[0].get("generated_text", "")
    elif isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    else:
        return str(data)

# ----------------------------
# Safe JSON Extractor
# ----------------------------
def extract_json(text):
    try:
        return json.loads(text)
    except:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        json_candidate = text[start:end + 1]
        json_candidate = re.sub(r",\s*}", "}", json_candidate)
        json_candidate = re.sub(r",\s*]", "]", json_candidate)

        try:
            return json.loads(json_candidate)
        except:
            return None

    return None

# ----------------------------
# Prompt Builder
# ----------------------------
def build_resume_prompt(jd, user_info):
    return f"""
You are a professional resume writer.

Using the following job description:

{jd}

Using this candidate information:

{json.dumps(user_info)}

Return ONLY valid JSON.
Do NOT include explanation.
Do NOT use markdown.
Do NOT wrap in code block.

Format:

{{
  "summary": "...",
  "skills": ["...", "..."],
  "experience": [
      {{
        "title": "...",
        "company": "...",
        "points": ["...", "..."]
      }}
  ]
}}
"""

# ----------------------------
# UI
# ----------------------------
st.title("AI Resume Generator")

jd = st.text_area("Paste Job Description")

is_me = st.checkbox("Are you me?")

if is_me:
    # Predefined info
    user_info = {
        "name": "Anurag Lokhande",
        "email": "your_email@example.com",
        "experience": "5+ years in marketing & real estate strategy",
        "skills": ["Marketing Strategy", "Meta Ads", "Real Estate Sales"]
    }
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

if st.button("Generate Resume"):
    if not jd:
        st.error("Please paste Job Description")
        st.stop()

    with st.spinner("Generating Resume..."):
        prompt = build_resume_prompt(jd, user_info)
        ai_output = generate_with_huggingface(prompt)

    if isinstance(ai_output, dict) and "error" in ai_output:
        st.error(ai_output["error"])
        st.stop()

    resume_data = extract_json(ai_output)

    if not resume_data:
        # Retry once
        stricter_prompt = prompt + "\nREMEMBER: RETURN VALID JSON ONLY."
        ai_output = generate_with_huggingface(stricter_prompt)
        resume_data = extract_json(ai_output)

    if not resume_data:
        st.error("AI failed to generate valid JSON.")
        st.write(ai_output)
        st.stop()

    st.success("Resume Generated Successfully!")

    st.subheader("Summary")
    st.write(resume_data.get("summary", ""))

    st.subheader("Skills")
    st.write(", ".join(resume_data.get("skills", [])))

    st.subheader("Experience")
    for exp in resume_data.get("experience", []):
        st.markdown(f"### {exp.get('title')} - {exp.get('company')}")
        for point in exp.get("points", []):
            st.write(f"- {point}")
