#!/usr/bin/env python3
"""
Simple script to build the vector index from documents in the data directory.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from AI_Systems.utils.vector_store import VectorStore
from AI_Systems.utils.document_processor import DocumentProcessor
from Configuration.config import *
import logging

def build_index():
    """Build the vector index from documents in the data directory."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize components
    doc_processor = DocumentProcessor()
    vector_store = VectorStore(
        embed_model=EMBED_MODEL,
        vector_dir=VECTOR_DIR
    )
    
    # Clear existing index
    vector_store.clear_index()
    logger.info("Cleared existing vector index")
    
    # Process documents from data directory
    data_dir = Path(DATA_DIR)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return False
    
    logger.info(f"Processing documents from: {data_dir}")
    
    # Process all documents
    all_documents = doc_processor.process_directory(data_dir, recursive=True)
    
    if not all_documents:
        logger.warning("No documents found to process")
        return False
    
    logger.info(f"Found {len(all_documents)} documents")
    
    # Chunk documents
    chunked_docs = doc_processor.chunk_documents(
        all_documents, 
        chunk_size=CHUNK_SIZE, 
        overlap=CHUNK_OVERLAP
    )
    
    logger.info(f"Created {len(chunked_docs)} chunks")
    
    # Add to vector store
    success = vector_store.add_documents(chunked_docs)
    
    if success:
        # Save the index
        if vector_store.save_index():
            logger.info("Successfully built and saved vector index")
            
            # Print statistics
            stats = vector_store.get_stats()
            logger.info(f"Index statistics:")
            logger.info(f"  - Total documents: {stats['total_documents']}")
            logger.info(f"  - Embedding model: {stats['model']}")
            logger.info(f"  - Embedding dimension: {stats['embedding_dim']}")
            
            return True
        else:
            logger.error("Failed to save vector index")
            return False
    else:
        logger.error("Failed to add documents to vector store")
        return False

def main():
    """Main function."""
    try:
        success = build_index()
        if success:
            print("\n✅ Vector index built successfully!")
            print("You can now run the RAG system using: python -m utils.rag")
        else:
            print("\n❌ Failed to build vector index")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error building index: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
