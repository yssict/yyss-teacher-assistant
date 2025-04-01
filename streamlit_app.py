import streamlit as st
import PyPDF2
import docx
import requests

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# AI Model setup - using a different model
API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
headers = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"}

def get_ai_response(prompt, context=None):
    try:
        if context:
            full_prompt = f"""Instructions: You are a helpful teaching assistant. Using the provided context, give a clear and educational answer.
            Context: {context[:500]}
            Question: {prompt}
            Answer:"""
        else:
            full_prompt = f"""Instructions: You are a helpful teaching assistant. Give a clear and educational answer.
            Question: {prompt}
            Answer:"""
            
        response = requests.post(
            API_URL, 
            headers=headers, 
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "do_sample": True
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['generated_text']
            else:
                return "I apologize, but I couldn't generate a proper response. Please try again."
        else:
            return f"Error {response.status_code}: The service is temporarily unavailable. Please try again in a moment."
            
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again."

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def read_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

# Sidebar for teacher controls
with st.sidebar:
    st.title("Teacher Controls")
    uploaded_file = st.file_uploader("Upload Reference Document", type=['txt', 'pdf', 'docx'])
    if uploaded_file:
        try:
            # Process different file types
            if uploaded_file.type == "text/plain":
                content = uploaded_file.getvalue().decode()
            elif uploaded_file.type == "application/pdf":
                content = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                content = read_docx(uploaded_file)
            
            st.session_state.document_content = content
            st.session_state.doc_name = uploaded_file.name
            st.success(f"Uploaded and processed: {uploaded_file.name}")
            st.write("Document Preview:")
            st.write(content[:200] + "...")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

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
    
    # Get AI response
    with st.spinner("Thinking..."):  # Added loading indicator
        if st.session_state.document_content:
            response = get_ai_response(prompt, st.session_state.document_content)
        else:
            response = get_ai_response(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

# Add a reset button in the sidebar
with st.sidebar:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
