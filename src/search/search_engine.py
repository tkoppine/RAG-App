"""
Advanced search functionality for paper similarity and retrieval
"""
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from storage.faiss_manager import FAISSManager
from storage.rocksdb_manager import RocksDBManager
from vectorization.clip_vectorization import vectorize_text, vectorize_image


class ArxivSearchEngine:
    """Main search engine for ArXiv papers using FAISS and RocksDB"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.faiss_manager = FAISSManager(data_dir)
        self.rocksdb_manager = RocksDBManager(str(self.data_dir / "rocksdb"))
        
        # Try to load existing indices
        try:
            self.faiss_manager.load_index()
            self.faiss_manager.load_mapping()
        except FileNotFoundError:
            print("Warning: No existing FAISS index found. Please build index first.")
    
    def search_by_text(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search papers by text query"""
        # Vectorize the query
        query_vector = vectorize_text(query)
        
        # Search similar embeddings
        similar_results = self.faiss_manager.search_similar(query_vector, k)
        
        # Enrich results with paper metadata
        enriched_results = []
        for result in similar_results:
            paper_id = result["paper_id"]
            paper_data = self.rocksdb_manager.get_paper(paper_id)
            
            if paper_data:
                enriched_result = {
                    **result,
                    "title": paper_data.get("title", "Unknown"),
                    "abstract": paper_data.get("abstract", ""),
                    "authors": paper_data.get("authors", []),
                    "url": paper_data.get("url", ""),
                    "content": self._get_section_content(paper_data, result["section_name"])
                }
                enriched_results.append(enriched_result)
        
        return enriched_results
    
    def search_by_image(self, image_path: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search papers by image query"""
        # Vectorize the image
        query_vector = vectorize_image(image_path)
        
        # Search similar embeddings
        similar_results = self.faiss_manager.search_similar(query_vector, k)
        
        # Enrich results with paper metadata
        enriched_results = []
        for result in similar_results:
            paper_id = result["paper_id"]
            paper_data = self.rocksdb_manager.get_paper(paper_id)
            
            if paper_data:
                enriched_result = {
                    **result,
                    "title": paper_data.get("title", "Unknown"),
                    "abstract": paper_data.get("abstract", ""),
                    "content": self._get_section_content(paper_data, result["section_name"])
                }
                enriched_results.append(enriched_result)
        
        return enriched_results
    
    def search_by_embedding(self, embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
        """Search papers by pre-computed embedding"""
        similar_results = self.faiss_manager.search_similar(embedding, k)
        
        # Enrich results with paper metadata
        enriched_results = []
        for result in similar_results:
            paper_id = result["paper_id"]
            paper_data = self.rocksdb_manager.get_paper(paper_id)
            
            if paper_data:
                enriched_result = {
                    **result,
                    "title": paper_data.get("title", "Unknown"),
                    "abstract": paper_data.get("abstract", ""),
                    "content": self._get_section_content(paper_data, result["section_name"])
                }
                enriched_results.append(enriched_result)
        
        return enriched_results
    
    def _get_section_content(self, paper_data: Dict, section_name: str) -> str:
        """Get content for a specific section"""
        if section_name == "abstract":
            return paper_data.get("abstract", "")
        
        sections = paper_data.get("sections", {})
        return sections.get(section_name, "Section not found")
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get complete paper details"""
        return self.rocksdb_manager.get_paper(paper_id)
    
    def list_available_papers(self) -> List[str]:
        """List all available paper IDs"""
        return self.rocksdb_manager.list_papers()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        stats = {
            "total_papers": len(self.list_available_papers()),
            "faiss_vectors": self.faiss_manager.index.ntotal if self.faiss_manager.index else 0,
            "data_directory": str(self.data_dir)
        }
        return stats


# Legacy function for backward compatibility
def search_similar_papers(query_vector: List[float], k: int = 3) -> List[Dict[str, Any]]:
    """Legacy search function for backward compatibility"""
    engine = ArxivSearchEngine()
    return engine.search_by_embedding(query_vector, k)


if __name__ == "__main__":
    # Example usage
    engine = ArxivSearchEngine()
    
    # Test search
    results = engine.search_by_text("machine learning neural networks", k=3)
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Title: {result.get('title', 'Unknown')}")
        print(f"  Paper ID: {result['paper_id']}")
        print(f"  Section: {result['section_name']}")
        print(f"  Similarity: {result['similarity_score']:.3f}")
        print(f"  Content: {result['content'][:200]}...")
        print()