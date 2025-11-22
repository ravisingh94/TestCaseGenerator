from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
import os

def store_vectors(state):
    """
    Embeds the chunks and stores them in ChromaDB.
    """
    print("---STORING VECTORS---")
    chunks = state["chunks"]
    
    try:
        # Initialize Ollama Embeddings
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
        # Initialize Chroma
        persist_dir = "./chroma_db"
        
        # Check if chunks is empty
        if not chunks:
            print("Warning: No chunks to store.")
            return {"vectorstore": None}
            
        print(f"Storing {len(chunks)} chunks in vector store...")
        
        # Process in batches to avoid overwhelming Ollama
        batch_size = 1  # Process one by one for maximum stability
        vectorstore = None
        import time
        
        total_batches = (len(chunks) + batch_size - 1) // batch_size
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            current_batch = i // batch_size + 1
            print(f"Processing batch {current_batch}/{total_batches} ({len(batch)} chunks)")
            
            # Retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if vectorstore is None:
                        vectorstore = Chroma.from_documents(
                            documents=batch,
                            embedding=embeddings,
                            persist_directory=persist_dir,
                            collection_name="requirements_vectors"
                        )
                    else:
                        vectorstore.add_documents(documents=batch)
                    break  # Success, exit retry loop
                except Exception as e:
                    print(f"Error processing batch {current_batch} (Attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        wait_time = 2 * (attempt + 1)
                        print(f"Waiting {wait_time}s before retrying...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"Failed to process batch {current_batch} after {max_retries} attempts: {e}")
            
            # Delay between successful batches
            time.sleep(0.5)
        
        print("Vectors stored successfully.")
        return {"vectorstore": vectorstore}
        
    except Exception as e:
        print(f"Error storing vectors: {e}")
        # Propagate error to be handled by streaming.py
        raise Exception(f"Failed to create vector store: {str(e)}")
