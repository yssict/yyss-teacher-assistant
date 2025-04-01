import streamlit as st

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Sidebar for teacher controls
with st.sidebar:
    st.title("Teacher Controls")
    uploaded_file = st.file_uploader("Upload Reference Document", type=['txt', 'pdf'])
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")
    
    # Teacher mode toggle
    is_teacher = st.checkbox("Teacher Mode")

# Main chat interface
st.title("YYSS Teacher Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "documents" not in st.session_state:
    st.session_state.documents = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me a question"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Bot response
    response = "I am a chatbot. Once documents are uploaded, I will be able to answer based on them!"
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)

# Show uploaded documents (only in teacher mode)
if is_teacher:
    st.sidebar.subheader("Uploaded Documents")
    for doc in st.session_state.documents:
        st.sidebar.text(doc)
