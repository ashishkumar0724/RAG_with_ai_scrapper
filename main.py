import os
import streamlit as st
from pdf_handler import upload_pdf, load_pdf, split_text, index_docs, retrieve_docs, answer_question
from url_handler import load_page, split_text as url_split_text, index_docs as url_index_docs, retrieve_docs as url_retrieve_docs, answer_question as url_answer_question
import uuid
from utils import generate_session_id

# Set page configuration FIRST
st.set_page_config(page_title="Chat with PDF", page_icon="📚", layout="wide")

# Set the Streamlit theme to black
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #161a21;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "sessions" not in st.session_state:
    st.session_state.sessions = {}  # Stores chat history for each session
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Sidebar Navigation
with st.sidebar:
    st.title("📚 Chat with PDF")

    # Option to create a new session
    if st.button("Create New Session"):
        session_id = generate_session_id()
        st.session_state.current_session_id = session_id
        st.session_state.sessions[session_id] = {"chat_history": []}
        st.rerun()

    # Display existing sessions
    st.subheader("Sessions")
    for session_id in st.session_state.sessions.keys():
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"Session: {session_id}", key=f"session_{session_id}"):
                st.session_state.current_session_id = session_id
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{session_id}"):
                del st.session_state.sessions[session_id]
                if st.session_state.current_session_id == session_id:
                    st.session_state.current_session_id = None
                st.rerun()

    # Toggle Chat History Visibility
    if st.button("Toggle Chat History"):
        st.session_state.show_chat_history = not st.session_state.get("show_chat_history", False)

    # Upload PDF file
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type="pdf",
        accept_multiple_files=False
    )

    if uploaded_file:
        with st.spinner("Uploading and processing the PDF..."):
            upload_pdf(uploaded_file)
            file_path = os.path.join("chat-with-pdf/pdfs/", uploaded_file.name)
            documents = load_pdf(file_path)
            chunked_documents = split_text(documents)
            index_docs(chunked_documents)
        st.success("PDF processed successfully!")

    # Enter URL
    url = st.text_input("Enter URL:")
    if url:
        with st.spinner("Loading and indexing page content..."):
            documents = load_page(url)
            chunked_documents = url_split_text(documents)
            url_index_docs(chunked_documents)
        st.success("Page indexed!")

# Add a title and description
st.title("📚 Chat with PDF")
st.markdown("""
Welcome to **Chat with PDF**! Upload a PDF or enter a URL to ask questions about its content. The app uses advanced AI models to provide answers based on the document's context.
""")

# Display Current Session ID
if st.session_state.current_session_id:
    st.subheader(f"Current Session ID: {st.session_state.current_session_id}")
else:
    st.info("No active session. Create a new session from the sidebar.")

# Chat input and response handling
question = st.chat_input("Ask a question:")

if question:
    try:
        # Ensure a valid session exists; if not, create one automatically
        if (
            not st.session_state.current_session_id
            or st.session_state.current_session_id not in st.session_state.sessions
        ):
            st.session_state.current_session_id = generate_session_id()
            st.session_state.sessions[st.session_state.current_session_id] = {"chat_history": []}

        current_session = st.session_state.sessions[st.session_state.current_session_id]

        # Save the question to chat history
        current_session["chat_history"].append({"role": "user", "message": question})
        st.chat_message("user").write(question)

        # Retrieve relevant documents and generate the answer
        with st.status("Retrieving relevant information and generating the answer...", expanded=True) as status:
            if uploaded_file:
                related_documents = retrieve_docs(question)
                answer = answer_question(question, "\n\n".join([doc.page_content for doc in related_documents]))
            elif url:
                related_documents = url_retrieve_docs(question)
                answer = url_answer_question(question, "\n\n".join([doc.page_content for doc in related_documents]))
            else:
                answer = "Please upload a PDF or enter a URL first."
            status.update(label="Answer generated!", state="complete", expanded=False)

        # Save the answer to chat history
        current_session["chat_history"].append({"role": "assistant", "message": answer})
        st.chat_message("assistant").write(answer)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Display Chat History (only if toggled in the sidebar)
if st.session_state.get("show_chat_history", False):
    st.subheader("Chat History")
    if st.session_state.current_session_id:
        current_session = st.session_state.sessions[st.session_state.current_session_id]
        chat_history = current_session["chat_history"]
        if chat_history:
            for entry in chat_history:
                role = entry["role"].capitalize()
                message = entry["message"]
                st.markdown(f"**{role}:** {message}")
        else:
            st.info("No chat history available for this session.")
    else:
        st.info("No active session. Create a new session from the sidebar.")