import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pandas as pd
except ImportError:
    pd = None


class DocumentProcessor:
    """Simple document processor for various file types."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Process a single file and return document chunks.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            List of document chunks with metadata
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return []
            
            # Determine file type and process accordingly
            suffix = file_path.suffix.lower()
            
            if suffix == '.pdf':
                return self._process_pdf(file_path)
            elif suffix == '.txt':
                return self._process_txt(file_path)
            elif suffix == '.md':
                return self._process_txt(file_path)  # Treat markdown as text
            elif suffix == '.csv':
                return self._process_csv(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {suffix}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return []
    
    def _process_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process PDF file."""
        if PyPDF2 is None:
            self.logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return []
        
        try:
            documents = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():
                        documents.append({
                            'text': text.strip(),
                            'metadata': {
                                'source_file': str(file_path),
                                'page_number': page_num + 1,
                                'file_type': 'pdf',
                                'total_pages': len(pdf_reader.pages)
                            }
                        })
            
            self.logger.info(f"Extracted {len(documents)} pages from {file_path.name}")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {file_path}: {e}")
            return []
    
    def _process_txt(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            if content.strip():
                return [{
                    'text': content.strip(),
                    'metadata': {
                        'source_file': str(file_path),
                        'file_type': 'text'
                    }
                }]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error processing text file {file_path}: {e}")
            return []
    
    def _process_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process CSV file."""
        if pd is None:
            self.logger.error("pandas not installed. Install with: pip install pandas")
            return []
        
        try:
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to text representation
            text_content = f"CSV File: {file_path.name}\n\n"
            text_content += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n\n"
            text_content += f"Columns: {', '.join(df.columns.tolist())}\n\n"
            text_content += "Data Sample:\n"
            text_content += df.head(10).to_string(index=False)
            
            if len(df) > 10:
                text_content += f"\n\n... and {len(df) - 10} more rows"
            
            return [{
                'text': text_content,
                'metadata': {
                    'source_file': str(file_path),
                    'file_type': 'csv',
                    'rows': len(df),
                    'columns': len(df.columns)
                }
            }]
            
        except Exception as e:
            self.logger.error(f"Error processing CSV {file_path}: {e}")
            return []
    
    def process_directory(self, directory: Path, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Process all supported files in a directory.
        
        Args:
            directory: Directory to process
            recursive: Whether to process subdirectories
            
        Returns:
            List of all document chunks
        """
        directory = Path(directory)
        
        if not directory.exists():
            self.logger.error(f"Directory not found: {directory}")
            return []
        
        all_documents = []
        supported_extensions = {'.pdf', '.txt', '.md', '.csv'}
        
        # Get file pattern based on recursive setting
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                documents = self.process_file(file_path)
                all_documents.extend(documents)
        
        self.logger.info(f"Processed {len(all_documents)} documents from {directory}")
        return all_documents
    
    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            
            # Prevent infinite loop
            if start >= end:
                start = end
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, Any]], 
                       chunk_size: int = 800, overlap: int = 120) -> List[Dict[str, Any]]:
        """
        Chunk all documents into smaller pieces.
        
        Args:
            documents: List of documents to chunk
            chunk_size: Maximum chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of chunked documents
        """
        chunked_docs = []
        
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', {})
            
            chunks = self.chunk_text(text, chunk_size, overlap)
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['total_chunks'] = len(chunks)
                chunk_metadata['text'] = chunk
                
                chunked_docs.append({
                    'text': chunk,
                    'metadata': chunk_metadata
                })
        
        return chunked_docs
