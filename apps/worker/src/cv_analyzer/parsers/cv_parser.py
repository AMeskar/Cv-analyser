"""CV parsing utilities."""
import io
from typing import Dict, Any
from pathlib import Path
import PyPDF2
from docx import Document
from cv_analyzer.core.logging import get_logger

logger = get_logger(__name__)


class CVParser:
    """Parser for CV files (PDF, DOCX, TXT)."""
    
    @staticmethod
    def parse(file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse CV file and extract text.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            
        Returns:
            Parsed CV data
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext == ".pdf":
            text = CVParser._parse_pdf(file_data)
        elif file_ext == ".docx":
            text = CVParser._parse_docx(file_data)
        elif file_ext == ".txt":
            text = file_data.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Normalize text
        normalized = CVParser._normalize_text(text)
        
        # Extract sections
        sections = CVParser._extract_sections(normalized)
        
        return {
            "raw_text": text,
            "normalized_text": normalized,
            "sections": sections,
            "filename": filename,
        }
    
    @staticmethod
    def _parse_pdf(file_data: bytes) -> str:
        """Extract text from PDF."""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text())
            return "\n".join(text_parts)
        except Exception as e:
            logger.error("pdf_parse_failed", error=str(e))
            raise
    
    @staticmethod
    def _parse_docx(file_data: bytes) -> str:
        """Extract text from DOCX."""
        try:
            doc_file = io.BytesIO(file_data)
            doc = Document(doc_file)
            text_parts = []
            for paragraph in doc.paragraphs:
                text_parts.append(paragraph.text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error("docx_parse_failed", error=str(e))
            raise
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text (remove extra whitespace, etc.)."""
        # Remove excessive whitespace
        lines = text.split("\n")
        normalized_lines = []
        for line in lines:
            line = line.strip()
            if line:
                normalized_lines.append(line)
        return "\n".join(normalized_lines)
    
    @staticmethod
    def _extract_sections(text: str) -> Dict[str, str]:
        """Extract CV sections (basic implementation)."""
        sections = {
            "header": "",
            "experience": "",
            "education": "",
            "skills": "",
            "other": "",
        }
        
        # Simple section detection (can be enhanced with ML/NLP)
        lines = text.split("\n")
        current_section = "other"
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["experience", "work", "employment"]):
                current_section = "experience"
            elif any(keyword in line_lower for keyword in ["education", "academic", "degree"]):
                current_section = "education"
            elif any(keyword in line_lower for keyword in ["skills", "competencies", "technologies"]):
                current_section = "skills"
            elif any(keyword in line_lower for keyword in ["name", "email", "phone", "contact"]):
                current_section = "header"
            else:
                sections[current_section] += line + "\n"
        
        return sections
