import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
import json
import numpy as np


# Load documents from the PDF file
def load_documents(pdf_file_path):
    documents = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            documents.append({
                'filename': os.path.basename(pdf_file_path),
                'text': text,
                'page': page_number  # Add page number to metadata
            })
    return documents

# Convert extracted documents to Document objects
def convert_to_documents(extracted_documents):
    documents = []
    for doc in extracted_documents:
        documents.append(Document(
            page_content=doc['text'],
            metadata={
                'filename': doc['filename'],
                'page': doc['page']  # Include page number in metadata
            }
        ))
    return documents

# Split the documents into chunks
def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=80, 
        length_function=len, 
        is_separator_regex=False
    )
    # Split the documents and carry over metadata to each chunk
    chunks = []
    for document in documents:
        chunk_id = 0
        for chunk in text_splitter.split_documents([document]):
            chunk.metadata['id'] = f"{document.metadata['filename']}.{document.metadata['page']}.{chunk_id}"
            chunks.append(chunk)
            chunk_id += 1
    return chunks

# Main function to handle the PDF processing
def split_chunks(pdf_path):
    extracted_documents = load_documents(pdf_path)
    document_objects = convert_to_documents(extracted_documents)
    return split_documents(document_objects)



