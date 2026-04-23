from dotenv import load_dotenv
import os
import streamlit as st
from groq import Groq

# ---------------- SETUP ----------------
load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]   # deployed
    except:
        return os.getenv(key)    # local

client = Groq(api_key=get_secret("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"


# ---------------- HELPER ----------------
def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"


# 🧠 RESUME ANALYZER
def analyze_resume(resume_text):
    prompt = f"""
You are an expert resume analyst.

Return output in this format:

### Skills
- ...

### Experience Level
...

### Strengths
- ...

### Improvements
- ...

Resume:
{resume_text}
"""
    return call_llm(prompt)


# 🔍 JOB MATCHER (SMARTER)
def match_jobs_with_ai(jobs, resume):
    prompt = f"""
You are a job matching AI.

Analyze and return:

### Top Matching Roles
- Job Title → Reason

### Best Career Fit
...

### Suggestions
- ...

Resume:
{resume}

Jobs:
{jobs.head(10).to_string()}
"""
    return call_llm(prompt)


# ✍️ COVER LETTER (UPGRADED)
def generate_cover_letter_ai(job, resume):
    prompt = f"""
Write a strong, personalized cover letter.

Rules:
- Max 200 words
- No generic phrases
- Direct and impactful
- Tailored to job

Job Title: {job['job_title']}
Company: {job['company']}

Resume:
{resume}
"""
    return call_llm(prompt)


# 🧠 SKILL GAP ANALYSIS (BETTER)
def skill_gap_analysis(job, resume):
    prompt = f"""
You are a career coach.

Return output in this format:

### Missing Skills
- ...

### Learning Plan
- ...

### Quick Improvements
- ...

Job:
{job}

Resume:
{resume}
"""
    return call_llm(prompt)


# 🚀 RESUME IMPROVER (VERY STRONG)
def improve_resume_ai(resume_text):
    prompt = f"""
You are a senior recruiter.

Return:

### Weak Points
- ...

### Missing Skills
- ...

### Improvements
- ...

### Better Resume Lines
- Before → After

Resume:
{resume_text}
"""
    return call_llm(prompt)