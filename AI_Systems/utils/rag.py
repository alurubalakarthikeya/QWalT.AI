import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import re

# Import your vector store
from AI_Systems.utils.vector_store import VectorStore
from config import *

# Try to import smart query processor
try:
    from AI_Systems.utils.smart_query_processor import SmartQueryProcessor
    SMART_PROCESSOR_AVAILABLE = True
except ImportError:
    SMART_PROCESSOR_AVAILABLE = False

class RAGSystem:
    """
    Retrieval-Augmented Generation system using VectorStore for retrieval
    and OpenAI/LLM for generation.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the RAG system."""
        self.config = config or self._load_default_config()
        
        # Initialize vector store
        self.vector_store = VectorStore(
            embed_model=self.config.get('EMBED_MODEL', EMBED_MODEL),
            vector_dir=self.config.get('VECTOR_DIR', VECTOR_DIR)
        )
        
        # Load existing index
        if not self.vector_store.load_index():
            logging.warning("No existing vector index found. Please build index first.")
        
        # Initialize smart query processor
        if SMART_PROCESSOR_AVAILABLE:
            self.smart_processor = SmartQueryProcessor()
            self.smart_mode = True
        else:
            self.smart_processor = None
            self.smart_mode = False
        
        # Initialize OpenAI client (optional for free mode)
        api_key = self.config.get('OPENAI_API_KEY', OPENAI_API_KEY)
        use_openai = self.config.get('USE_OPENAI', True)
        
        if use_openai and api_key and not api_key.startswith('sk-abcdef') and api_key != "disabled":
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.use_openai = True
                logging.info("OpenAI client initialized successfully")
            except Exception as e:
                logging.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
                self.use_openai = False
        else:
            self.openai_client = None
            self.use_openai = False
            logging.info("Running in FREE mode - using built-in knowledge base only")
        
        # RAG parameters
        self.top_k = self.config.get('TOP_K', TOP_K)
        self.llm_model = self.config.get('LLM_MODEL', LLM_MODEL)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration from config.py"""
        return {
            'VECTOR_DIR': VECTOR_DIR,
            'EMBED_MODEL': EMBED_MODEL,
            'LLM_MODEL': LLM_MODEL,
            'TOP_K': TOP_K,
            'OPENAI_API_KEY': OPENAI_API_KEY
        }
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for the query.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata
        """
        if top_k is None:
            top_k = self.top_k
            
        try:
            results = self.vector_store.search(query, top_k=top_k)
            self.logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
            return results
        except Exception as e:
            self.logger.error(f"Error during retrieval: {e}")
            return []
    
    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context for the LLM.
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return "No relevant information found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            metadata = doc.get('metadata', {})
            text = metadata.get('text', '')
            source = metadata.get('source_file', 'Unknown source')
            score = doc.get('score', 0.0)
            
            context_parts.append(
                f"Document {i} (Relevance: {score:.3f}, Source: {Path(source).name}):\n{text}\n"
            )
        
        return "\n" + "="*50 + "\n".join(context_parts) + "="*50 + "\n"
    
    def generate_response(self, query: str, context: str) -> str:
        """
        Generate response using LLM with retrieved context.
        In free mode, return formatted context directly.
        
        Args:
            query: User query
            context: Retrieved and formatted context
            
        Returns:
            Generated response
        """
        try:
            if self.use_openai and self.openai_client:
                # Use OpenAI API
                system_prompt = """You are a helpful AI assistant. Use the provided context to answer the user's question accurately and comprehensively. 

Guidelines:
- Base your answer primarily on the provided context
- If the context doesn't contain enough information, say so clearly
- Cite specific sources when possible
- Be concise but thorough
- If you're uncertain about something, express that uncertainty"""

                user_prompt = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""

                # Call OpenAI API
                response = self.openai_client.chat.completions.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=1000
                )
                
                return response.choices[0].message.content.strip()
            else:
                # Free mode - return formatted context with simple analysis
                return f"""**Based on your documents, here's what I found:**

{context}

**Summary:** The above information from your knowledge base documents contains relevant content for your query: "{query}". This response is generated from your local document collection without using external APIs.

💡 *Note: Running in FREE mode using local document search only.*"""
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            # In case of error, return context directly
            return f"""**I found relevant information in your documents:**

{context}

*Note: There was an issue with AI processing, but the above information from your documents should help answer your question about: "{query}"*"""
    
    def query(self, user_query: str, top_k: int = None, include_sources: bool = True) -> Dict[str, Any]:
        """
        Main RAG query method - retrieve and generate.
        
        Args:
            user_query: User's question
            top_k: Number of documents to retrieve
            include_sources: Whether to include source information in response
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.retrieve(user_query, top_k)
            
            if not retrieved_docs:
                return {
                    'response': "I couldn't find any relevant information to answer your question. Please try rephrasing your query or check if the knowledge base contains information about this topic.",
                    'sources': [],
                    'retrieved_docs': []
                }
            
            # Step 2: Format context
            context = self.format_context(retrieved_docs)
            
            # Step 3: Generate response
            response = self.generate_response(user_query, context)
            
            # Step 4: Prepare sources information
            sources = []
            if include_sources:
                for doc in retrieved_docs:
                    metadata = doc.get('metadata', {})
                    sources.append({
                        'source_file': metadata.get('source_file', 'Unknown'),
                        'score': doc.get('score', 0.0),
                        'doc_id': doc.get('doc_id', ''),
                        'chunk_preview': metadata.get('text', '')[:200] + "..." if len(metadata.get('text', '')) > 200 else metadata.get('text', '')
                    })
            
            return {
                'response': response,
                'sources': sources,
                'retrieved_docs': retrieved_docs,
                'query': user_query
            }
            
        except Exception as e:
            self.logger.error(f"Error in RAG query: {e}")
            return {
                'response': f"An error occurred while processing your query: {str(e)}",
                'sources': [],
                'retrieved_docs': []
            }
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a new document to the knowledge base.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            True if successful
        """
        try:
            # Prepare document
            doc = {
                'text': content,
                'metadata': metadata or {}
            }
            
            # Add to vector store
            success = self.vector_store.add_documents([doc])
            
            if success:
                # Save the updated index
                self.vector_store.save_index()
                self.logger.info("Document added and index saved")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error adding document: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        return {
            'vector_store_stats': self.vector_store.get_stats(),
            'config': {
                'top_k': self.top_k,
                'llm_model': self.llm_model,
                'embed_model': EMBED_MODEL
            }
        }
    
    def chat(self):
        """Interactive chat interface for testing."""
        print("RAG System Chat Interface")
        print("Type 'quit' to exit, 'stats' for system statistics")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'stats':
                    stats = self.get_stats()
                    print(f"\nSystem Statistics:")
                    print(f"- Total documents: {stats['vector_store_stats']['total_documents']}")
                    print(f"- Index size: {stats['vector_store_stats']['index_size']}")
                    print(f"- Model: {stats['vector_store_stats']['model']}")
                    continue
                
                if not user_input:
                    continue
                
                print("\nSearching knowledge base...")
                result = self.query(user_input)
                
                print(f"\nAssistant: {result['response']}")
                
                if result['sources']:
                    print(f"\nSources ({len(result['sources'])}):")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"{i}. {Path(source['source_file']).name} (Score: {source['score']:.3f})")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function to run the RAG system."""
    # Initialize RAG system
    rag = RAGSystem()
    
    # Check if index is loaded
    stats = rag.get_stats()
    if stats['vector_store_stats']['total_documents'] == 0:
        print("No documents found in vector store. Please build the index first using build_index.py")
        return
    
    print(f"RAG system initialized with {stats['vector_store_stats']['total_documents']} documents")
    
    # Start interactive chat
    rag.chat()


if __name__ == "__main__":
    main()