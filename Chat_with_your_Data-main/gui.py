import streamlit as st
from processingTxt import split_chunks
import os

st.title("PDF Processor")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Custom CSS to adjust the distance in the sidebar
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        padding-top: 0;
    }
    .sidebar .css-1d391kg {
        margin-top: 0;
    }
    .sidebar .css-1s0rno7 {
        margin-top: 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for file upload
st.sidebar.header("Upload PDF")
uploaded_file = st.sidebar.file_uploader("", type="pdf")

if uploaded_file is not None:
    # Save the uploaded PDF file to a temporary file
    temp_pdf_path = "temp_uploaded_pdf.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.read())

    # Process the PDF file
    chunks = split_chunks(temp_pdf_path)
    
    # Display the results
    st.subheader("Extracted and Split Text from PDF")
    for chunk in chunks:
        st.write(f"**Chunk ID**: {chunk.metadata['id']}")
        st.write(chunk.page_content)
        st.write("---")

    # Remove the temporary file
    os.remove(temp_pdf_path)
    
    # Add PDF processing info to chat history (optional)
    st.session_state.messages.append({"role": "system", "content": "PDF content has been processed and split into chunks."})

# React to user input
if prompt := st.chat_input("Type your message here..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate and display assistant response
    response = f"Echo: {prompt}"
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
