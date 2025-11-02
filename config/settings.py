"""
Configuration management for ArXiv Research Assistant
"""
import os
from pathlib import Path
from typing import Any, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
    
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Database Configuration
    FAISS_INDEX_FILE = os.getenv("FAISS_INDEX_FILE", str(DATA_DIR / "faiss_index.idx"))
    FAISS_MAPPING_FILE = os.getenv("FAISS_MAPPING_FILE", str(DATA_DIR / "embeddings_mapping.json"))
    ROCKSDB_PATH = os.getenv("ROCKSDB_PATH", str(DATA_DIR / "rocksdb"))
    PAPERS_DATA_JSON = os.getenv("PAPERS_DATA_JSON", str(DATA_DIR / "combined_data.json"))
    
    # Django Configuration
    DJANGO_SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-secret-key-here")
    DJANGO_DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
    DJANGO_ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # File Storage
    MEDIA_ROOT = os.getenv("MEDIA_ROOT", "media")
    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    
    # ArXiv Configuration
    ARXIV_API_URL = os.getenv("ARXIV_API_URL", "http://export.arxiv.org/api/query")
    DEFAULT_SEARCH_QUERY = os.getenv("DEFAULT_SEARCH_QUERY", "machine learning")
    MAX_PAPERS_PER_QUERY = int(os.getenv("MAX_PAPERS_PER_QUERY", "100"))
    
    # Vectorization Configuration
    CLIP_MODEL_NAME = os.getenv("CLIP_MODEL_NAME", "ViT-B/32")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "512"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))
    
    # Search Configuration
    DEFAULT_SEARCH_RESULTS = int(os.getenv("DEFAULT_SEARCH_RESULTS", "5"))
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "50"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Performance Configuration
    NUM_WORKERS = int(os.getenv("NUM_WORKERS", "4"))
    USE_GPU = os.getenv("USE_GPU", "False").lower() == "true"
    CACHE_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "3600"))
    
    # Development Configuration
    DEV_MODE = os.getenv("DEV_MODE", "True").lower() == "true"
    SKIP_SSL_VERIFY = os.getenv("SKIP_SSL_VERIFY", "False").lower() == "true"
    MOCK_APIS = os.getenv("MOCK_APIS", "False").lower() == "true"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        directories = [
            cls.DATA_DIR,
            Path(cls.MEDIA_ROOT),
            Path(cls.LOG_FILE).parent,
            Path(cls.ROCKSDB_PATH).parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        # Check required API keys
        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            issues.append("No LLM API key configured (GROQ_API_KEY or OPENAI_API_KEY)")
        
        # Check Django secret key
        if cls.DJANGO_SECRET_KEY == "your-secret-key-here":
            issues.append("Django secret key not configured (DJANGO_SECRET_KEY)")
        
        # Check file paths
        if not cls.DATA_DIR.exists():
            issues.append(f"Data directory does not exist: {cls.DATA_DIR}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config_summary": {
                "data_dir": str(cls.DATA_DIR),
                "has_groq_key": bool(cls.GROQ_API_KEY),
                "has_openai_key": bool(cls.OPENAI_API_KEY),
                "debug_mode": cls.DJANGO_DEBUG,
                "use_gpu": cls.USE_GPU
            }
        }


# Create singleton instance
config = Config()

# Ensure directories exist on import
config.ensure_directories()


if __name__ == "__main__":
    # Configuration validation script
    validation = config.validate_config()
    
    print("Configuration Validation Report")
    print("=" * 40)
    print(f"Status: {'✓ Valid' if validation['valid'] else '✗ Issues Found'}")
    print()
    
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
        print()
    
    print("Configuration Summary:")
    for key, value in validation['config_summary'].items():
        print(f"  {key}: {value}")