"""
Streaming utilities for Server-Sent Events (SSE)
Enables progressive display of test cases as they're generated
"""
import json
import asyncio
from typing import AsyncGenerator
from backend.nodes.loader import load_document
from backend.nodes.splitter import split_text
from backend.nodes.vector_store import store_vectors
from backend.nodes.feature_extractor import extract_features, should_extract_features
from backend.nodes.retrieval import retrieve_chunks
from backend.nodes.generation import generate_test_cases
from backend.nodes.validation import check_hallucinations

async def stream_test_case_generation(file_path: str, feature_name: str, test_case_limit: int = None) -> AsyncGenerator[str, None]:
    """
    Stream test case generation using Server-Sent Events.
    Yields events as test cases are generated in real-time.
    
    Args:
        file_path: Path to uploaded requirements file
        feature_name: Feature name to generate test cases for
        test_case_limit: Optional limit on number of test cases
        
    Yields:
        SSE formatted strings with event data
    """
    try:
        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'message': 'Loading document...'})}\n\n"
        
        # Step 1: Load and process document
        # Initialize state with inputs and placeholders
        state = {
            "file_path": file_path,
            "feature_name": feature_name,
            "test_case_limit": test_case_limit,
            "documents": [],
            "chunks": [],
        }
        
        # Load document
        state = await asyncio.to_thread(load_document, state)
        yield f"data: {json.dumps({'type': 'status', 'message': 'Splitting text...'})}\n\n"
        
        # Split text
        state = await asyncio.to_thread(split_text, state)
        yield f"data: {json.dumps({'type': 'status', 'message': 'Creating vector store...'})}\n\n"
        
        # Store vectors (merge result)
        try:
            vector_result = await asyncio.to_thread(store_vectors, state)
            state = {**state, **vector_result}
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error creating vector store: {str(e)}'})}\n\n"
            return
        
        # Step 2: Determine if batch mode
        mode = should_extract_features(state)
        
        if mode == "extract":
            # Batch mode - extract features and process each
            yield f"data: {json.dumps({'type': 'status', 'message': 'Extracting features...'})}\n\n"
            
            state = await asyncio.to_thread(extract_features, state)
            if state.get("error"):
                yield f"data: {json.dumps({'type': 'error', 'message': state['error']})}\n\n"
                return
            
            features = state.get("extracted_features", [])
            total_features = len(features)
            
            yield f"data: {json.dumps({'type': 'batch_start', 'total_features': total_features})}\n\n"
            
            # Process each feature and stream results
            for idx, feature in enumerate(features, 1):
                feature_name = feature.get("name", f"Feature {idx}")
                feature_desc = feature.get("description", "")
                
                # Send progress
                yield f"data: {json.dumps({'type': 'progress', 'current': idx, 'total': total_features, 'feature': feature_name})}\n\n"
                
                # Process this feature
                feature_state = {
                    **state,
                    "feature_name": feature_name,
                    "retrieved_chunks": [],
                    "generated_test_cases": [],
                }
                
                # Retrieve chunks
                feature_state = await asyncio.to_thread(retrieve_chunks, feature_state)
                
                # Generate test cases
                try:
                    gen_result = await asyncio.to_thread(generate_test_cases, feature_state)
                    feature_state = {**feature_state, **gen_result}
                except Exception as e:
                    print(f"ERROR in generation for {feature_name}: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f'Error generating for {feature_name}: {str(e)}'})}\n\n"
                    continue

                if feature_state.get("error"):
                    print(f"ERROR returned for {feature_name}: {feature_state['error']}")
                    yield f"data: {json.dumps({'type': 'error', 'message': f"Error for {feature_name}: {feature_state['error']}"})}\n\n"
                    continue
                
                # Initialize validation components for this feature
                from backend.nodes.validation import validate_single_test_case
                from backend.nodes.llm_provider import get_llm
                from langchain_core.prompts import PromptTemplate
                from langchain_core.output_parsers import JsonOutputParser
                
                retrieved_chunks = feature_state["retrieved_chunks"]
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
                prompt = PromptTemplate(template=prompt_template, input_variables=["context", "test_case"])
                chain = prompt | llm | JsonOutputParser()
                
                # Stream each test case after validation
                test_cases = feature_state.get("generated_test_cases", [])
                
                for tc in test_cases:
                    # Validate individually
                    validated_tc, error = await asyncio.to_thread(validate_single_test_case, tc, context, chain)
                    
                    # Add feature info
                    validated_tc["feature"] = feature_name
                    validated_tc["feature_description"] = feature_desc
                    
                    # Stream immediately
                    yield f"data: {json.dumps({'type': 'test_case', 'test_case': validated_tc, 'feature': feature_name})}\n\n"
                    await asyncio.sleep(0.01)  # Small delay for smooth streaming
            
            # Send completion
            yield f"data: {json.dumps({'type': 'complete', 'result': {'hallucination_report': {'found_issues': False, 'issues': []}}})}\n\n"
            
        else:
            # Single feature mode
            yield f"data: {json.dumps({'type': 'status', 'message': f'Generating test cases for {feature_name}...'})}\n\n"
            
            # Retrieve chunks (merge)
            retrieve_result = await asyncio.to_thread(retrieve_chunks, state)
            state = {**state, **retrieve_result}
            
            # Generate test cases (merge)
            gen_result = await asyncio.to_thread(generate_test_cases, state)
            state = {**state, **gen_result}
            
            if state.get("error"):
                yield f"data: {json.dumps({'type': 'error', 'message': state['error']})}\n\n"
                return
            
            # Initialize validation components
            from backend.nodes.validation import validate_single_test_case
            from backend.nodes.llm_provider import get_llm
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import JsonOutputParser
            
            retrieved_chunks = state["retrieved_chunks"]
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
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "test_case"])
            chain = prompt | llm | JsonOutputParser()
            
            # Stream each test case after validation
            test_cases = state.get("generated_test_cases", [])
            hallucination_errors = []
            validated_test_cases = []
            
            for tc in test_cases:
                # Validate individually
                validated_tc, error = await asyncio.to_thread(validate_single_test_case, tc, context, chain)
                
                if error:
                    hallucination_errors.append(error)
                
                validated_test_cases.append(validated_tc)
                
                # Stream immediately
                yield f"data: {json.dumps({'type': 'test_case', 'test_case': validated_tc})}\n\n"
                await asyncio.sleep(0.01)
            
            # Update state with validation results
            state["hallucination_errors"] = hallucination_errors
            state["generated_test_cases"] = validated_test_cases
            
            # Send completion
            result = {
                "hallucination_report": {
                    "found_issues": len(hallucination_errors) > 0,
                    "issues": hallucination_errors
                }
            }
            yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"
        
    except Exception as e:
        # Send error event
        error_msg = str(e)
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
