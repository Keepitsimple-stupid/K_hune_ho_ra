"""
Configuration management for the Neural News Analysis System.

This module loads and centralizes all configuration parameters from environment variables,
providing defaults for LLM settings, news retrieval parameters, and domain weights.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Centralized configuration class for the application.
    
    All settings are loaded from environment variables with sensible defaults.
    Modify the .env file to override any configuration values.
    """
    # LLM Configuration
    LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "models/qwen2.5-7b-instruct-q4_K_M.gguf")
    N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "99"))  # Number of layers to offload to GPU
    N_CTX = int(os.getenv("N_CTX", "8192"))  # Context window size
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))  # Sampling temperature (lower = more deterministic)
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))  # Maximum tokens per response
    
    # News Retrieval Configuration
    NEWS_MAX_ARTICLES = int(os.getenv("NEWS_MAX_ARTICLES", "15"))  # Maximum articles to retrieve per search
    NEWS_TIME_RANGE = os.getenv("NEWS_TIME_RANGE", "week")  # Time filter: 'day', 'week', or 'month'
    DUCKDUCKGO_TIMEOUT = int(os.getenv("DUCKDUCKGO_TIMEOUT", "10"))  # Request timeout in seconds
    
    # Domain Weight Configuration
    # Weights determine the influence of each domain in the final report synthesis.
    # Higher weights indicate greater relevance to the analysis.
    dw_str = os.getenv("DOMAIN_WEIGHTS", "")
    DOMAIN_WEIGHTS = {}
    if dw_str:
        # Parse comma-separated key:value pairs from environment variable
        for item in dw_str.split(","):
            if ":" in item:
                k, v = item.split(":")
                DOMAIN_WEIGHTS[k.strip()] = float(v.strip())
    else:
        # Default domain weights
        DOMAIN_WEIGHTS = {
            "financial": 1.0, "geopolitical": 0.9, "legal": 0.7,
            "sentiment": 0.6, "economic": 0.9, "technological": 0.8,
            "social": 0.5, "environmental": 0.7, "health": 0.6,
            "military": 0.8, "cultural": 0.4, "ethical": 0.6,
            "strategic": 0.9, "historical": 0.5, "predictive": 0.8
        }
    
    # List of all analysis domains
    DOMAINS = list(DOMAIN_WEIGHTS.keys())


# Global configuration instance
config = Config()