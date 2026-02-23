import os
from typing import List, BinaryIO
from pathlib import Path
import PyPDF2
from docx import Document as DocxDocument
from app.config import settings
from loguru import logger


class DocumentProcessor:
    """Service for processing different document types"""
    
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
    
    def process_file(self, file_path: str) -> str:
        """Process file and extract text based on file type"""
        extension = Path(file_path).suffix.lower()
        
        try:
            if extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif extension in ['.txt']:
                return self._extract_txt_text(file_path)
            elif extension in ['.doc', '.docx']:
                return self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {extension}")
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.debug(f"Extracted page {page_num + 1}/{len(pdf_reader.pages)}")
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            logger.info(f"Extracted {len(text)} characters from TXT")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            raise
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            logger.info(f"Extracted {len(text)} characters from DOCX")
            return text.strip()
        
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise
    
    def chunk_text(self, text: str, metadata: dict = None) -> List[dict]:
        """
        Split text into overlapping chunks
        
        Chunking Strategy:
        - Fixed size chunks with overlap
        - Overlap helps maintain context between chunks
        - Metadata is preserved for each chunk
        """
        chunks = []
        start = 0
        text_length = len(text)
        chunk_index = 0
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence boundary (period followed by space)
                sentence_end = text.rfind('. ', start, end)
                if sentence_end != -1 and sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary (space)
                    word_end = text.rfind(' ', start, end)
                    if word_end != -1 and word_end > start + self.chunk_size // 2:
                        end = word_end
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "metadata": metadata or {}
                }
                chunks.append(chunk)
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap if end < text_length else end
        
        logger.info(f"Created {len(chunks)} chunks from text (length: {text_length})")
        return chunks


document_processor = DocumentProcessor()
