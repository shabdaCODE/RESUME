import streamlit as st
import requests
import json
import re

import streamlit as st
import requests


# =========================
# CONFIG
# =========================

HF_API_KEY = st.secrets["HF_API_KEY"]

MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
API_URL = f"https://router.huggingface.co/hf-inference/models/{MODEL}"

headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json",
}

# =========================
# HUGGING FACE CALL
# =========================

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
# STREAMLIT UI
# =========================

st.title("AI Resume Generator")

jd = st.text_area("Paste Job Description")

if st.button("Generate Resume"):
    if not jd.strip():
        st.error("Please paste a Job Description.")
        st.stop()

    with st.spinner("Generating Resume..."):
        ai_output = generate_with_huggingface(jd)

    if isinstance(ai_output, dict) and "error" in ai_output:
        st.error("API Error:")
        st.code(ai_output["error"])
        st.stop()

    st.success("Output Generated!")
    st.write(ai_output)
