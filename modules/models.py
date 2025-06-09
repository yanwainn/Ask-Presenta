"""
Data models for the PDF to Presentation application.
"""
from pydantic import BaseModel
from typing import List, Optional

class KeySection(BaseModel):
    """Represents a key section extracted from a document."""
    title: str
    content: str
    importance: int
    themes: List[str]
    visual_elements: List[str]

class ContentExtractionResult(BaseModel):
    """Results from content extraction process."""
    document_title: str
    summary: str
    key_sections: List[KeySection]
    overall_themes: List[str]

class VisualPrompt(BaseModel):
    """Prompt for image generation."""
    section_title: str
    prompt: str
    style_guidance: str
    avoid_elements: List[str]
    reference_section: str

class ImageInfo(BaseModel):
    """Information about a generated image."""
    file_path: str
    file_name: str
    base64_data: str
    width: int
    height: int

class HTMLSlide(BaseModel):
    """Represents an HTML slide."""
    html_content: str
    title: str
    section_title: str
    section_content: str

# Bosch Brand Colors
BOSCH_COLORS = {
    "primary": "#E20015",  # Bosch Red
    "black": "#000000",
    "white": "#FFFFFF",
    "dark_gray": "#333333",
    "medium_gray": "#7D7D7D",
    "light_gray": "#E5E5E5",
    "secondary_blue": "#007BC0",
    "secondary_green": "#00884A"
}