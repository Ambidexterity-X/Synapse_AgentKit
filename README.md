# Multi-Agent Content Pipeline

## Description
This project is a fully local, zero-cost multi-agent AI system that autonomously produces long-form, SEO-optimized content from a single topic input. It leverages advanced AI tools to demonstrate real-world agent coordination.

## Requirements

### Software
- **Python 3.11**
- **Libraries**:
  - CrewAI
  - ChromaDB
  - OpenVINO
  - Ollama Python Client
  - Transformers
  - Optimum-Intel
  - Streamlit (optional for UI)

### Operating System
- Windows 11

## Features
- Fully local execution with zero-cost tools.
- Five specialized agents for research, writing, editing, SEO optimization, and publishing.
- Outputs formatted for Markdown, WordPress, or Google Docs.

## Project Structure
```
multi-agent-content-pipeline/
├── agents/
│   ├── researcher.py
│   ├── writer.py
│   ├── editor.py
│   ├── seo_optimizer.py
│   └── publisher.py
├── tools/
│   ├── search_tool.py       # Tavily wrapper
│   ├── chroma_tool.py       # ChromaDB read/write
│   └── embed_tool.py        # OpenVINO embedding
├── memory/
│   └── vector_store.py      # ChromaDB client singleton
├── output/                  # Generated articles saved here
├── main.py                  # Entry point — kickoff the crew
├── requirements.txt
└── README.md
```