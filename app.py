import streamlit as st
from rag_pipeline import create_vectorstore, ask

st.set_page_config(page_title="Chatbot", layout="wide")

# =========================
# CSS 
# =========================
st.markdown("""
<style>

/* App Background */
.stApp {
    background-color: #f3f6fb;
}

/* Left Panel */
[data-testid="column"]:first-child {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 16px;
    height: 92vh;
    border: 1px solid #e2e8f0;
}

/* Right Panel */
[data-testid="column"]:nth-child(2) {
    background-color: #ffffff;
    padding: 25px;
    border-radius: 16px;
    height: 92vh;
    border: 1px solid #e2e8f0;
}

/* Buttons */
.stButton button {
    width: 100%;
    border-radius: 10px;
    height: 42px;
    font-weight: 600;
    background-color: #2563eb;
    color: white;
    border: none;
}

.stButton button:hover {
    background-color: #1d4ed8;
}

/* File Upload Box */
[data-testid="stFileUploader"] {
    background-color: #f8fafc;
    padding: 18px;
    border-radius: 14px;
    border: 2px dashed #cbd5e1;
}

/* Chat Layout */
.chat-row {
    display: flex;
    margin-bottom: 14px;
}

/* User Message */
.chat-user {
    justify-content: flex-end;
}

.chat-bubble-user {
    background-color: #2563eb;
    color: white;
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 70%;
    font-size: 15px;
}

/* Bot Message */
.chat-bot {
    justify-content: flex-start;
}

.chat-bubble-bot {
    background-color: #eef2f7;
    color: #0f172a;
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 70%;
    font-size: 15px;
    border: 1px solid #e2e8f0;
}

</style>
""", unsafe_allow_html=True)

# =========================
# SESSION STATE
# =========================
if "db" not in st.session_state:
    st.session_state.db = None

if "chat" not in st.session_state:
    st.session_state.chat = []

# =========================
# LAYOUT
# =========================
left, right = st.columns([1, 2])

# =========================
# LEFT PANEL (UPLOAD)
# =========================
with left:

    st.markdown("## Institute document")
    st.caption("Upload excel file and click Process")

    file = st.file_uploader(
        "Upload",
        type=["xlsx"],
        label_visibility="collapsed"
    )

    st.caption("Limit 200MB per file • XLSX")

    if file and st.button("Process"):
        with st.spinner("Processing..."):
            st.session_state.db = create_vectorstore(file)
        st.success("File processed")

    # if st.button("Load Existing Data"):
    #     st.session_state.db = load_vectorstore()
    #     st.success("Existing data loaded")

# =========================
# RIGHT PANEL (CHAT)
# =========================
with right:

    st.markdown("###  ChatBot")

    chat_box = st.container(height=650)

    with chat_box:
        for role, msg in st.session_state.chat:

            if role == "user":
                st.markdown(
                    f"""
                    <div class="chat-row chat-user">
                        <div class="chat-bubble-user">{msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="chat-row chat-bot">
                        <div class="chat-bubble-bot">{msg}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if st.session_state.db:
        q = st.chat_input("Ask something...")

        if q:
            ans = ask(st.session_state.db, q)
            st.session_state.chat.append(("user", q))
            st.session_state.chat.append(("assistant", ans))
            st.rerun()
    else:
        st.info("Upload file or load data to start chatting.")
