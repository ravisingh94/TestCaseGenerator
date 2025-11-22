from backend.nodes.llm_provider import get_llm, get_provider_name
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def check_hallucinations(state):
    """
    Verifies that each generated test case is supported by the retrieved requirement chunks.
    """
    print("---CHECKING HALLUCINATIONS---")
    provider = get_provider_name()
    print(f"Using LLM Provider for validation: {provider}")
    retrieved_chunks = state["retrieved_chunks"]
    generated_test_cases = state["generated_test_cases"]
    print(f"DEBUG: Validation received type: {type(generated_test_cases)}")
    print(f"DEBUG: Validation received content: {generated_test_cases}")
    
    context = "\n\n".join([doc.page_content for doc in retrieved_chunks])
    
    llm = get_llm(temperature=0, format_json=True)
    
    prompt_template = """
    You are a QA auditor. Verify that the following test case is supported by the provided requirement text.
    
    Requirement Text:
    {context}
    
    Test Case:
    {test_case}
    
    Instructions:
    1. Check if the test case steps and expected results are derived from the requirements.
    2. Be lenient with exact wording; look for semantic meaning.
    3. If the test case is a standard app behavior (like "Open app") implied by the feature, consider it supported.
    4. Only flag as unsupported if it explicitly contradicts the requirements or mentions features completely absent from the text.
    
    Return a JSON object with:
    "supported": boolean,
    "reason": string (explanation if not supported, otherwise "Supported")
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "test_case"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    hallucination_errors = []
    checked_test_cases = []
    
    # We can check each test case individually or in batch. 
    # Checking individually is more precise but slower. 
    # Given the likely small number, individual checks are safer for accuracy.
    
def validate_single_test_case(test_case, context, chain):
    """
    Validates a single test case against the context using the provided chain.
    Returns the validated test case with hallucination flags.
    """
    try:
        # Convert test case to string for the prompt
        test_case_str = str(test_case)
        result = chain.invoke({"context": context, "test_case": test_case_str})
        
        if not result.get("supported", True):
            test_case["hallucination_flag"] = True
            test_case["hallucination_reason"] = result.get("reason")
            return test_case, f"Test Case {test_case.get('Test Case ID', 'Unknown')} not supported: {result.get('reason')}"
        else:
            test_case["hallucination_flag"] = False
            return test_case, None
            
    except Exception as e:
        print(f"Error checking test case: {e}")
        return test_case, f"Error checking test case: {str(e)}"

def check_hallucinations(state):
    """
    Verifies that each generated test case is supported by the retrieved requirement chunks.
    """
    print("---CHECKING HALLUCINATIONS---")
    provider = get_provider_name()
    print(f"Using LLM Provider for validation: {provider}")
    retrieved_chunks = state["retrieved_chunks"]
    generated_test_cases = state["generated_test_cases"]
    
    context = "\n\n".join([doc.page_content for doc in retrieved_chunks])
    
    llm = get_llm(temperature=0, format_json=True)
    
    prompt_template = """
    You are a QA auditor. Verify that the following test case is supported by the provided requirement text.
    
    Requirement Text:
    {context}
    
    Test Case:
    {test_case}
    
    Return a JSON object with:
    "supported": boolean,
    "reason": string (explanation if not supported)
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "test_case"]
    )
    
    chain = prompt | llm | JsonOutputParser()
    
    hallucination_errors = []
    checked_test_cases = []
    
    if isinstance(generated_test_cases, list):
        for test_case in generated_test_cases:
            validated_tc, error = validate_single_test_case(test_case, context, chain)
            checked_test_cases.append(validated_tc)
            if error:
                hallucination_errors.append(error)
    else:
        print("Generated test cases format is not a list.")
        
    print(f"Found {len(hallucination_errors)} potential hallucinations.")
    
    return {
        "hallucination_errors": hallucination_errors,
        "generated_test_cases": checked_test_cases
    }
