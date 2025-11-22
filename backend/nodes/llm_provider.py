"""
LLM Provider Utility
Provides a unified interface to get LLM instances from different providers (Ollama, Groq).
"""
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def get_llm(temperature=0, format_json=False):
    """
    Returns an LLM instance based on the LLM_PROVIDER environment variable.
    
    Args:
        temperature: Temperature setting for the LLM (default: 0)
        format_json: Whether to request JSON formatted output (default: False)
    
    Returns:
        LLM instance (ChatOllama or ChatGroq)
    
    Raises:
        ValueError: If LLM_PROVIDER is not set to a valid value
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if provider == "ollama":
        return get_ollama_llm(temperature, format_json)
    elif provider == "groq":
        return get_groq_llm(temperature, format_json)
    else:
        raise ValueError(f"Invalid LLM_PROVIDER: {provider}. Must be 'ollama' or 'groq'")

def get_ollama_llm(temperature=0, format_json=False):
    """
    Returns a ChatOllama instance.
    
    Args:
        temperature: Temperature setting for the LLM
        format_json: Whether to request JSON formatted output
    
    Returns:
        ChatOllama instance
    """
    # Using llama3.2:3b - much lighter and faster than llama3.1 (2GB vs 4.9GB)
    # Alternative options: "phi3:mini", "gemma2:2b", "qwen2.5:3b"
    model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    
    kwargs = {
        "model": model,
        "temperature": temperature
    }
    
    if format_json:
        kwargs["format"] = "json"
    
    return ChatOllama(**kwargs)

def get_groq_llm(temperature=0, format_json=False):
    """
    Returns a ChatGroq instance.
    
    Args:
        temperature: Temperature setting for the LLM
        format_json: Whether to request JSON formatted output
    
    Returns:
        ChatGroq instance
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    kwargs = {
        "model": "llama-3.3-70b-versatile",  # Using Groq's Llama 3.3 70B model (updated from decommissioned 3.1)
        "temperature": temperature,
        "api_key": api_key
    }
    
    if format_json:
        # Groq uses model_kwargs for JSON mode
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
    
    return ChatGroq(**kwargs)

def get_provider_name():
    """
    Returns the current LLM provider name.
    
    Returns:
        str: Provider name ("ollama" or "groq")
    """
    return os.getenv("LLM_PROVIDER", "ollama").lower()
