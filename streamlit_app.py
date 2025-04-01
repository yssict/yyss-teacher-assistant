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

# AI Model setup - using a simpler, more reliable model
API_URL = "https://api-inference.huggingface.co/models/facebook/opt-350m"
headers = {"Authorization": f"Bearer {st.secrets['HUGGINGFACE_API_KEY']}"}

def get_ai_response(prompt, context=None):
    try:
        if context:
            full_prompt = f"""Based on this context: {context[:500]}
            Answer this question: {prompt}"""
        else:
            full_prompt = f"""As a helpful teaching assistant, answer this: {prompt}"""
            
        response = requests.post(
            API_URL, 
            headers=headers, 
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_length": 100,
                    "return_full_text": False
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0]['generated_text'].strip()
            return "I couldn't generate a response. Please try again."
        else:
            return f"Error: Please try again. (Status: {response.status_code})"
            
    except Exception as e:
        return f"Error: {str(e)}"

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

# Main chat interface
st.title("YYSS Teacher Assistant")

# Sidebar
with st.sidebar:
    st.title("Teacher Controls")
    uploaded_file = st.file_uploader("Upload Reference Document", type=['txt', 'pdf', 'docx'])
    if uploaded_file:
        try:
            if uploaded_file.type == "text/plain":
                content = uploaded_file.getvalue().decode()
            elif uploaded_file.type == "application/pdf":
                content = read_pdf(uploaded_file)
            else:
                content = read_docx(uploaded_file)
            
            st.session_state.document_content = content
            st.success("Document processed!")
            st.write("Preview:")
            st.write(content[:200] + "...")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.spinner("Thinking..."):
        response = get_ai_response(prompt, st.session_state.document_content if st.session_state.document_content else None)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)
