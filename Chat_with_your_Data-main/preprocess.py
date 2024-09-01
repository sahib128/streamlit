import pdfplumber
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

def preprocess_text(text):
    return text

# Load documents from the PDF file
def load_documents(pdf_file_path):
    documents = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            lines = text.split('\n')

            # Initialize metadata
            metadata = {
                'filename': os.path.basename(pdf_file_path),
                'page': page_number,
                'title': None,
                'authors': None,
                'keywords': [],
                'journal_info': None,
                'doi': None
            }

            # Logic to extract title, authors, and journal information from the first page
            if page_number == 0:
                for i, line in enumerate(lines):
                    line = line.strip()

                    # Extract title (usually the first non-empty line)
                    if i == 0:
                        metadata['title'] = line
                    
                    # Extract authors (usually found after the title)
                    if 'Authors' in line or i == 1:
                        metadata['authors'] = line.replace("Authors:", "").strip()
                    
                    # Extract journal information and DOI
                    if 'Citation' in line:
                        metadata['journal_info'] = line
                    elif 'DOI' in line:
                        metadata['doi'] = line

                    # Extract keywords
                    if 'Keywords:' in line:
                        metadata['keywords'] = [kw.strip() for kw in line.replace("Keywords:", "").split(',')]

            # Skip irrelevant lines and consider only meaningful content
            content = []
            skip_keywords = ['Abstract', 'Introduction', 'References']
            for line in lines:
                if any(skip_word in line for skip_word in skip_keywords):
                    continue
                content.append(line.strip())

            # Join the content lines
            content = '\n'.join(content)
            
            # Append the extracted document with its metadata
            documents.append({
                'filename': metadata['filename'],
                'text': content,
                'page': metadata['page'],
                'metadata': metadata
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
                'page': doc['page'],
                'title': doc['metadata']['title'],
                'authors': doc['metadata']['authors'],
                'keywords': doc['metadata']['keywords'],
                'journal_info': doc['metadata']['journal_info'],
                'doi': doc['metadata']['doi']
            }
        ))
    return documents

# Split the documents into paragraphs using RecursiveCharacterTextSplitter
def split_documents(documents):
    chunks = []
    for document in documents:
        # Extract and handle metadata separately if needed
        metadata = document.metadata
        
        # Split the text into chunks using RecursiveCharacterTextSplitter
        paragraphs = text_splitter.split_text(document.page_content)
        for chunk_id, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if paragraph:  # Ensure it's not an empty paragraph
                chunks.append(Document(
                    page_content=paragraph,
                    metadata={
                        'id': f"{document.metadata['filename']}.{document.metadata['page']}.{chunk_id}",
                        'filename': document.metadata['filename'],
                        'page': document.metadata['page'],
                        'title': metadata['title'],
                        'authors': metadata['authors'],
                        'keywords': metadata['keywords'],
                        'journal_info': metadata['journal_info'],
                        'doi': metadata['doi']
                    }
                ))
    return chunks

# Save chunks to a file with UTF-8 encoding
def save_chunks_to_file(chunks, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for chunk in chunks:
            file.write(chunk.page_content + "\n\n")

# Save metadata to a separate file (optional)
def save_metadata_to_file(documents, filename):
    metadata_list = []
    for document in documents:
        metadata_list.append(document.metadata)
    
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(metadata_list, file, indent=2)

# Display chunks and their metadata
def display_chunks_with_metadata(chunks):
    for chunk in chunks:
        print(f"Chunk ID: {chunk.metadata['id']}")
        print(f"Filename: {chunk.metadata['filename']}")
        print(f"Page: {chunk.metadata['page']}")
        print(f"Title: {chunk.metadata['title']}")
        print(f"Authors: {chunk.metadata['authors']}")
        print(f"Keywords: {', '.join(chunk.metadata['keywords'])}")
        print(f"Journal Info: {chunk.metadata['journal_info']}")
        print(f"DOI: {chunk.metadata['doi']}")
        print("Content:")
        print(chunk.page_content)
        print("\n" + "-"*40 + "\n")

# Main function to handle the PDF processing
def split_chunks(pdf_path):
    extracted_documents = load_documents(pdf_path)
    document_objects = convert_to_documents(extracted_documents)
    chunks = split_documents(document_objects)
    save_chunks_to_file(chunks, "text_generation_data.txt")
    save_metadata_to_file(document_objects, "metadata.json")  # Save metadata to a separate file
    display_chunks_with_metadata(chunks)  # Display chunks and metadata
    return chunks

split_chunks("machine.pdf")