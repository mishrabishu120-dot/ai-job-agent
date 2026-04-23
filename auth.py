import streamlit as st

def login():
    if "user" not in st.session_state:
        st.session_state.user = None

    if not st.session_state.user:
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

        return False

    return True