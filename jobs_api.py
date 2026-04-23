from dotenv import load_dotenv
import os
import requests
import streamlit as st

# ---------------- LOAD ENV ----------------
load_dotenv()

def get_secret(key):
    try:
        return st.secrets[key]   # deployed
    except:
        return os.getenv(key)    # local


API_KEY = get_secret("RAPIDAPI_KEY")
if not API_KEY:
    raise ValueError("❌ RAPIDAPI_KEY not found. Check .env or Streamlit secrets.")


def fetch_jobs(query="software developer", location="India"):
    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    queries = [
        f"{query} in {location}",
        f"{query} fresher {location}",
        f"{query} intern {location}"
    ]

    jobs = []

    try:
        for q in queries:
            params = {
                "query": q,
                "page": "1",
                "num_pages": "2"
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()

            for job in data.get("data", []):

                apply_link = job.get("job_apply_link") or job.get("job_google_link")

                jobs.append({
                    "job_title": clean_text(job.get("job_title")),
                    "company": clean_text(job.get("employer_name")),
                    "skills": clean_text(job.get("job_description"))[:300],
                    "logo": job.get("employer_logo") or f"https://logo.clearbit.com/{job.get('employer_website', '')}",
                    "apply_link": apply_link or f"https://www.google.com/search?q={job.get('job_title')}+{job.get('employer_name')}+apply"
                })

        # 🔥 ADD REMOTIVE JOBS
        jobs += fetch_remotive_jobs(query)

        # 🚫 REMOVE DUPLICATES (STRONGER)
        unique_jobs = {}
        for job in jobs:
            key = f"{job['job_title']}_{job['company']}".lower()
            if key not in unique_jobs:
                unique_jobs[key] = job

        jobs = list(unique_jobs.values())

        # LIMIT
        jobs = jobs[:50]

        return jobs if jobs else get_dummy_jobs()

    except Exception as e:
        print("API Error:", e)
        return get_dummy_jobs()


# 🌐 REMOTIVE API
def fetch_remotive_jobs(query):
    try:
        url = "https://remotive.com/api/remote-jobs"
        data = requests.get(url, timeout=10).json()

        jobs = []

        for job in data.get("jobs", [])[:10]:
            jobs.append({
                "job_title": clean_text(job.get("title")),
                "company": clean_text(job.get("company_name")),
                "skills": clean_text(job.get("description"))[:200],
                "logo": job.get("company_logo"),
                "apply_link": job.get("url")
            })

        return jobs

    except:
        return []


# 🧼 CLEAN TEXT FUNCTION (VERY IMPORTANT)
def clean_text(text):
    if not text:
        return "N/A"
    return str(text).replace("\n", " ").strip()


# 🔁 FALLBACK
def get_dummy_jobs():
    return [
        {
            "job_title": "Software Developer",
            "company": "Google",
            "skills": "Python SQL APIs Problem Solving",
            "logo": "https://logo.clearbit.com/google.com",
            "apply_link": "https://careers.google.com"
        },
        {
            "job_title": "Backend Engineer",
            "company": "Amazon",
            "skills": "Django AWS REST APIs",
            "logo": "https://logo.clearbit.com/amazon.com",
            "apply_link": "https://amazon.jobs"
        }
    ]