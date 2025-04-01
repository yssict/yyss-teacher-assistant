import streamlit as st
import PyPDF2
import docx
import io
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

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

def preprocess_text(text):
    # Tokenize into sentences
    sentences = sent_tokenize(text)
    return sentences

def find_relevant_content(query, content):
    # Preprocess query
    query = query.lower()
    query_words = set(word_tokenize(query)) - set(stopwords.words('english')) - set(string.punctuation)
    
    # Preprocess content
    sentences = preprocess_text(content)
    
    # Find relevant sentences
    relevant_sentences = []
    for sentence in sentences:
        sentence_words = set(word_tokenize(sentence.lower()))
        # If any query word is in the sentence
        if query_words & sentence_words:
            relevant_sentences.append(sentence)
    
    return relevant_sentences

def get_response(prompt, doc_content, doc_name):
    prompt_lower = prompt.lower()
    
    # Document-specific queries
    if doc_content:
        # If asking about the uploaded document
        if any(word in prompt_lower for word in ['document', 'uploaded', 'file']):
            return f"I have the document '{doc_name}' uploaded. It contains information about {doc_content[:100]}... What would you like to know about it?"
        
        # Find relevant content from document
        relevant_content = find_relevant_content(prompt, doc_content)
        if relevant_content:
            response = "Based on the document:\n\n"
            for sentence in relevant_content[:3]:  # Show up to 3 relevant sentences
                response += f"• {sentence}\n\n"
            return response
    
    # General conversation responses
    if 'hello' in prompt_lower or 'hi' in prompt_lower:
        return "Hello! I'm your school assistant. I can help you understand documents or chat about school-related topics. What would you like to discuss?"
    
    elif 'help' in prompt_lower:
        return "I can help you by:\n1. Answering questions about uploaded documents\n2. Discussing school subjects\n3. Explaining concepts\n\nWhat would you like to know more about?"
    
    elif any(subject in prompt_lower for subject in ['math', 'science', 'english', 'geography', 'history', 'literature']):
        return f"I'd be happy to discuss {prompt}! What specific aspect would you like to explore? If you have any study materials to upload, I can help explain those too."
    
    elif doc_content:
        return "I have access to the document but couldn't find a direct answer to your question. Could you rephrase it or be more specific about what you're looking for?"
    
    else:
        return "I'm here to help! If you're asking about specific information, you can upload a document and I'll help you understand it. Or we can discuss any school-related topic you're interested in."

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
    
    # Get and display response
    response = get_response(prompt, st.session_state.document_content, st.session_state.doc_name)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
