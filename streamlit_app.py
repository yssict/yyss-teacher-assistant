import streamlit as st
import PyPDF2
import docx
import io

# Page configuration
st.set_page_config(page_title="YYSS Teacher Assistant", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_content" not in st.session_state:
    st.session_state.document_content = ""

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def is_document_related(prompt):
    # Keywords that suggest document-related queries
    doc_keywords = ['mims', 'sls', 'password', 'ict', 'rules', 'room', 'teacher']
    return any(keyword in prompt.lower() for keyword in doc_keywords)

def get_response(prompt, doc_content):
    prompt_lower = prompt.lower()
    
    # If question is about document content
    if is_document_related(prompt):
        if doc_content:
            # Add specific document-based responses here
            if 'mims' in prompt_lower:
                return "MIMS is our school's Management Information System. Based on the document, for MIMS password resets, you should inform your Form Teacher who will help submit your request through the fault reporting form."
            elif 'time' in prompt_lower and 'ict' in prompt_lower:
                return "Let me check the ICT room timing information in the document. If you don't see a specific answer, please check with your Form Teacher for the current ICT room schedule."
            else:
                return f"Based on the document: {doc_content[:200]}... Would you like me to explain any specific part?"
        return "I see you're asking about school-related information, but I need the relevant document to be uploaded first to give you accurate information."
    
    # General conversation responses (age-appropriate for Sec 1-5)
    else:
        if 'hello' in prompt_lower or 'hi' in prompt_lower:
            return "Hello! I'm your friendly school assistant. I can help you with school-related questions or we can just chat about appropriate topics for secondary school students!"
        elif 'how are you' in prompt_lower:
            return "I'm doing well, thank you! Ready to help you with your questions about school or have a friendly chat. How's your school day going?"
        elif any(word in prompt_lower for word in ['joke', 'funny']):
            return "Here's a school-appropriate joke: Why don't calculators tell jokes? Because they take things too literally! 😄"
        else:
            return "I'm happy to chat with you about school, studies, or general topics suitable for secondary school students. What would you like to discuss?"

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
    response = get_response(prompt, st.session_state.document_content)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)
