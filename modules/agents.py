"""
OpenAI agent definitions and configurations.
"""
import os
from agents import Agent, Runner
from openai import AsyncAzureOpenAI
from modules.models import ContentExtractionResult, VisualPrompt

def create_content_extraction_agent():
    """
    Agent to extract key sections from the PDF.
    
    Returns:
        Agent: Content extraction agent
    """
    extraction_instructions = """Extract 3-7 key sections from this document that would be excellent for presentation slides.
    For each section:
    1. Create a clear title
    2. Extract/summarize essential content (200-300 words max)
    3. Rate importance (1-10)
    4. Identify 3-5 key themes
    5. List 3-7 visual elements for an image
    
    Also provide:
    - Document title
    - Brief document summary (3-5 sentences)
    - 3-5 overall themes
    
    Focus on sections with clear visual potential that would work well for presentation slides.
    """

    return Agent(
        name="ContentExtractionAgent",
        instructions=extraction_instructions,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        output_type=ContentExtractionResult
    )

def create_visual_prompt_agent():
    """
    Agent to create DALL-E prompts.
    
    Returns:
        Agent: Visual prompt generation agent
    """
    prompt_instructions = """Create a premium photorealistic image prompt for DALL-E 3.
    Your prompt must:
    1. Be highly detailed and specific
    2. Specify photorealistic style (not cartoon/illustration)
    3. Include lighting, perspective, atmosphere details
    4. Focus on visual elements only (NO text/diagrams)
    5. Be under 200 words
    
    Also provide:
    1. Style guidance: Photography/artistic styles
    2. Elements to avoid: 3-5 things to exclude
    
    IMPORTANT:
    - NEVER include text in the image
    - Focus on physical, tangible elements
    - Create prompt for a SINGLE cohesive image
    """

    return Agent(
        name="VisualPromptAgent",
        instructions=prompt_instructions,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        output_type=VisualPrompt
    )

async def extract_key_sections(pdf_text):
    """
    Extract key sections from PDF text.
    
    Args:
        pdf_text (str): Text extracted from PDF
        
    Returns:
        ContentExtractionResult: Extraction results
    """
    extraction_agent = create_content_extraction_agent()
    
    if len(pdf_text) > 25000:
        pdf_text = pdf_text[:25000] + "\n\n[Content truncated due to length]"
    
    result = await Runner.run(extraction_agent, f"Document Content:\n\n{pdf_text}")
    return result.final_output

async def extract_key_bullet_points(section, document_title):
    """
    Extract concise bullet points from section content.
    
    Args:
        section: Section to extract bullet points from
        document_title (str): Document title
        
    Returns:
        list: List of bullet points
    """
    # Use GPT directly for speed rather than the Agents framework
    client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    
    # Create the prompt for bullet point extraction
    prompt = f"""Extract 3-5 extremely concise bullet points (5-10 words each) from this content.
Each bullet point should capture a key insight using active, impactful language.

SECTION TITLE: {section.title}

CONTENT:
{section.content}

KEY THEMES: {', '.join(section.themes)}

Format your response as a simple Python list of strings, like this:
["First bullet point", "Second bullet point", "Third bullet point"]

Make each bullet point extremely concise, starting with action verbs when possible.
Focus on the most important facts, insights, or takeaways.
"""
    
    try:
        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for more focused, consistent output
            max_tokens=300
        )
        
        # Extract the list of bullet points from the response
        bullet_points_text = response.choices[0].message.content.strip()
        
        # Try to parse as a Python list
        try:
            # Use a safer alternative to eval
            import ast
            bullet_points = ast.literal_eval(bullet_points_text)
            
            # Make sure we got a list
            if not isinstance(bullet_points, list):
                raise ValueError("Response is not a list")
                
            # Ensure all elements are strings
            bullet_points = [str(point) for point in bullet_points]
            
            # Limit to 5 bullet points maximum
            bullet_points = bullet_points[:5]
            
            return bullet_points
            
        except (SyntaxError, ValueError) as e:
            # Fallback if we can't parse the list - manually extract bullet points
            print(f"Error parsing bullet points: {e}")
            
            # Try to extract bullet points with regex
            import re
            bullet_pattern = r'"([^"]+)"'
            bullet_points = re.findall(bullet_pattern, bullet_points_text)
            
            if not bullet_points:
                # Try alternative pattern for non-quoted bullet points
                bullet_pattern = r'\[\s*(.+?)\s*\]'
                bullet_match = re.search(bullet_pattern, bullet_points_text)
                if bullet_match:
                    # Split by commas
                    bullet_points = [bp.strip().strip('"\'') for bp in bullet_match.group(1).split(',')]
            
            if not bullet_points:
                # Last resort - split by new lines and look for common bullet markers
                lines = bullet_points_text.split('\n')
                bullet_points = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*') or (line.startswith('[') and ']' in line):
                        # Clean up the bullet point
                        cleaned = line.lstrip('-*[] ').rstrip(']').strip()
                        if cleaned:
                            bullet_points.append(cleaned)
            
            # If we still don't have bullet points, create basic ones from themes
            if not bullet_points and section.themes:
                bullet_points = [f"Explores {theme}" for theme in section.themes[:5]]
            
            # Final fallback
            if not bullet_points:
                # Create some generic bullet points based on the title
                bullet_points = [
                    f"Highlights key aspects of {section.title}",
                    f"Provides essential insights",
                    f"Establishes important context"
                ]
            
            return bullet_points[:5]  # Limit to 5 bullet points
            
    except Exception as e:
        print(f"Error extracting bullet points: {str(e)}")
        # If all else fails, provide generic bullet points
        return [
            f"Explores {section.title}",
            "Provides essential insights",
            "Highlights key information"
        ]

async def create_visual_prompt(section, document_title):
    """
    Create image prompt for a section.
    
    Args:
        section: Section to create prompt for
        document_title (str): Document title
        
    Returns:
        VisualPrompt: Generated visual prompt
    """
    prompt_agent = create_visual_prompt_agent()
    
    input_text = (
        f"Document Title: {document_title}\n\n"
        f"Section Title: {section.title}\n\n"
        f"Section Content:\n{section.content}\n\n"
        f"Key Themes: {', '.join(section.themes)}\n\n"
        f"Potential Visual Elements: {', '.join(section.visual_elements)}\n\n"
        f"Create a photorealistic prompt for this content."
    )
    
    result = await Runner.run(prompt_agent, input_text)
    return result.final_output