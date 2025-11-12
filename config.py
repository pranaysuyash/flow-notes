import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration for Learning Mentor
# Add your API keys in the .env file

# OpenAI API (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-nano")  # or "gpt-4"

# Anthropic API (optional) 
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")  # or "claude-3-sonnet-20240229"

# Ollama/local models (optional)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # or any local model you have installed

# Default to local processing if no API keys provided
USE_LOCAL_PROCESSING = not bool(OPENAI_API_KEY)  # Set to False if API key is provided

# Ollama/local models (optional)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # or any local model you have installed
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Google Generative AI (optional)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")  # or other Gemini models

# Default model selection (fallback to local if no API keys provided)
DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "openai")  # Options: openai, anthropic, ollama, google