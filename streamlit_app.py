import streamlit as st

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""

# Sidebar for teacher controls
with st.sidebar:
    st.title("Teacher Controls")
    uploaded_file = st.file_uploader("Upload Reference Document", type=['txt'])
    if uploaded_file:
        # Read and store the document content
        content = uploaded_file.getvalue().decode()
        st.session_state.document_content = content
        st.success(f"Uploaded and processed: {uploaded_file.name}")
        st.write("Document Preview:")
        st.write(content[:200] + "...")  # Show first 200 characters

# Main chat interface
st.title("YYSS Teacher Assistant")

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
    if st.session_state.document_content:
        if "uploaded" in prompt.lower():
            response = f"Yes, I have a document uploaded. Here's a preview of its content:\n\n{st.session_state.document_content[:200]}..."
        else:
            response = f"I can help answer questions based on the uploaded document. Try asking specific questions about its content!"
    else:
        response = "Please upload a document first. I can then answer questions based on its content."
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
