import os
import tempfile
from typing import Optional
import PyPDF2
import docx
from fastapi import UploadFile, HTTPException
import logging
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    async def process_uploaded_file(self, file: UploadFile) -> str:
        """
        Process uploaded file and extract text content with proper format handling
        """
        content_type = file.content_type
        filename = file.filename.lower()
        
        # Validate file type
        if not self._is_supported_file_type(content_type, filename):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Please upload PDF, Word, or text files."
            )
        
        try:
            # Read file content
            file_content = await file.read()
            
            # Process based on file type
            if filename.endswith('.pdf'):
                return self._extract_text_from_pdf(file_content)
            elif filename.endswith(('.doc', '.docx')):
                return self._extract_text_from_docx(file_content)
            elif filename.endswith('.txt') or 'text' in (content_type or ''):
                return file_content.decode('utf-8')
            else:
                raise HTTPException(
                    status_code=400, 
                    detail="Unsupported file type. Please upload PDF, Word, or text files."
                )
                
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process document: {str(e)}"
            )
    
    def _is_supported_file_type(self, content_type: Optional[str], filename: str) -> bool:
        """Check if file type is supported"""
        supported_extensions = ['.pdf', '.doc', '.docx', '.txt']
        supported_content_types = [
            'application/pdf', 
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        
        return (any(filename.endswith(ext) for ext in supported_extensions) or
                any(ct in (content_type or '') for ct in supported_content_types))
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from Word document using python-docx"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Word document extraction failed: {str(e)}")