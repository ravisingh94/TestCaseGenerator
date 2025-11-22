import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.documents import Document
from typing import List

def load_document(state):
    """
    Loads a document from the file path specified in the state.
    Supports PDF, TXT, and DOCX.
    """
    print("---LOADING DOCUMENT---")
    file_path = state["file_path"]
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    documents: List[Document] = []

    try:
        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif file_extension == ".txt":
            loader = TextLoader(file_path)
            documents = loader.load()
        elif file_extension == ".docx":
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
        print(f"Loaded {len(documents)} pages/documents.")
        # Merge documents into existing state without discarding other keys
        new_state = dict(state)
        new_state["documents"] = documents
        return new_state
        
    except Exception as e:
        print(f"Error loading document: {e}")
        raise e
