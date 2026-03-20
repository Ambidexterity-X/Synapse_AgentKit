# Multi-Agent Content Pipeline

## Description
This project is a fully local, zero-cost multi-agent AI system that autonomously produces long-form, SEO-optimized content from a single topic input. It leverages advanced AI tools to demonstrate real-world agent coordination.

## What Is Implemented

- Five-agent pipeline: Researcher, Writer, Editor, SEO Optimizer, Publisher
- Shared in-memory vector memory (ChromaDB with local fallback)
- Local LLM generation through Ollama (with graceful fallback)
- Embedding generation through OpenVINO on NPU when available (with deterministic fallback)
- Markdown publication output in the output folder
- CLI entrypoints: synapse and synapsecheck

## Requirements
- Run ``pip install -e `` and run the command ``synapsecheck`` to see if your PC can run this

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

## Quick Start

```bash
python -m pip install -e .
synapse "AI trends in 2026"
```

Optional environment variables:

```bash
TAVILY_API_KEY=your_tavily_key
EMBEDDING_DEVICE=NPU
USE_OPENVINO=1
```

If Tavily or Ollama is unavailable, the pipeline still runs in local fallback mode.

## Commands

- `synapse "<topic>"` runs the full pipeline and writes a markdown file to `output/`
- `synapse "<topic>" --destination markdown --output-dir output`
- `synapsecheck` runs the local hardware compatibility check

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
├── models.py                # Shared dataclasses between agents
├── pipeline.py              # Sequential orchestrator
├── output/                  # Generated articles saved here
├── main.py                  # Entry point — kickoff the crew
└── README.md
```
