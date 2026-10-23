"""Central configuration — all values sourced from environment / .env file."""

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env into os.environ

# Server
HOST  = '0.0.0.0'
PORT  = int(os.getenv('PORT', 5001))
DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# RAG
RAG_TOP_K = int(os.getenv('RAG_TOP_K', 5))

# ML classifier
CLASSIFIER_MAX_ITER = 1000
CLASSIFIER_C        = 1.0

# Cerebras LLM
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY', '')
CEREBRAS_MODEL   = os.getenv('CEREBRAS_MODEL', 'llama3.1-8b')

# Cache
CACHE_MAX_SIZE = int(os.getenv('CACHE_MAX_SIZE', 256))   # max cached LLM responses
CACHE_TTL_SECS = int(os.getenv('CACHE_TTL_SECS', 3600))  # 1 hour

# Rate limiting
RATE_LIMIT = os.getenv('RATE_LIMIT', '30 per minute')

# Paths
import pathlib
BASE_DIR        = pathlib.Path(__file__).parent
MODEL_CACHE_DIR = BASE_DIR / '.model_cache'
MODEL_CACHE_DIR.mkdir(exist_ok=True)
