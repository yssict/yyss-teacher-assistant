import streamlit as st
import PyPDF2
import docx
import requests
import json

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# Hugging Face API setup
API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
try:
    headers = {"Authorization": f"Bearer {st.secrets['huggingface']['api_token']}"}
except:
    st.error("Hugging Face API token not found. Please configure in Streamlit Cloud settings.")
    headers = {}

def query_model(payload):
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_ai_response(prompt, context=None):
    # Fallback responses for common questions
    fallback_responses = {
        "geography": """Geography is the study of places, people, and the relationships between them. It includes:
- Physical geography (landforms, climate, natural resources)
- Human geography (populations, cultures, economics)
- Environmental geography (how humans interact with nature)
Geography helps us understand our world and make informed decisions about environmental and social issues.""",
        
        "smart": """I am an AI assistant designed to help students and teachers. I can:
- Answer questions about various subjects
- Help explain complex topics
- Assist with document understanding
- Engage in educational discussions

How can I help you learn today?""",
        
        "math": """Mathematics is a fundamental subject that includes:
- Numbers and operations
- Algebra and functions
- Geometry and measurement
- Statistics and probability
What specific area of mathematics would you like to explore?""",

        "science": """Science encompasses several major fields:
- Biology (study of living things)
- Chemistry (study of matter and its changes)
- Physics (study of energy and forces)
- Earth Science (study of our planet)
Which area interests you most?"""
    }

    try:
        if context:
            full_prompt = f"Context: {context[:500]}...\n\nQuestion: {prompt}\nProvide a detailed, educational response suitable for secondary school students."
        else:
            full_prompt = f"Question: {prompt}\nProvide a detailed, educational response suitable for secondary school students."
        
        # Check for fallback responses first
        for key, response in fallback_responses.items():
            if key in prompt.lower():
                return response

        response = query_model({
            "inputs": full_prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "top_p": 0.9
            }
        })
        
        if response and isinstance(response, list) and len(response) > 0:
            return response[0]['generated_text']
        else:
            return "I apologize for the technical difficulty. Let me provide a general response: What specific aspect of this topic would you like to learn more about?"
            
    except Exception as e:
        return "I'm here to help! Could you please specify what aspect you'd like to learn about?"

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
