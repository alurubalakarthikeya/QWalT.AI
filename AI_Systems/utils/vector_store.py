import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import hashlib

try:
    import faiss
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import openai
except ImportError:
    openai = None


class VectorStore:
    """
    Vector store implementation using FAISS for similarity search.
    Supports both local sentence transformers and OpenAI embeddings.
    """
    
    def __init__(self, embed_model: str, vector_dir: str):
        """
        Initialize the vector store.
        
        Args:
            embed_model: Embedding model name
            vector_dir: Directory to store vector index and metadata
        """
        self.embed_model = embed_model
        self.vector_dir = Path(vector_dir)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize embedding model
        self.embedder = None
        self.embedding_dim = None
        self.is_openai_model = "text-embedding" in embed_model.lower()
        
        # FAISS index
        self.index = None
        self.metadata = []
        self.doc_ids = []
        
        # File paths
        self.index_path = self.vector_dir / "faiss_index.bin"
        self.metadata_path = self.vector_dir / "metadata.pkl"
        self.config_path = self.vector_dir / "config.pkl"
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self._initialize_embedder()
    
    def _initialize_embedder(self):
        """Initialize the embedding model."""
        try:
            if self.is_openai_model:
                if openai is None:
                    raise ImportError("OpenAI library not installed. Install with: pip install openai")
                self.embedding_dim = 1536  # Default for OpenAI text-embedding models
                self.logger.info(f"Using OpenAI embedding model: {self.embed_model}")
            else:
                if SentenceTransformer is None:
                    raise ImportError("sentence-transformers library not installed. Install with: pip install sentence-transformers")
                self.embedder = SentenceTransformer(self.embed_model)
                # Get embedding dimension by encoding a test string
                test_embedding = self.embedder.encode(["test"])
                self.embedding_dim = test_embedding.shape[1]
                self.logger.info(f"Using sentence transformer: {self.embed_model}, dim: {self.embedding_dim}")
        except Exception as e:
            self.logger.error(f"Failed to initialize embedder: {e}")
            raise
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text."""
        try:
            if self.is_openai_model:
                response = openai.embeddings.create(
                    model=self.embed_model,
                    input=text
                )
                return np.array(response.data[0].embedding, dtype=np.float32)
            else:
                return self.embedder.encode([text])[0].astype(np.float32)
        except Exception as e:
            self.logger.error(f"Error getting embedding: {e}")
            raise
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Get embeddings for multiple texts."""
        try:
            if self.is_openai_model:
                response = openai.embeddings.create(
                    model=self.embed_model,
                    input=texts
                )
                embeddings = [np.array(item.embedding, dtype=np.float32) for item in response.data]
                return np.vstack(embeddings)
            else:
                return self.embedder.encode(texts).astype(np.float32)
        except Exception as e:
            self.logger.error(f"Error getting embeddings: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add multiple documents to the vector store.
        
        Args:
            documents: List of documents with 'text' and optional 'metadata'
            
        Returns:
            True if successful
        """
        try:
            if not documents:
                return True
            
            # Extract texts and prepare metadata
            texts = []
            doc_metadata = []
            doc_ids = []
            
            for doc in documents:
                text = doc.get('text', '')
                if not text.strip():
                    continue
                
                texts.append(text)
                
                # Create document ID
                doc_id = doc.get('doc_id') or hashlib.md5(text.encode()).hexdigest()
                doc_ids.append(doc_id)
                
                # Prepare metadata
                metadata = doc.get('metadata', {})
                metadata['text'] = text
                metadata['doc_id'] = doc_id
                doc_metadata.append(metadata)
            
            if not texts:
                self.logger.warning("No valid texts found in documents")
                return False
            
            # Get embeddings
            self.logger.info(f"Getting embeddings for {len(texts)} documents...")
            embeddings = self._get_embeddings(texts)
            
            # Initialize FAISS index if needed
            if self.index is None:
                if faiss is None:
                    raise ImportError("FAISS library not installed. Install with: pip install faiss-cpu")
                self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.extend(doc_metadata)
            self.doc_ids.extend(doc_ids)
            
            self.logger.info(f"Added {len(texts)} documents to vector store")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar documents with scores
        """
        try:
            if self.index is None or self.index.ntotal == 0:
                self.logger.warning("Vector index is empty")
                return []
            
            # Get query embedding
            query_embedding = self._get_embedding(query)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.metadata):
                    results.append({
                        'score': float(score),
                        'doc_id': self.doc_ids[idx],
                        'metadata': self.metadata[idx].copy()
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            return []
    
    def save_index(self) -> bool:
        """Save the vector index and metadata to disk."""
        try:
            if self.index is None:
                self.logger.warning("No index to save")
                return False
            
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            with open(self.metadata_path, 'wb') as f:
                pickle.dump({
                    'metadata': self.metadata,
                    'doc_ids': self.doc_ids
                }, f)
            
            # Save config
            config = {
                'embed_model': self.embed_model,
                'embedding_dim': self.embedding_dim,
                'is_openai_model': self.is_openai_model,
                'total_documents': len(self.metadata)
            }
            with open(self.config_path, 'wb') as f:
                pickle.dump(config, f)
            
            self.logger.info(f"Saved index with {len(self.metadata)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving index: {e}")
            return False
    
    def load_index(self) -> bool:
        """Load the vector index and metadata from disk."""
        try:
            if not all(p.exists() for p in [self.index_path, self.metadata_path, self.config_path]):
                self.logger.info("Index files not found")
                return False
            
            # Load config
            with open(self.config_path, 'rb') as f:
                config = pickle.load(f)
            
            # Verify compatibility
            if config['embed_model'] != self.embed_model:
                self.logger.warning(f"Model mismatch: {config['embed_model']} vs {self.embed_model}")
                return False
            
            # Load FAISS index
            if faiss is None:
                raise ImportError("FAISS library not installed")
            
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data['metadata']
                self.doc_ids = data['doc_ids']
            
            self.logger.info(f"Loaded index with {len(self.metadata)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.metadata),
            'index_size': self.index.ntotal if self.index else 0,
            'model': self.embed_model,
            'embedding_dim': self.embedding_dim,
            'is_openai_model': self.is_openai_model
        }
    
    def clear_index(self) -> bool:
        """Clear the vector index and metadata."""
        try:
            self.index = None
            self.metadata = []
            self.doc_ids = []
            
            # Remove files
            for path in [self.index_path, self.metadata_path, self.config_path]:
                if path.exists():
                    path.unlink()
            
            self.logger.info("Cleared vector store")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing index: {e}")
            return False
