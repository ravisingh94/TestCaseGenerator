import json

def format_output(state):
    """
    Formats the final output.
    """
    print("---FORMATTING OUTPUT---")
    generated_test_cases = state["generated_test_cases"]
    hallucination_errors = state.get("hallucination_errors", [])
    is_batch_mode = state.get("is_batch_mode", False)
    processed_features = state.get("processed_features", [])
    error = state.get("error", None)
    error_type = state.get("error_type", None)
    
    output = {
        "test_cases": generated_test_cases,
        "hallucination_report": {
            "found_issues": len(hallucination_errors) > 0,
            "issues": hallucination_errors
        }
    }
    
    # Add error information if present
    if error:
        output["error"] = error
        output["error_type"] = error_type
    
    # Add batch mode metadata
    if is_batch_mode:
        output["batch_mode"] = True
        output["features_processed"] = processed_features
        output["total_features"] = len(processed_features)
        output["total_test_cases"] = len(generated_test_cases)
    
    return {"final_output": output}
