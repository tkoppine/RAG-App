"""
FAISS Index Manager for efficient similarity search
"""
import json
import numpy as np
import faiss
import os
from typing import Dict, List, Any, Tuple
from pathlib import Path


class FAISSManager:
    """Manages FAISS index operations for document embeddings"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.index_file = self.data_dir / "faiss_index.idx"
        self.mapping_file = self.data_dir / "embeddings_mapping.json"
        self.index = None
        self.paper_map = {}
        
    def create_index(self, embedding_dim: int) -> faiss.Index:
        """Create a new FAISS index"""
        self.index = faiss.IndexFlatL2(embedding_dim)
        return self.index
    
    def load_index(self) -> faiss.Index:
        """Load existing FAISS index from file"""
        if self.index_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            return self.index
        else:
            raise FileNotFoundError(f"FAISS index not found at {self.index_file}")
    
    def save_index(self):
        """Save FAISS index to file"""
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_file))
            print(f"FAISS index saved to {self.index_file}")
        else:
            raise ValueError("No index to save. Create or load an index first.")
    
    def load_mapping(self) -> Dict:
        """Load paper mapping from file"""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r') as f:
                self.paper_map = json.load(f)
            return self.paper_map
        else:
            raise FileNotFoundError(f"Mapping file not found at {self.mapping_file}")
    
    def save_mapping(self):
        """Save paper mapping to file"""
        with open(self.mapping_file, 'w') as f:
            json.dump(self.paper_map, f, indent=2)
        print(f"Mapping saved to {self.mapping_file}")
    
    def add_embeddings(self, embeddings_data: Dict[str, Dict[str, List[float]]]):
        """Add embeddings to FAISS index and create mapping"""
        if self.index is None:
            # Auto-detect embedding dimension
            first_embedding = next(iter(next(iter(embeddings_data.values())).values()))
            embedding_dim = len(first_embedding)
            self.create_index(embedding_dim)
        
        id_counter = len(self.paper_map)
        
        for paper_id, sections in embeddings_data.items():
            for section_name, embedding in sections.items():
                if isinstance(embedding, list):
                    vector = np.array(embedding, dtype='float32')
                    self.index.add(np.expand_dims(vector, axis=0))
                    
                    self.paper_map[id_counter] = {
                        "paper_id": paper_id,
                        "section_name": section_name,
                        "vector": vector.tolist()
                    }
                    id_counter += 1
        
        return id_counter
    
    def search_similar(self, query_vector: List[float], k: int = 5) -> List[Dict]:
        """Search for similar embeddings"""
        if self.index is None:
            self.load_index()
        
        if not self.paper_map:
            self.load_mapping()
        
        query_vector = np.array(query_vector, dtype='float32').reshape(1, -1)
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i in range(k):
            idx = indices[0][i]
            if idx != -1 and str(idx) in self.paper_map:
                result = self.paper_map[str(idx)]
                results.append({
                    "paper_id": result["paper_id"],
                    "section_name": result["section_name"],
                    "distance": float(distances[0][i]),
                    "similarity_score": 1.0 / (1.0 + distances[0][i])
                })
        
        return results


def build_index_from_json(json_file: str, output_dir: str = "data") -> FAISSManager:
    """Build FAISS index from JSON embeddings file"""
    manager = FAISSManager(output_dir)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    manager.add_embeddings(data)
    manager.save_index()
    manager.save_mapping()
    
    return manager


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build FAISS index from embeddings")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with embeddings")
    parser.add_argument("--output", "-o", default="data", help="Output directory for index files")
    
    args = parser.parse_args()
    
    manager = build_index_from_json(args.input, args.output)
    print(f"FAISS index built successfully with {manager.index.ntotal} vectors")