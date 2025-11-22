from backend.nodes.llm_provider import get_llm, get_provider_name
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import List, Dict
import json

def generate_test_cases(state):
    """
    Generates test cases using configured LLM (Ollama or Groq) based on retrieved chunks.
    """
    print("---GENERATING TEST CASES---")
    provider = get_provider_name()
    print(f"Using LLM Provider: {provider}")
    feature_name = state["feature_name"]
    retrieved_chunks = state["retrieved_chunks"]
    test_case_limit = state.get("test_case_limit")
    
    # Format context
    context = "\n\n".join([doc.page_content for doc in retrieved_chunks])
    
    # Initialize LLM using provider utility
    llm = get_llm(temperature=0, format_json=True)
    
    limit_instruction = ""
    if test_case_limit:
        limit_instruction = f"Generate exactly {test_case_limit} test cases."
    
    prompt_template = """
    Generate detailed test cases for the feature: {feature_name}.
    {limit_instruction}
    Include Test Case ID, Description, Preconditions, Steps, Expected Result.
    Only use information present in the provided requirements:
    {retrieved_chunks}
    
    Output the result as a JSON list of objects.
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["feature_name", "retrieved_chunks", "limit_instruction"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({
            "feature_name": feature_name, 
            "retrieved_chunks": context,
            "limit_instruction": limit_instruction
        })
        print(f"DEBUG: Generated response type: {type(response)}")
        print(f"DEBUG: Generated response content: {response}")
        
        # Handle both dict with 'testCases' key and direct list
        if isinstance(response, dict) and 'testCases' in response:
            test_cases = response['testCases']
        elif isinstance(response, list):
            test_cases = response
        else:
            test_cases = []
            
        print("Test cases generated.")
        return {"generated_test_cases": test_cases}
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating test cases: {error_msg}")
        
        # Check if it's a rate limit error
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            return {
                "generated_test_cases": [], 
                "error": "Rate limit exceeded. Please wait a few minutes or switch to Ollama provider.",
                "error_type": "rate_limit"
            }
        else:
            return {
                "generated_test_cases": [], 
                "error": error_msg,
                "error_type": "generation_error"
            }
