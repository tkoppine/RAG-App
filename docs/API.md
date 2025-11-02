# API Documentation

## Overview

The ArXiv Research Assistant provides both REST API endpoints and Python SDK for searching and analyzing academic papers.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

Currently, the API does not require authentication for basic operations. API keys may be required for LLM-powered features.

## Endpoints

### Search Endpoints

#### Text Search

Search papers using natural language queries.

**Endpoint:** `POST /api/search/text/`

**Request Body:**

```json
{
  "query": "machine learning neural networks",
  "k": 5,
  "threshold": 0.1
}
```

**Response:**

```json
{
  "results": [
    {
      "paper_id": "arxiv:2301.12345",
      "title": "Advanced Neural Networks for Machine Learning",
      "abstract": "This paper presents...",
      "section_name": "abstract",
      "similarity_score": 0.95,
      "distance": 0.02,
      "authors": ["John Doe", "Jane Smith"],
      "url": "https://arxiv.org/abs/2301.12345",
      "content": "Detailed content from the matched section..."
    }
  ],
  "query_time": 0.15,
  "total_results": 1
}
```

#### Image Search

Search papers using image queries.

**Endpoint:** `POST /api/search/image/`

**Request:** Multipart form data

- `image`: Image file (JPG, PNG)
- `k`: Number of results (optional, default: 5)

**Response:** Same format as text search

#### Embedding Search

Search using pre-computed embeddings.

**Endpoint:** `POST /api/search/embedding/`

**Request Body:**

```json
{
    "embedding": [0.1, 0.2, ...],  // 512-dimensional vector
    "k": 5
}
```

### Paper Information

#### Get Paper Details

**Endpoint:** `GET /api/papers/{paper_id}/`

**Response:**

```json
{
  "paper_id": "arxiv:2301.12345",
  "title": "Paper Title",
  "abstract": "Abstract text...",
  "authors": ["Author 1", "Author 2"],
  "url": "https://arxiv.org/abs/2301.12345",
  "sections": {
    "introduction": "Introduction content...",
    "methodology": "Methodology content..."
  },
  "images": {
    "figure_1": {
      "image_desc": "Architecture diagram",
      "image_location": "path/to/image.jpg"
    }
  }
}
```

#### List Available Papers

**Endpoint:** `GET /api/papers/`

**Response:**

```json
{
  "papers": ["arxiv:2301.12345", "arxiv:2301.12346"],
  "total_count": 2
}
```

### Vectorization Endpoints

#### Vectorize Text

**Endpoint:** `POST /api/vectorize/text/`

**Request Body:**

```json
{
  "text": "Text to vectorize"
}
```

**Response:**

```json
{
    "embedding": [0.1, 0.2, ...],  // 512-dimensional vector
    "dimension": 512
}
```

#### Vectorize Image

**Endpoint:** `POST /api/vectorize/image/`

**Request:** Multipart form data

- `image`: Image file

**Response:** Same format as text vectorization

### System Information

#### Health Check

**Endpoint:** `GET /api/health/`

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### Statistics

**Endpoint:** `GET /api/stats/`

**Response:**

```json
{
  "total_papers": 1000,
  "faiss_vectors": 5000,
  "data_directory": "/app/data",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

### Common Error Codes

- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service temporarily unavailable

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting based on your needs.

## Python SDK Usage

```python
from src.search.search_engine import ArxivSearchEngine

# Initialize engine
engine = ArxivSearchEngine()

# Text search
results = engine.search_by_text("machine learning", k=5)

# Image search
results = engine.search_by_image("path/to/image.jpg", k=3)

# Get paper details
paper = engine.get_paper_details("arxiv:2301.12345")
```

## Examples

### cURL Examples

```bash
# Text search
curl -X POST http://localhost:8000/api/search/text/ \
  -H "Content-Type: application/json" \
  -d '{"query": "neural networks", "k": 3}'

# Image search
curl -X POST http://localhost:8000/api/search/image/ \
  -F "image=@/path/to/image.jpg" \
  -F "k=5"

# Get paper details
curl http://localhost:8000/api/papers/arxiv:2301.12345/
```

### JavaScript Examples

```javascript
// Text search
const response = await fetch("/api/search/text/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    query: "machine learning",
    k: 5,
  }),
});
const results = await response.json();

// Image search
const formData = new FormData();
formData.append("image", imageFile);
formData.append("k", "3");

const response = await fetch("/api/search/image/", {
  method: "POST",
  body: formData,
});
```
