"""Example test file for CV parser."""
import pytest
from cv_analyzer.parsers.cv_parser import CVParser


def test_parse_txt():
    """Test parsing TXT file."""
    parser = CVParser()
    text_content = b"John Doe\nSoftware Engineer\nPython, JavaScript"
    result = parser.parse(text_content, "test.txt")
    assert "raw_text" in result
    assert "normalized_text" in result
    assert "sections" in result
