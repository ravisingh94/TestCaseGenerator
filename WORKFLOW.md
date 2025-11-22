# Application Workflow Graph

This graph visualizes the internal logic of the Test Case Generator, powered by LangGraph.

```mermaid
graph TD
    %% Nodes
    Start((Start))
    End((End))
    
    Loader["File Loader<br/>(Load PDF/DOCX/TXT)"]
    Splitter["Text Splitter<br/>(Chunking)"]
    VectorStore["Vector Store<br/>(Embed & Store)"]
    
    %% Conditional Logic
    CheckMode{Feature Mode?}
    
    %% Single Feature Path
    Query["Feature Query<br/>(Retrieve Context)"]
    Gen["Generation Node<br/>(LLM)"]
    Hallucination["Hallucination Checker<br/>(Validation)"]
    
    %% All Features Path (Batch)
    Extractor["Feature Extractor<br/>(Identify Features)"]
    BatchProc["Batch Processor<br/>(Loop Features)"]
    
    Formatter["Formatter Node<br/>(Final Output)"]

    %% Edges
    Start --> Loader
    Loader --> Splitter
    Splitter --> VectorStore
    VectorStore --> CheckMode
    
    %% Single Feature Flow
    CheckMode -- "Single Feature" --> Query
    Query --> Gen
    Gen --> Hallucination
    Hallucination --> Formatter
    
    %% All Features Flow
    CheckMode -- "All Features" --> Extractor
    Extractor --> BatchProc
    BatchProc --> Formatter
    
    %% End
    Formatter --> End

    %% Styling
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef logic fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef llm fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    
    class CheckMode logic;
    class VectorStore storage;
    class Gen,Extractor,Hallucination llm;
```

## Node Descriptions

1.  **File Loader**: Reads the uploaded file content.
2.  **Text Splitter**: Breaks the text into manageable chunks (1000 chars) for processing.
3.  **Vector Store**: Embeds chunks using `nomic-embed-text` and stores them in ChromaDB.
4.  **Feature Mode Check**: Determines if the user requested a specific feature or "all features".
5.  **Feature Extractor**: (Batch Mode) Uses LLM to identify all testable features in the document.
6.  **Batch Processor**: (Batch Mode) Iterates through each extracted feature, running the generation pipeline for each.
7.  **Feature Query**: (Single Mode) Retrieves relevant text chunks for the specific feature.
8.  **Generation Node**: (Single Mode) Uses LLM to generate test cases based on retrieved context.
9.  **Hallucination Checker**: (Single Mode) Validates generated test cases against the source text to ensure accuracy.
10. **Formatter Node**: Formats the final result for the frontend.
