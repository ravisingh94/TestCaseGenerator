from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_text(state):
    """
    Splits the loaded documents into chunks.
    """
    print("---SPLITTING TEXT---")
    documents = state["documents"]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    # Merge chunks into existing state
    new_state = dict(state)
    new_state["chunks"] = chunks
    return new_state
