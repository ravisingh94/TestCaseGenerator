"""
Batch Processor for Multiple Features
Processes multiple features sequentially to generate test cases for each
"""
from typing import List, Dict, Any
from backend.nodes.retrieval import retrieve_chunks
from backend.nodes.generation import generate_test_cases
from backend.nodes.validation import check_hallucinations

def process_all_features(state):
    """
    Processes all extracted features sequentially.
    Generates test cases for each feature and aggregates results.
    """
    print("---PROCESSING ALL FEATURES---")
    
    extracted_features = state.get("extracted_features", [])
    
    # Check if there was an error during feature extraction
    if state.get("error"):
        print(f"Error in feature extraction: {state.get('error')}")
        return {
            "generated_test_cases": [],
            "hallucination_errors": [],
            "processed_features": [],
            "error": state.get("error"),
            "error_type": state.get("error_type")
        }
    
    if not extracted_features:
        print("No features extracted, returning empty results")
        return {
            "generated_test_cases": [],
            "hallucination_errors": [],
            "processed_features": []
        }
    
    all_test_cases = []
    all_hallucination_errors = []
    processed_features = []
    
    print(f"Processing {len(extracted_features)} features...")
    
    for idx, feature in enumerate(extracted_features, 1):
        feature_name = feature.get("name", f"Feature {idx}")
        feature_desc = feature.get("description", "")
        
        print(f"\n--- Processing Feature {idx}/{len(extracted_features)}: {feature_name} ---")
        
        try:
            # Create a temporary state for this feature
            feature_state = {
                **state,
                "feature_name": feature_name,
                "retrieved_chunks": [],
                "generated_test_cases": [],
                "hallucination_errors": []
            }
            
            # Step 1: Retrieve relevant chunks for this feature
            retrieval_result = retrieve_chunks(feature_state)
            feature_state.update(retrieval_result)
            
            # Step 2: Generate test cases for this feature
            generation_result = generate_test_cases(feature_state)
            feature_state.update(generation_result)
            
            # Step 3: Check for hallucinations
            validation_result = check_hallucinations(feature_state)
            feature_state.update(validation_result)
            
            # Add feature metadata to each test case
            feature_test_cases = feature_state.get("generated_test_cases", [])
            for tc in feature_test_cases:
                tc["feature"] = feature_name
                tc["feature_description"] = feature_desc
            
            # Aggregate results
            all_test_cases.extend(feature_test_cases)
            all_hallucination_errors.extend(feature_state.get("hallucination_errors", []))
            
            processed_features.append({
                "name": feature_name,
                "description": feature_desc,
                "test_case_count": len(feature_test_cases),
                "hallucination_count": len(feature_state.get("hallucination_errors", []))
            })
            
            print(f"Generated {len(feature_test_cases)} test cases for {feature_name}")
            
        except Exception as e:
            print(f"Error processing feature '{feature_name}': {e}")
            all_hallucination_errors.append(f"Error processing feature '{feature_name}': {str(e)}")
    
    print(f"\n--- Batch Processing Complete ---")
    print(f"Total features processed: {len(processed_features)}")
    print(f"Total test cases generated: {len(all_test_cases)}")
    print(f"Total hallucination errors: {len(all_hallucination_errors)}")
    
    return {
        "generated_test_cases": all_test_cases,
        "hallucination_errors": all_hallucination_errors,
        "processed_features": processed_features,
        "is_batch_mode": True
    }
