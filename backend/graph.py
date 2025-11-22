from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END

from backend.nodes.loader import load_document
from backend.nodes.splitter import split_text
from backend.nodes.vector_store import store_vectors
from backend.nodes.retrieval import retrieve_chunks
from backend.nodes.generation import generate_test_cases
from backend.nodes.validation import check_hallucinations
from backend.nodes.formatter import format_output
from backend.nodes.feature_extractor import extract_features, should_extract_features
from backend.nodes.batch_processor import process_all_features

class GraphState(TypedDict):
    """
    Represents the state of the LangGraph workflow.
    """
    file_path: str
    documents: List[Document]
    chunks: List[Document]
    feature_name: str
    retrieved_chunks: List[Document]
    generated_test_cases: List[Dict[str, Any]]
    hallucination_errors: List[str]
    final_output: Dict[str, Any]
    extracted_features: Optional[List[Dict[str, str]]]  # For all features mode
    processed_features: Optional[List[Dict[str, Any]]]  # Metadata about processed features
    is_batch_mode: Optional[bool]  # Flag to indicate batch processing

def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("file_loader", load_document)
    workflow.add_node("text_splitter", split_text)
    workflow.add_node("vector_store", store_vectors)
    workflow.add_node("feature_extractor", extract_features)  # New node
    workflow.add_node("batch_processor", process_all_features)  # New node
    workflow.add_node("feature_query", retrieve_chunks)
    workflow.add_node("ollama_llm_node", generate_test_cases)
    workflow.add_node("hallucination_checker", check_hallucinations)
    workflow.add_node("formatter_node", format_output)
    
    # Add edges
    workflow.set_entry_point("file_loader")
    workflow.add_edge("file_loader", "text_splitter")
    workflow.add_edge("text_splitter", "vector_store")
    
    # Conditional routing after vector store
    workflow.add_conditional_edges(
        "vector_store",
        should_extract_features,
        {
            "extract": "feature_extractor",  # Go to feature extraction for "all features"
            "single": "feature_query"  # Go to normal flow for single feature
        }
    )
    
    # All features path
    workflow.add_edge("feature_extractor", "batch_processor")
    workflow.add_edge("batch_processor", "formatter_node")
    
    # Single feature path
    workflow.add_edge("feature_query", "ollama_llm_node")
    workflow.add_edge("ollama_llm_node", "hallucination_checker")
    workflow.add_edge("hallucination_checker", "formatter_node")
    
    # End
    workflow.add_edge("formatter_node", END)
    
    return workflow.compile()

app_graph = build_graph()

