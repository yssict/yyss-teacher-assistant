import streamlit as st
import PyPDF2
import docx
import io
from transformers import pipeline
import torch

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Initialize the model (this will download a small model first time)
@st.cache_resource
def load_model():
    try:
        qa_pipeline = pipeline(
            "question-answering",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        chat_pipeline = pipeline(
            "text-generation",
            model="facebook/blenderbot-400M-distill",
            device=0 if torch.cuda.is_available() else -1
        )
        return qa_pipeline, chat_pipeline
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

qa_pipeline, chat_pipeline = load_model()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def get_ai_response(prompt, doc_content=None):
    try:
        if doc_content and qa_pipeline:
            # Try to answer from document first
            answer = qa_pipeline(
                question=prompt,
                context=doc_content[:512]  # Limited context window
            )
            if answer['score'] > 0.1:  # Confidence threshold
                return answer['answer']
        
        # Fall back to general chat if no good document answer
        if chat_pipeline:
            response = chat_pipeline(
                prompt,
                max_length=100,
                num_return_sequences=1
            )[0]['generated_text']
            return response
        
    except Exception as e:
        return f"I encountered an error: {str(e)}. Could you rephrase your question?"

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
    response = get_ai_response(prompt, st.session_state.document_content)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)

# Add requirements to requirements.txt:
# transformers
# torch
# sentencepiece
