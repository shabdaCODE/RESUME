import streamlit as st
import openai

st.set_page_config(page_title="JD to Resume", page_icon="📄")
st.title("📄 JD to Resume Converter")

api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")
jd_input = st.text_area("Paste Job Description here", height=250)
user_bg  = st.text_area("Your background / skills (brief)", height=150)

if st.button("Generate Resume"):
    if not api_key or not jd_input:
        st.warning("Please provide API key and a Job Description.")
    else:
        openai.api_key = api_key
        with st.spinner("Generating your tailored resume..."):
            prompt = f"""You are a professional resume writer.
Job Description: {jd_input}
Candidate Background: {user_bg}
Write an ATS-friendly resume with: Summary, Skills, Experience, Education."""
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt}]
            )
            result = response.choices[0].message.content
        st.success("Resume Generated!")
        st.markdown(result)
        st.download_button("⬇ Download", result, file_name="resume.md")
