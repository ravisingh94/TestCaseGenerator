"""
Feature Extractor Node
Extracts all features from requirements document when user requests "all features"
"""
from backend.nodes.llm_provider import get_llm, get_provider_name
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict

def extract_features(state):
    """
    Extracts all features from the requirements document.
    Only called when feature_name is "all features" or similar.
    """
    print("---EXTRACTING FEATURES---")
    provider = get_provider_name()
    print(f"Using LLM Provider for feature extraction: {provider}")
    
    chunks = state.get("chunks", [])
    
    # Combine chunks to get full context (limit to avoid token issues)
    # Take first 10 chunks to avoid overwhelming the LLM
    max_chunks = 10
    context_chunks = chunks[:max_chunks]
    context = "\n\n".join([doc.page_content for doc in context_chunks])
    
    if len(chunks) > max_chunks:
        print(f"Warning: Document has {len(chunks)} chunks, using first {max_chunks} for feature extraction")
    
    llm = get_llm(temperature=0, format_json=True)
    
    prompt_template = """
    Analyze the following requirements document and extract all distinct features/functionalities.
    For each feature, provide:
    - name: A concise name for the feature
    - description: A brief description of what the feature does
    
    Requirements Document:
    {context}
    
    Return a JSON object with a "features" key containing a list of feature objects.
    Limit to maximum 10 most important features to avoid overwhelming output.
    
    Example output format:
    {{
        "features": [
            {{"name": "User Login", "description": "Allows users to authenticate with email and password"}},
            {{"name": "Password Reset", "description": "Enables users to reset forgotten passwords"}}
        ]
    }}
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({"context": context})
        print(f"DEBUG: Feature extraction response: {response}")
        
        features = []
        if isinstance(response, dict) and 'features' in response:
            features = response['features']
        elif isinstance(response, list):
            features = response
        
        print(f"Extracted {len(features)} features")
        
        # Store features in state
        return {"extracted_features": features}
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error extracting features: {error_msg}")
        
        # Check if it's a rate limit error
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            return {
                "extracted_features": [],
                "error": "Rate limit exceeded. Please wait a few minutes or switch to Ollama provider.",
                "error_type": "rate_limit"
            }
        else:
            return {
                "extracted_features": [],
                "error": f"Error extracting features: {error_msg}",
                "error_type": "extraction_error"
            }

def should_extract_features(state):
    """
    Determines if we should extract all features or use the provided feature name.
    Returns "extract" or "single"
    """
    feature_name = state.get("feature_name", "").lower().strip()
    
    # Check for various ways user might request all features
    all_features_keywords = ["all features", "all feature", "all", "everything", "complete"]
    
    if any(keyword in feature_name for keyword in all_features_keywords):
        return "extract"
    else:
        return "single"
