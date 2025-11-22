# Requirement Test Case Generator

An intelligent, agentic AI-powered tool that automatically generates comprehensive test cases from requirement documents (PDF, DOCX, TXT). It uses RAG (Retrieval-Augmented Generation) to ensure accuracy and includes a built-in hallucination check.

![Application Screenshot](https://via.placeholder.com/800x400?text=Requirement+Test+Case+Generator+UI)

## 🚀 Key Features

### 1. **Intelligent Test Case Generation**
- **RAG-Powered**: Uses Retrieval-Augmented Generation to ground test cases in your actual requirement text.
- **Multi-Format Support**: Upload requirements in PDF, DOCX, or TXT formats.
- **Structured Output**: Generates detailed test cases with IDs, Descriptions, Preconditions, Steps, and Expected Results.

### 2. **Real-Time Progressive Streaming**
- **Live Updates**: See test cases appear one by one as they are generated.
- **Status Feedback**: Real-time status messages (e.g., "Splitting text...", "Creating vector store...") keep you informed of the backend process.
- **Progress Tracking**: Visual progress bars for batch operations.

### 3. **Batch Processing ("All Features")**
- **Auto-Discovery**: Type "all features" to automatically extract every feature from your document.
- **Sequential Processing**: Processes features one by one to ensure stability and high quality.
- **Robust Handling**: Automatically handles large files by processing chunks in small batches with retry logic.

### 4. **Hallucination Detection & Validation**
- **Self-Correction**: Every generated test case is automatically validated against the source text.
- **Visual Warnings**: Flags potential hallucinations (test cases not supported by requirements) with clear warnings.
- **Context-Aware**: Uses smart prompts to understand implied behaviors and semantic meaning.

### 5. **Customizable Generation**
- **Feature Targeting**: Generate test cases for a specific feature (e.g., "Login Page") or the entire document.
- **Test Case Limit**: Set a maximum number of test cases to generate per feature to save time or tokens.

## 🛠️ Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS (No build step required)
  - Modern Glassmorphism UI
  - Server-Sent Events (SSE) for streaming
- **Backend**: Python FastAPI
  - **LangChain & LangGraph**: For orchestration and RAG pipelines.
  - **ChromaDB**: Local vector store for efficient retrieval.
  - **Ollama / Groq**: LLM support (defaulting to local Ollama for privacy).
  - **Pydantic**: For data validation.

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally.
- `nomic-embed-text` model for embeddings (`ollama pull nomic-embed-text`).
- A generation model like `llama3` or `mistral` (`ollama pull llama3`).

### 1. Clone the Repository
```bash
git clone <repository-url>
cd TestCaseGenerator
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory if you plan to use Groq or other providers:
```env
GROQ_API_KEY=your_groq_api_key_here
# OLLAMA_BASE_URL=http://localhost:11434 (Optional, defaults to localhost)
```

### 4. Run the Application

**Start the Backend:**
```bash
# From the root directory
uvicorn backend.main:app --reload
```
The backend will start at `http://127.0.0.1:8000`.

**Start the Frontend:**
You can use any simple HTTP server. For Python:
```bash
cd frontend
python -m http.server 3000
```
Access the app at `http://localhost:3000`.

## 📖 Usage Guide

1.  **Upload Document**: Drag and drop your requirement file (PDF, DOCX, TXT).
2.  **Select Feature**:
    *   Enter a specific feature name (e.g., "Search Functionality").
    *   OR enter **"all features"** to generate test cases for the entire document.
3.  **Set Limit (Optional)**: Enter a number to limit how many test cases are generated (e.g., "5").
4.  **Generate**: Click "Generate Test Cases".
5.  **Review**: Watch test cases appear in real-time. Check for any "Potential Hallucination" warnings.

## 🔧 Troubleshooting

-   **"Error creating vector store"**: This usually means Ollama is overloaded or not running.
    *   Ensure Ollama is running (`ollama serve`).
    *   The system automatically retries with smaller batches for large files.
-   **Stuck at "Generating..."**: Refresh the page. The backend might have hit a timeout.
-   **"No ID" in test cases**: Ensure you are using the latest version of the frontend (hard refresh to clear cache).

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
