"""
Helper functions for the PDF to Presentation application.
"""
import os
import base64
import requests
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import PyPDF2
import streamlit as st

from modules.models import ImageInfo

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from PDF file.
    
    Args:
        pdf_file: The uploaded PDF file
        
    Returns:
        str: Extracted text or None if extraction failed
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
            
            if len(text) > 50000:
                text += "... [Content truncated due to length]"
                break
                
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def generate_image_from_prompt(client, prompt, size="1024x1024"):
    """
    Generate image using DALL-E.
    
    Args:
        client: DALL-E client
        prompt (str): Image generation prompt
        size (str): Image size (default: "1024x1024")
        
    Returns:
        dict: Dictionary with image, URL, and revised prompt
    """
    try:
        # Generate image with DALL-E
        try:
            response = client.images.generate(
                model=os.getenv("DALLE_DEPLOYMENT", "dall-e-3"),
                prompt=prompt,
                n=1,
                size=size
            )
            
            image_url = response.data[0].url
            image_data = requests.get(image_url).content
            image = Image.open(BytesIO(image_data))
            revised_prompt = getattr(response.data[0], 'revised_prompt', None)
            
            return {
                "image": image,
                "url": image_url,
                "revised_prompt": revised_prompt
            }
            
        except Exception as dalle_error:
            # Create a placeholder gradient if DALL-E fails
            st.warning(f"Image generation failed: {str(dalle_error)}")
            
            width, height = map(int, size.split('x'))
            image = Image.new('RGB', (width, height), color='white')
            
            # Generate random colors based on the prompt
            def get_color_from_prompt(prompt_text):
                hash_val = sum(ord(c) for c in prompt_text)
                r = (hash_val * 123) % 256
                g = (hash_val * 456) % 256
                b = (hash_val * 789) % 256
                return (r, g, b)
            
            # Create a gradient
            start_color = get_color_from_prompt(prompt[:10])
            end_color = get_color_from_prompt(prompt[-10:] if len(prompt) > 10 else prompt)
            
            arr = np.zeros((height, width, 3), dtype=np.uint8)
            for y in range(height):
                for x in range(width):
                    r = int(start_color[0] * (width - x) / width + end_color[0] * x / width)
                    g = int(start_color[1] * (height - y) / height + end_color[1] * y / height)
                    b = int(start_color[2] * (1 - (x + y) / (width + height)) + end_color[2] * (x + y) / (width + height))
                    arr[y, x] = [r, g, b]
            
            image = Image.fromarray(arr)
            
            # Add a placeholder label
            draw = ImageDraw.Draw(image)
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            message = "Placeholder Image"
            text_width = 200
            text_position = ((width - text_width) // 2, height // 2)
            draw.text((text_position[0]+2, text_position[1]+2), message, font=font, fill=(0, 0, 0))
            draw.text(text_position, message, font=font, fill=(255, 255, 255))
            
            return {
                "image": image,
                "url": "placeholder_image_url",
                "revised_prompt": "Placeholder image due to API error",
                "is_placeholder": True
            }
            
    except Exception as e:
        st.error(f"Error in image generation: {str(e)}")
        from random import randint
        image = Image.new('RGB', (512, 512), color=(randint(0, 255), randint(0, 255), randint(0, 255)))
        return {
            "image": image,
            "url": "error_placeholder_image_url",
            "revised_prompt": f"Error occurred: {str(e)}",
            "is_placeholder": True
        }

def save_image_locally(image, section_title, index, images_folder):
    """
    Save generated image to a folder.
    
    Args:
        image: PIL Image
        section_title (str): Title of the section
        index (int): Image index
        images_folder (str): Path to save images
        
    Returns:
        dict: Information about the saved image
    """
    try:
        os.makedirs(images_folder, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_title = ''.join(c if c.isalnum() else '_' for c in section_title)
        filename = f"{timestamp}_{index}_{clean_title}.png"
        
        filepath = os.path.join(images_folder, filename)
        image.save(filepath, format="PNG")
        
        return {
            "success": True,
            "filepath": filepath,
            "filename": filename
        }
    except Exception as e:
        st.error(f"Error saving image: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def load_image_info_from_pil(image, filename, filepath):
    """
    Create ImageInfo from PIL Image.
    
    Args:
        image: PIL Image
        filename (str): Image filename
        filepath (str): Full path to the image
        
    Returns:
        ImageInfo: Image information or None if processing failed
    """
    try:
        width, height = image.size
        
        # Convert to RGB if needed
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if hasattr(image, 'convert') and callable(image.convert):
                alpha = image.convert('RGBA').split()[3]
                background.paste(image, mask=alpha)
                image = background
        
        # Resize large images
        max_dimension = 1200
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))
            
            image = image.resize((new_width, new_height), Image.LANCZOS)
            width, height = image.size
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return ImageInfo(
            file_path=filepath,
            file_name=filename,
            base64_data=img_str,
            width=width,
            height=height
        )
    except Exception as e:
        st.error(f"Error creating ImageInfo: {str(e)}")
        return None