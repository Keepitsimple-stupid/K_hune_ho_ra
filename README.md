# KHUNEHO: Neural News Analysis System

KHUNEHO (Knowledge-based Hierarchical Universal Neural Engine for Holistic Outlook) is a local-first news intelligence system that retrieves live articles, runs 15 domain-specialized reasoning agents using a quantized large language model, and produces structured predictions with confidence scores and timelines.

Designed to operate on consumer hardware with 16GB VRAM, KHUNEHO requires no API keys, sends no data to the cloud, and provides transparent, citeable outputs.

## Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output Format](#output-format)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)

## Features

- Topic-to-report pipeline: input a topic, system fetches 15 relevant news articles from free web sources (GNews RSS, DuckDuckGo fallback).
- 15 multi-agent reasoning: each domain (financial, geopolitical, legal, technological, etc.) produces 5-10 detailed predictions.
- Each prediction includes: natural language statement, confidence score (0-1), timeline, and affected entity/sector.
- Local execution: runs entirely offline after model download; no external API keys.
- GPU acceleration via llama-cpp-python with CUDA (optional CPU fallback).
- Lightweight VRAM footprint: 6GB peak for 8B quantized model (Phi-3.5 uses ~2.5GB).
- Structured JSON output for easy integration with downstream tools.

## System Requirements

- Operating System: Linux, Windows (WSL2 recommended), or macOS with Metal support.
- Python: 3.10 or higher.
- GPU (recommended): NVIDIA GPU with 8GB+ VRAM (16GB ideal). CPU execution possible but slower.
- RAM: 16GB system RAM.
- Disk space: 10GB free for models and dependencies.

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/yourusername/khuneho-reasoner.git
cd khuneho-reasoner
python -m venv venv
source venv/bin/activate   # Linux/macOS
# or .\venv\Scripts\activate (Windows)
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install llama-cpp-python with GPU support (recommended):

```bash
# For CUDA (NVIDIA GPU)
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python==0.2.77
```

If you encounter build issues, use a pre‑built wheel (see [Troubleshooting](#troubleshooting)).

Download the default model (Qwen2.5-7B-Instruct Q4_K_M, ~4.5GB):

```bash
python setup.py
```

You can change the model by editing .env (see Configuration).

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| LLM_MODEL_PATH | Path to GGUF model file | models/qwen2.5-7b-instruct-q4_K_M.gguf |
| N_GPU_LAYERS | Number of layers to offload to GPU (0 = CPU only) | 99 |
| N_CTX | Context window size (tokens) | 8192 |
| MAX_TOKENS | Maximum tokens per prediction batch | 2048 |
| NEWS_MAX_ARTICLES | Number of articles to retrieve | 15 |
| NEWS_TIME_RANGE | day, week, month | week |
| DOMAIN_WEIGHTS | Comma-separated domain:weight pairs | see .env.example |

## Usage

Run the main script:

```bash
python run.py
```

Enter a topic at the prompt. Example:

```
> Topic: Global semiconductor shortage impact on European automakers
```

The system will:

1. Search for 15 relevant news articles (using GNews RSS).
2. Run 15 reasoning agents sequentially (each producing 5-10 predictions).
3. Output a formatted report with domain-specific predictions, confidence scores, timelines, and source citations.

To exit, type exit or quit.

## Output Format

The final report includes per-domain prediction arrays, a timeline of source articles, and full citations.

Example snippet for the financial domain:

```
## FINANCIAL (weight 1.00)
    1. Banking sector ETF rises 8-12% in next 6 months
       Confidence: 0.85 | Timeline: Q3-Q4 2025
       Affected Sector: financial
    2. Tech growth stocks underperform value stocks by 15% in 2025
       Confidence: 0.78 | Timeline: 12 months
       Affected Sector: technology
```

All predictions are extracted as JSON arrays internally, allowing programmatic consumption.

## Architecture

```
khuneho_reasoner/
├── run.py                 # Entry point
├── setup.py               # Model download script
├── requirements.txt
├── .env                   # Configuration
├── src/
│   ├── config.py          # Loads environment variables
│   ├── news_retriever.py  # Fetches articles (GNews + fallback)
│   ├── agent_manager.py   # Loads LLM, runs 15 domain agents
│   ├── synthesizer.py     # Compiles predictions into final report
│   └── utils.py           # Helper functions
└── models/                # Downloaded GGUF models
```

**Data flow**:

- User topic → NewsRetriever → 15 articles.
- Articles → AgentManager (one LLM, sequential domain prompts).
- Each domain returns JSON prediction array → Synthesizer.
- Final report printed to console.

## Troubleshooting

### Model fails to load (ValueError)

- Ensure the GGUF file exists and is not corrupted. Delete and re‑download using python setup.py.
- Try a different model, e.g., Phi-3.5-mini-instruct-Q4_K_M.gguf (more stable).

### DuckDuckGo rate limits

The system falls back to GNews RSS, which is more reliable. If both fail, install gnews:

```bash
pip install gnews
```

### CUDA build fails for llama-cpp-python

Use a pre‑built wheel:

```bash
pip install https://github.com/abetlen/llama-cpp-python/releases/download/v0.2.90/llama_cpp_python_cuda-0.2.90-cp312-cp312-linux_x86_64.whl
```

For other Python/CUDA versions, check the [releases page](https://github.com/abetlen/llama-cpp-python/releases).

### Out of memory (OOM) errors

Reduce N_CTX (e.g., 4096) or MAX_TOKENS (1024). Switch to CPU by setting N_GPU_LAYERS=0.

### Slow inference on CPU

Set N_GPU_LAYERS=0 in .env; CPU inference is slower (2-5 tokens/sec) but works.

## Contributing

Issues and pull requests are welcome. Please follow existing code style and include tests where applicable.

For major changes, open an issue first to discuss what you would like to change.

## Acknowledgements

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [Qwen2.5](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) and [bartowski](https://huggingface.co/bartowski) for GGUF quantizations
- [GNews](https://github.com/ranahaani/GNews) for free news RSS access
