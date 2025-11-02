# 🔬 ArXiv Research Assistant

**An AI-Powered Retrieval-Augmented Generation System for Academic Paper Discovery and Analysis**

> Transform how you discover and interact with scientific literature using advanced vector search and LLM integration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/framework-Django-green.svg)](https://www.djangoproject.com/)
[![FAISS](https://img.shields.io/badge/search-FAISS-red.svg)](https://github.com/facebookresearch/faiss)

---

## 🌟 Overview

The **ArXiv Research Assistant** is a sophisticated Retrieval-Augmented Generation (RAG) system designed specifically for academic research. It enables researchers to efficiently discover, analyze, and interact with scientific papers from ArXiv using natural language queries and image-based searches.

### 🎯 Key Features

- **🔍 Multi-Modal Search**: Query papers using text descriptions or images
- **🧠 AI-Powered Analysis**: Get intelligent summaries and insights using LLM integration
- **⚡ Lightning-Fast Retrieval**: FAISS-powered vector similarity search
- **📊 Rich Metadata**: Comprehensive paper information with RocksDB storage
- **🌐 Web Interface**: Django-based API for easy integration
- **📱 Modern Architecture**: Modular, scalable, and production-ready design

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Vector Search   │───▶│  LLM Response   │
│ (Text/Image)    │    │   (FAISS)        │    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        ▲
        ▼                        ▼                        │
┌─────────────────┐    ┌──────────────────┐              │
│ CLIP Embeddings │    │ Paper Metadata   │──────────────┘
│   (512-dim)     │    │   (RocksDB)      │
└─────────────────┘    └──────────────────┘
```

### 📁 Project Structure

```
ArXiv-Research-Assistant/
├── 📂 src/                     # Core application modules
│   ├── 📂 core/               # Base utilities and models
│   ├── 📂 vectorization/      # CLIP-based embedding generation
│   ├── 📂 storage/            # FAISS and RocksDB managers
│   ├── 📂 search/             # Advanced search functionality
│   └── 📂 web/                # Django web interface
├── 📂 config/                 # Configuration management
├── 📂 scripts/                # Utility scripts
├── 📂 docs/                   # Documentation
├── 📂 data/                   # Data storage directory
├── 📂 tests/                  # Test suites
├── 📄 .env.example           # Environment configuration template
├── 📄 requirements.txt       # Python dependencies
├── 📄 Dockerfile            # Container configuration
└── 📄 docker-compose.yml    # Multi-service deployment
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Git**
- **10GB+ free disk space** (for embeddings and papers)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-username/ArXiv-Research-Assistant.git
cd ArXiv-Research-Assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (see Environment Variables section below)
nano .env  # or your preferred editor
```

### 3. Initialize the System

```bash
# Validate configuration
python config/settings.py

# Build search indices (if you have existing data)
python src/storage/faiss_manager.py --input data/embeddings.json

# Run Django migrations
cd llm-integration/llmproject
python manage.py migrate
python manage.py collectstatic
```

### 4. Start the Application

```bash
# Development server
python manage.py runserver

# Or using Docker
docker-compose up
```

Visit `http://localhost:8000` to access the web interface.

---

## 🔧 Environment Variables

### 🔑 Required Configuration

| Variable            | Description                  | Example           |
| ------------------- | ---------------------------- | ----------------- |
| `GROQ_API_KEY`      | Groq API key for LLM queries | `gsk_abc123...`   |
| `DJANGO_SECRET_KEY` | Django security key          | `your-secret-key` |

### 🔧 Optional Configuration

| Variable                 | Description                          | Default |
| ------------------------ | ------------------------------------ | ------- |
| `OPENAI_API_KEY`         | OpenAI API key (alternative to Groq) | -       |
| `DATA_DIR`               | Data storage directory               | `data`  |
| `EMBEDDING_DIM`          | Vector embedding dimensions          | `512`   |
| `DEFAULT_SEARCH_RESULTS` | Default number of search results     | `5`     |
| `USE_GPU`                | Enable GPU acceleration              | `False` |

**📋 Get your API keys:**

- **Groq**: [console.groq.com/keys](https://console.groq.com/keys) (Free tier available)
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/account/api-keys)

---

## 📖 Usage Guide

### 🔍 Text-Based Search

```python
from src.search.search_engine import ArxivSearchEngine

# Initialize search engine
engine = ArxivSearchEngine()

# Search by text query
results = engine.search_by_text("neural networks for computer vision", k=5)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Similarity: {result['similarity_score']:.3f}")
    print(f"Abstract: {result['abstract'][:200]}...")
```

### 🖼️ Image-Based Search

```python
# Search using an image
results = engine.search_by_image("path/to/your/image.jpg", k=3)

for result in results:
    print(f"Found similar content in: {result['title']}")
    print(f"Section: {result['section_name']}")
```

### 🌐 Web API Usage

```bash
# Text search endpoint
curl -X POST http://localhost:8000/api/search/ \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "type": "text", "k": 5}'

# Image search endpoint
curl -X POST http://localhost:8000/api/search/ \
  -F "image=@/path/to/image.jpg" \
  -F "k=3"
```

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test modules
python -m pytest tests/test_faiss.py
python -m pytest tests/test_search_engine.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking (if using mypy)
mypy src/
```

### Adding New Features

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Implement changes** in appropriate `src/` modules
3. **Add tests** in `tests/` directory
4. **Update documentation** as needed
5. **Submit pull request**

---

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Deployment

```bash
# Build production image
docker build -t arxiv-assistant:latest .

# Run with environment file
docker run --env-file .env -p 8000:8000 arxiv-assistant:latest
```

---

## 📊 Performance & Scaling

### System Requirements

| Component   | Minimum | Recommended                |
| ----------- | ------- | -------------------------- |
| **RAM**     | 8GB     | 16GB+                      |
| **Storage** | 50GB    | 100GB+                     |
| **CPU**     | 4 cores | 8+ cores                   |
| **GPU**     | -       | CUDA-compatible (optional) |

### Optimization Tips

- **Enable GPU acceleration** for faster embeddings: Set `USE_GPU=True`
- **Adjust batch size** based on available memory
- **Use SSD storage** for faster index operations
- **Consider FAISS GPU indices** for large-scale deployments

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork the repository and clone your fork
git clone https://github.com/your-username/ArXiv-Research-Assistant.git

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **📖 Documentation**: [Full documentation](docs/)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/your-username/ArXiv-Research-Assistant/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/your-username/ArXiv-Research-Assistant/discussions)
- **📧 Email**: support@arxiv-assistant.com

---

## 🏆 Acknowledgments

- **[ArXiv](https://arxiv.org/)** for providing open access to scientific papers
- **[FAISS](https://github.com/facebookresearch/faiss)** for efficient similarity search
- **[OpenAI CLIP](https://github.com/openai/CLIP)** for multimodal embeddings
- **[Django](https://www.djangoproject.com/)** for the web framework
- **[Groq](https://groq.com/)** for fast LLM inference

---

<div align="center">

**⭐ Star this project if you find it useful!**

[Report Bug](https://github.com/your-username/ArXiv-Research-Assistant/issues) · [Request Feature](https://github.com/your-username/ArXiv-Research-Assistant/issues) · [Documentation](docs/)

</div>
