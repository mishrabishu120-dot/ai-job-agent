from agents import analyze_resume, match_jobs_with_ai, generate_cover_letter_ai
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# 📄 Read resume PDF
def read_resume(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    return text


# 📊 Load jobs CSV
def load_jobs():
    return pd.read_csv("jobs.csv")


# 🎯 Skill matching logic
def match_score(resume, skills):
    score = 0
    for skill in skills.split():
        if skill.lower() in resume.lower():
            score += 1
    return score


# 🚀 MAIN FUNCTION
def main():
    print("\n🔹 Starting AI Job Agent...\n")

    # Step 1: Read resume
    resume = read_resume("resume.pdf")

    # Step 2: Load jobs
    jobs = load_jobs()

    # Step 3: Match jobs
    jobs["score"] = jobs["skills"].apply(lambda x: match_score(resume, x))
    top_jobs = jobs.sort_values(by="score", ascending=False).head(3)

    print("Top Matching Jobs:\n")
    print(top_jobs[["job_title", "company", "score"]])

    # Step 4: Resume Analysis
    print("\n--- Resume Analysis ---\n")
    analysis = analyze_resume(resume)
    print(analysis)

    # Step 5: AI Job Matching
    print("\n--- AI Job Matching ---\n")
    ai_match = match_jobs_with_ai(jobs, resume)
    print(ai_match)

    # Step 6: Generate Cover Letters
    print("\n--- Generating Cover Letters ---\n")

    for _, job in top_jobs.iterrows():
        print(f"\nProcessing: {job['job_title']} at {job['company']}")

        letter = generate_cover_letter_ai(job, resume)

        file_name = f"cover_letter_{job['job_title'].replace(' ', '_')}.txt"

        with open(file_name, "w") as f:
            f.write(letter)

        print(f"Saved: {file_name}")


# ▶️ Run
if __name__ == "__main__":
    main()
    