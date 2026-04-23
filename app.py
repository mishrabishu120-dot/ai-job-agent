import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import os

load_dotenv()

from jobs_api import fetch_jobs
from agents import (
    analyze_resume,
    generate_cover_letter_ai,
    skill_gap_analysis,
    match_jobs_with_ai
)
from database import (
    create_table, create_user, verify_user, login_user,
    generate_otp, save_otp, verify_otp, reset_password,
    get_user_role, post_job, get_recruiter_jobs,
    make_recruiter, get_all_users, get_all_jobs, delete_any_job
)
from email_utils import send_otp_email

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Job Assistant", layout="wide")
create_table()

# ---------------- SESSION ----------------
defaults = {
    "user": None,
    "role": "user",
    "jobs": [],
    "resume": "",
    "selected_job": None,
    "saved_jobs": [],
    "otp_email": None,
    "otp_mode": False,
    "reset_mode": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
.card {
    background:#1e293b;
    padding:15px;
    border-radius:10px;
    margin-bottom:10px;
}
.badge {
    background:#0ea5e9;
    padding:4px 8px;
    border-radius:5px;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if not st.session_state.user:

    st.title("🚀 AI Job Assistant")

    mode = st.radio("", ["Login", "Signup"], horizontal=True)

    # -------- SIGNUP --------
    if mode == "Signup":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Create Account"):
            res = create_user(email, password)

            if res == "success":
                otp = generate_otp()
                save_otp(email, otp)
                send_otp_email(email, otp)

                st.session_state.otp_email = email
                st.session_state.otp_mode = True
                st.success("OTP sent")

        if st.session_state.otp_mode:
            otp = st.text_input("Enter OTP")

            if st.button("Verify OTP"):
                if verify_otp(st.session_state.otp_email, otp):
                    verify_user(st.session_state.otp_email)
                    st.success("Signup successful")
                    st.session_state.otp_mode = False

    # -------- LOGIN --------
    if mode == "Login":

        if not st.session_state.reset_mode:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                res = login_user(email, password)

                if res == "success":
                    st.session_state.user = email

                    # ✅ ROLE ADDED HERE
                    st.session_state.role = get_user_role(email)

                    st.rerun()
                else:
                    st.error(res)

            if st.button("Forgot Password"):
                st.session_state.reset_mode = True

        else:
            email = st.text_input("Email")

            if st.button("Send OTP"):
                otp = generate_otp()
                save_otp(email, otp)
                send_otp_email(email, otp)
                st.success("OTP sent")

            otp = st.text_input("OTP")
            new_pass = st.text_input("New Password", type="password")

            if st.button("Reset Password"):
                if verify_otp(email, otp):
                    reset_password(email, new_pass)
                    st.success("Password updated")
                    st.session_state.reset_mode = False

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.write(f"Welcome {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

uploaded_file = st.sidebar.file_uploader("Upload Resume", type="pdf")
role = st.sidebar.selectbox("Role", ["Software Developer", "Data Analyst"])
location = st.sidebar.selectbox("Location", ["India", "USA"])

# ---------------- RUN ANALYSIS ----------------
if st.sidebar.button("Run Analysis"):

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        text = "".join([p.extract_text() or "" for p in reader.pages])
        st.session_state.resume = text

    jobs = fetch_jobs(role, location)
    st.session_state.jobs = jobs

# ---------------- TABS ----------------
tabs = ["📊 Resume AI", "💼 Jobs", "⭐ Saved Jobs", "🏢 Recruiter"]

is_admin = st.session_state.role == "admin"

if is_admin:
    tabs.append("🛠 Admin")

tab_objects = st.tabs(tabs)

tab1, tab2, tab3, tab4 = tab_objects[:4]

if is_admin:
    tab5 = tab_objects[4]

# -------- TAB 1 --------
with tab1:
    if st.session_state.resume:
        st.markdown("### Resume Analysis")
        st.markdown(analyze_resume(st.session_state.resume))

        if st.session_state.jobs:
            df = pd.DataFrame(st.session_state.jobs)
            st.markdown("### Best Matches")
            st.write(match_jobs_with_ai(df, st.session_state.resume))
    else:
        st.info("Upload resume and run analysis")

# -------- TAB 2 --------
with tab2:

    jobs = st.session_state.jobs

    if jobs:
        df = pd.DataFrame(jobs)

        search = st.text_input("Search jobs")

        if search:
            df = df[
                df["job_title"].str.contains(search, case=False) |
                df["company"].str.contains(search, case=False)
            ]

        cols = st.columns(2)

        for i, job in df.iterrows():
            with cols[i % 2]:

                logo = job.get("logo") or "https://via.placeholder.com/50"

                st.markdown(f"""
                <div class="card">
                    <img src="{logo}" width="40">
                    <b>{job['job_title']}</b><br>
                    {job['company']}<br>
                    <span class="badge">Top Match</span>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)

                if c1.button("View", key=f"v{i}"):
                    st.session_state.selected_job = job.to_dict()

                if c2.button("Save ⭐", key=f"s{i}"):
                    st.session_state.saved_jobs.append(job.to_dict())

                if c3.button("Cover Letter", key=f"c{i}"):
                    st.write(generate_cover_letter_ai(job, st.session_state.resume))

        if st.session_state.selected_job:
            job = st.session_state.selected_job

            st.markdown("---")
            st.subheader(job["job_title"])
            st.write(job["company"])

            st.markdown("### Skill Gap")
            st.write(skill_gap_analysis(job, st.session_state.resume))

            st.link_button(
                "Apply",
                f"https://google.com/search?q={job['job_title']} {job['company']}"
            )

    else:
        st.info("Run analysis to load jobs")

# -------- TAB 3 --------
with tab3:
    if st.session_state.saved_jobs:
        for job in st.session_state.saved_jobs:
            st.write(f"{job['job_title']} - {job['company']}")
    else:
        st.info("No saved jobs yet")

# -------- TAB 4 (RECRUITER) --------
with tab4:

    if st.session_state.role not in ["recruiter", "admin"]:
        st.warning("Recruiter access only")
        st.stop()

    st.header("🏢 Recruiter Dashboard")

    # ---- POST JOB ----
    st.subheader("➕ Post New Job")

    title = st.text_input("Job Title")
    company = st.text_input("Company")
    desc = st.text_area("Description")

    if st.button("Post Job"):
        post_job(title, company, desc, st.session_state.user)
        st.success("✅ Job posted!")
        st.rerun()

    st.markdown("---")

    # ---- VIEW JOBS ----
    st.subheader("💼 Your Job Listings")

    jobs = get_recruiter_jobs(st.session_state.user)

    if not jobs:
        st.info("No jobs posted yet.")
    else:
        for i, job in enumerate(jobs):
            title_j, company_j, desc_j = job

            # 🎨 Premium Card
            st.markdown(f"""
            <div style="
                padding:18px;
                border-radius:14px;
                background: rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.08);
                margin-bottom:12px;
            ">
                <h4 style="margin-bottom:4px;">{title_j}</h4>
                <p style="margin:0; color:#9aa4b2;">{company_j}</p>
                <p style="margin-top:10px; font-size:14px;">
                    {desc_j[:140]}...
                </p>
                <span style="
                    font-size:12px;
                    background:#1f6feb;
                    padding:4px 10px;
                    border-radius:20px;
                ">Active</span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            # 👁 VIEW
            with col1:
                if st.button("View", key=f"view_job_{i}"):
                    st.session_state.selected_recruiter_job = job

            # 🗑 DELETE (SAFE)
            with col2:
                if st.button("Delete", key=f"delete_job_{i}"):
                    st.session_state[f"confirm_delete_{i}"] = True

            # 🔴 CONFIRM DELETE
            if st.session_state.get(f"confirm_delete_{i}", False):
                st.warning("Are you sure you want to delete this job?")

                c1, c2 = st.columns(2)

                with c1:
                    if st.button("Yes, delete", key=f"yes_{i}"):
                        from database import delete_job
                        delete_job(title_j, st.session_state.user)
                        st.success("🗑 Job deleted")
                        st.session_state[f"confirm_delete_{i}"] = False
                        st.rerun()

                with c2:
                    if st.button("Cancel", key=f"cancel_{i}"):
                        st.session_state[f"confirm_delete_{i}"] = False

    # ---- JOB DETAILS PANEL ----
    if st.session_state.get("selected_recruiter_job"):
        title_j, company_j, desc_j = st.session_state.selected_recruiter_job

        st.markdown("---")
        st.subheader("📄 Job Details")

        st.markdown(f"""
        <div style="
            padding:20px;
            border-radius:14px;
            background: rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.1);
        ">
            <h3>{title_j}</h3>
            <p style="color:#9aa4b2;">{company_j}</p>
            <p style="margin-top:12px;">{desc_j}</p>
        </div>
        """, unsafe_allow_html=True)
  # -------- TAB 5 (ADMIN) --------
if is_admin:
    with tab5:

        st.header("🛠 Admin Dashboard")

        # 📊 STATS
        users = get_all_users()
        jobs = get_all_jobs()

        total_users = len(users)
        total_jobs = len(jobs)
        recruiters = len([u for u in users if u[1] == "recruiter"])

        col1, col2, col3 = st.columns(3)

        col1.metric("👥 Users", total_users)
        col2.metric("💼 Jobs", total_jobs)
        col3.metric("🏢 Recruiters", recruiters)

st.markdown("---")

admin_tab1, admin_tab2 = st.tabs(["👥 Users", "💼 Jobs"])

        # ================= USERS =================
with admin_tab1:

            st.subheader("Manage Users")

            if not users:
                st.warning("No users found")

            for i, (email, role) in enumerate(users):

                st.markdown(f"""
                <div style="
                    padding:15px;
                    border-radius:12px;
                    background: rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.08);
                    margin-bottom:10px;
                ">
                    <b>{email}</b><br>
                    Role: <span style="color:#38bdf8;">{role}</span>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns([2,1])

                if role != "admin":
                    with c2:
                        if st.button("Promote to Recruiter", key=f"promote_{i}"):
                            make_recruiter(email)
                            st.success(f"{email} is now recruiter")
                            st.rerun()

        # ================= JOBS =================
with admin_tab2:

            st.subheader("All Jobs")

            if not jobs:
                st.warning("No jobs found")

            for i, job in enumerate(jobs):
                title, company, desc, posted_by = job

                st.markdown(f"""
                <div style="
                    padding:18px;
                    border-radius:14px;
                    background: rgba(255,255,255,0.04);
                    border:1px solid rgba(255,255,255,0.08);
                    margin-bottom:12px;
                ">
                    <h4 style="margin-bottom:4px;">{title}</h4>
                    <p style="margin:0; color:#9aa4b2;">{company}</p>
                    <p style="margin-top:8px;">👤 {posted_by}</p>
                    <p style="font-size:14px;">
                        {desc[:120]}...
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([1,1])

                with col2:
                    if st.button("🗑 Delete", key=f"admin_delete_{i}"):
                        delete_any_job(title)
                        st.success("Job deleted")
                        st.rerun()