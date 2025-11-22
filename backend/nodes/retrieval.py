from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

def retrieve_chunks(state):
    """
    Retrieves relevant chunks from the vector store based on the feature name.
    """
    print("---RETRIEVING CHUNKS---")
    feature_name = state["feature_name"]
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    persist_dir = "./chroma_db"
    
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name="requirements_vectors"
    )
    
    # Retrieve top k chunks
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(feature_name)
    
    print(f"Retrieved {len(retrieved_docs)} chunks.")
    # Merge chunks into existing state
    new_state = dict(state)
    new_state["retrieved_chunks"] = retrieved_docs
    return new_state
