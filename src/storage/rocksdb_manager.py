"""
RocksDB Manager for fast key-value storage of paper metadata
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class RocksDBManager:
    """Manages RocksDB operations for paper metadata storage"""
    
    def __init__(self, db_path: str = "data/rocksdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to RocksDB"""
        try:
            from rocksdict import Rdict  # type: ignore
            self.db = Rdict(str(self.db_path))
        except ImportError:
            print("Warning: rocksdict not installed. Using file-based storage as fallback.")
            self.db = None
    
    def store_paper(self, paper_id: str, paper_data: Dict[str, Any]):
        """Store paper metadata"""
        if self.db is not None:
            self.db[paper_id] = json.dumps(paper_data)
        else:
            # Fallback to file storage
            file_path = self.db_path.parent / f"{paper_id}.json"
            with open(file_path, 'w') as f:
                json.dump(paper_data, f, indent=2)
    
    def get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve paper metadata"""
        if self.db is not None:
            data = self.db.get(paper_id)
            return json.loads(data) if data else None
        else:
            # Fallback to file storage
            file_path = self.db_path.parent / f"{paper_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
    
    def store_multiple(self, papers_data: Dict[str, Dict[str, Any]]):
        """Store multiple papers"""
        for paper_id, paper_data in papers_data.items():
            self.store_paper(paper_id, paper_data)
    
    def list_papers(self):
        """List all stored paper IDs"""
        if self.db is not None:
            return list(self.db.keys())
        else:
            # Fallback to file storage
            json_files = list(self.db_path.parent.glob("*.json"))
            return [f.stem for f in json_files]
    
    def close(self):
        """Close the database connection"""
        if self.db is not None:
            self.db.close()


def load_papers_from_json(json_file: str, db_path: str = "data/rocksdb") -> RocksDBManager:
    """Load papers from JSON file into RocksDB"""
    manager = RocksDBManager(db_path)
    
    with open(json_file, 'r') as f:
        papers_data = json.load(f)
    
    manager.store_multiple(papers_data)
    print(f"Loaded {len(papers_data)} papers into RocksDB")
    
    return manager


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load papers into RocksDB")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with papers")
    parser.add_argument("--db", "-d", default="data/rocksdb", help="RocksDB path")
    
    args = parser.parse_args()
    
    manager = load_papers_from_json(args.input, args.db)
    print(f"RocksDB initialized with {len(manager.list_papers())} papers")