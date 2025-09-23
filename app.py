import streamlit as st 
import sqlite3

conn = sqlite3.connect("papers.db")
cur = conn.cursor()

# Create tables if not exist
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    faculty_id INTEGER,
    file_path TEXT,
    report_path TEXT,
    status TEXT,
    next_role TEXT
)
""")
conn.commit()

# Initialize navigation page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar Navigation
with st.sidebar:
    st.title("Navigation")
    if st.button("🏠 Home"):
        st.session_state.page = "home"
    if st.button("🔐 Login"):
        st.session_state.page = "login"
    if st.button("📝 Register"):
        st.session_state.page = "register"
    if "user" in st.session_state and st.session_state.get("page") == "dashboard":
        if st.button("📊 Dashboard"):
            st.session_state.page = "dashboard"
    if "user" in st.session_state:
        if st.button("🚪 Logout"):
            st.session_state.pop("user")
            st.session_state.page = "login"
            st.rerun()

# ------ Pages ------

# Home Page
if st.session_state.page == "home":
    st.title("Welcome to the Research Paper Management System")
    st.write("Use the sidebar to navigate to Login or Register.")

# Registration Page
elif st.session_state.page == "register":
    st.title("Registration")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["faculty", "hod", "dean", "principal"])
    
    if st.button("Register"):
        try:
            cur.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)", 
                        (name,email,password,role))
            conn.commit()
            st.success("Registration successful! Please login.")
            st.session_state.page = "login"
            st.rerun()
        except sqlite3.IntegrityError:
            st.error("Email already registered.")

    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

# Login Page
elif st.session_state.page == "login":
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = cur.fetchone()
        if user:
            st.session_state.user = user
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials")
    
    if st.button("New user? Register here"):
        st.session_state.page = "register"
        st.rerun()

# Dashboard Page
elif st.session_state.page == "dashboard":
    if "user" not in st.session_state:
        st.warning("Please login first.")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()
    else:
        user = st.session_state.user
        st.title(f"Welcome, {user[1]} ({user[4]})")

        if user[4] == "faculty":
            st.subheader("Upload Research Paper")
            title = st.text_input("Paper Title")
            paper = st.file_uploader("Upload Paper (PDF)", type="pdf")
            report = st.file_uploader("Upload Plagiarism Report (PDF)", type="pdf")
            if st.button("Submit Paper"):
                if paper and report and title:
                    with open(paper.name, "wb") as f:
                        f.write(paper.getbuffer())
                    with open(report.name, "wb") as f:
                        f.write(report.getbuffer())
                    cur.execute("INSERT INTO papers (title,faculty_id,file_path,report_path,status,next_role) VALUES (?,?,?,?,?,?)",
                                (title,user[0],paper.name,report.name,"in_progress","hod"))
                    conn.commit()
                    st.success("Paper submitted successfully!")
                else:
                    st.warning("Please fill in all fields and upload both files.")

        else:
            role = user[4]
            st.subheader(f"{role.upper()} Review Dashboard")

            cur.execute("""
                SELECT p.id, p.title, u.name, p.file_path, p.report_path 
                FROM papers p JOIN users u ON p.faculty_id = u.id 
                WHERE p.next_role=? AND p.status='in_progress'""", (role,))
            papers = cur.fetchall()

            if papers:
                for pid, title, faculty_name, fpath, rpath in papers:
                    st.markdown(f"### {title}")
                    st.write(f"Submitted by: {faculty_name}")

                    with open(fpath, "rb") as pf:
                        st.download_button("Download Paper", pf, file_name=title + ".pdf", key=f"download_paper_{pid}")
                    with open(rpath, "rb") as rf:
                        st.download_button("Download Plagiarism Report", rf, file_name="report.pdf", key=f"download_report_{pid}")

                    col1, col2 = st.columns(2)
                    if col1.button("✅ Accept", key=f"accept_{pid}"):
                        next_role = None
                        if role == "hod":
                            next_role = "dean"
                        elif role == "dean":
                            next_role = "principal"
                        elif role == "principal":
                            next_role = None  # Final approval

                        if next_role:
                            cur.execute("UPDATE papers SET status='in_progress', next_role=? WHERE id=?", (next_role, pid))
                        else:
                            cur.execute("UPDATE papers SET status='accepted', next_role=NULL WHERE id=?", (pid,))
                        conn.commit()
                        st.success(f"Paper forwarded to {next_role if next_role else 'final approval'}")
                        st.rerun()

                    if col2.button("❌ Reject", key=f"reject_{pid}"):
                        cur.execute("UPDATE papers SET status='rejected', next_role='faculty' WHERE id=?", (pid,))
                        conn.commit()
                        st.error("Paper rejected and sent back to faculty")
                        st.rerun()

                    st.markdown("---")
            else:
                st.info("No pending papers for review.")
