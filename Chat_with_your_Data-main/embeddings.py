import streamlit as st
import os
from processingTxt import split_chunks  # Ensure this function is correctly imported
from chatbot import query_general_model, query_rag

# Streamlit page configuration
st.set_page_config(page_title="Chat with Your Data", layout="wide")

# Custom CSS to hide the default file uploader and style the custom button
st.markdown("""
    <style>
    /* Hide the drag-and-drop file uploader area */
    .stFileUploader > label {
        display: none;
    }
    
    /* Style the upload button */
    .stFileUploader > div > div {
        border: none;
        padding: 0;
    }
    
    .stFileUploader > div > div > div > button {
        background-color: #007BFF; /* Custom blue color */
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
    }
    
    .stFileUploader > div > div > div > button:hover {
        background-color: #0056b3; /* Darker blue on hover */
    }
    </style>
""", unsafe_allow_html=True)

# Title and sidebar configuration
st.sidebar.title("Chat with Your Data")
st.sidebar.write("This application allows you to upload any text file and chat with it. You can also communicate through general queries.")

st.sidebar.subheader("Settings")
model_options = ["llama-3.1", "another_model_1", "another_model_2"]
selected_model = st.sidebar.selectbox("Select Model", model_options, index=model_options.index("llama-3.1"))
temperature = st.sidebar.slider('Temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('Top P', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_length = st.sidebar.slider('Max Length', min_value=32, max_value=128, value=120, step=8)

# Initialize session state variables
if 'text_chunks' not in st.session_state:
    st.session_state.text_chunks = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""

# Function to handle queries
def handle_query():
    try:
        model = selected_model if selected_model else "llama-3.1"
        if st.session_state.text_chunks:
            context_text = ' '.join(chunk.page_content for chunk in st.session_state.text_chunks)
            response = query_rag(st.session_state.query_input, context_text, model)
        else:
            response = query_general_model(st.session_state.query_input, model)
        
        st.session_state.messages.append(f"**You:** {st.session_state.query_input}")
        st.session_state.messages.append(f"**Chatbot:** {response}")
        st.session_state.query_input = ""
    except Exception as e:
        st.error(f"Error: {e}")

# PDF processing function
def process_and_update(pdf_file):
    try:
        st.write("Processing the PDF...")
        chunks = split_chunks(pdf_file)
        st.session_state.text_chunks = chunks
        st.success("PDF processed successfully. You can start asking questions.")
    except Exception as e:
        st.error(f"Error: {e}")

# Chat with Data interface (default view)
st.title("Welcome to Data Heaven")

for message in st.session_state.messages:
    st.write(message)

col1, col2, col3 = st.columns([8, 1, 1])

with col1:
    st.text_input("Enter your query...", key="query_input", placeholder="Type your question here...", label_visibility="collapsed")

with col2:
    st.markdown("""
        <style>
            .send-button {
                display: flex;
                justify-content: center;
                align-items: center;
                background-color: #007bff;
                border: none;
                color: white;
                padding: 0.5rem;
                border-radius: 50%;
                cursor: pointer;
                font-size: 1.25rem;
                margin-top: 0.2rem;
            }
            .send-button:hover {
                background-color: #0056b3;
            }
        </style>
        <button class="send-button" onclick="document.querySelector('button[type=submit]').click()">&#x27A4;</button>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <label for="file-upload" class="custom-file-uploader">
            Upload PDF
        </label>
        <input id="file-upload" class="file-uploader" type="file" accept="application/pdf" style="display:none;">
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
if uploaded_file is not None:
    process_and_update(uploaded_file)
