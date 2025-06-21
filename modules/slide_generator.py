"""
HTML slide generation functionality.
"""
import os
import base64
from modules.models import HTMLSlide, BOSCH_COLORS
from modules.agents import extract_key_bullet_points

def load_company_logo():
    """
    Load company logo and convert to base64.
    
    Returns:
        str: Base64 encoded logo
    """
    try:
        # Look for logo.png in the current directory
        logo_path = os.path.join(os.getcwd(), "logo.png")
        
        # If not found there, check other common locations
        if not os.path.exists(logo_path):
            # Check static folder if it exists
            static_path = os.path.join(os.getcwd(), "static", "logo.png")
            if os.path.exists(static_path):
                logo_path = static_path
            else:
                # Check assets folder if it exists
                assets_path = os.path.join(os.getcwd(), "assets", "logo.png")
                if os.path.exists(assets_path):
                    logo_path = assets_path
        
        # If logo is found, encode it
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                return encoded_string
    except Exception as e:
        print(f"Error loading logo: {e}")
    
    # Return a transparent placeholder if logo not found or error occurs
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

async def create_html_slide(section, image_info, document_title):
    """
    Create a professional HTML slide with various layouts based on content type.
    
    Args:
        section: Section to create slide for
        image_info: Image information
        document_title (str): Document title
        
    Returns:
        HTMLSlide: Generated HTML slide
    """
    # Get concise bullet points using dedicated agent
    bullet_points = await extract_key_bullet_points(section, document_title)
    
    # Generate a clean title for the slide
    slide_title = section.title.strip()
    
    # Define Bosch color scheme
    subtitle_color = "#007BC0"  # Bosch blue
    colors = {
        "primary": "#E20015",  # Bosch Red
        "secondary": "#007BC0", # Bosch Blue
        "accent": "#00884A",    # Bosch Green
        "text": "#333333",      # Dark Gray
        "light_text": "#7D7D7D", # Medium Gray
        "background": "#FFFFFF", # White
        "slide_bg": "#FFFFFF",   # White
        "card_bg": "#F5F5F5"     # Light Gray
    }
    
    # DETERMINE LAYOUT TYPE based on content analysis
    # 1. Count bullet points
    num_bullet_points = len(bullet_points)
    
    # 2. Analyze section title for keywords
    title_lower = slide_title.lower()
    image_keywords = ["visual", "diagram", "chart", "picture", "image", "photo"]
    has_image_keywords = any(keyword in title_lower for keyword in image_keywords)
    
    # 3. Determine section content length
    content_length = len(section.content)
    
    # 4. Choose appropriate layout
    if num_bullet_points <= 2 and has_image_keywords:
        # Use a centered large image layout
        layout_type = "image_focus"
    elif num_bullet_points >= 5:
        # Use a text-heavy layout
        layout_type = "text_focus"
    elif "comparison" in title_lower or "versus" in title_lower or "vs" in title_lower:
        # Use a split comparison layout
        layout_type = "comparison"
    elif content_length > 500:
        # Use a text-heavy layout for longer content
        layout_type = "text_focus"
    else:
        # Use a balanced layout
        layout_type = "balanced"
    
    # Generate bullet points HTML
    bullet_points_html = generate_bullet_points_html(bullet_points, layout_type, colors)
    
    # Create a professional HTML slide template based on layout
    html_content = generate_html_content(
        slide_title, document_title, layout_type, bullet_points_html, image_info, colors, subtitle_color
    )
    
    # Create a valid HTMLSlide object
    html_slide = HTMLSlide(
        html_content=html_content,
        title=slide_title,
        section_title=section.title,
        section_content=", ".join(bullet_points) if bullet_points else section.content[:100] + "..."
    )
    
    return html_slide

def generate_bullet_points_html(bullet_points, layout_type, colors):
    """
    Generate HTML for bullet points based on layout type.
    
    Args:
        bullet_points (list): List of bullet points
        layout_type (str): Layout type
        colors (dict): Color scheme
        
    Returns:
        str: HTML for bullet points
    """
    bullet_points_html = ""
    
    # Different styling for bullet points based on layout
    if layout_type == "text_focus":
        # Compact bullet points
        for i, point in enumerate(bullet_points):
            bullet_points_html += f"""
            <div class="bullet-point compact" style="animation-delay: {i * 0.15}s;">
                <div class="bullet-icon">•</div>
                <div class="bullet-text">{point}</div>
            </div>
            """
    elif layout_type == "comparison":
        # Split into two columns if possible
        half = len(bullet_points) // 2
        bullet_points_html += '<div class="comparison-container">'
        
        bullet_points_html += '<div class="comparison-column">'
        for i, point in enumerate(bullet_points[:half]):
            bullet_points_html += f"""
            <div class="bullet-point comparison-item" style="animation-delay: {i * 0.15}s;">
                <div class="bullet-text">{point}</div>
            </div>
            """
        bullet_points_html += '</div>'
        
        bullet_points_html += '<div class="comparison-column">'
        for i, point in enumerate(bullet_points[half:]):
            bullet_points_html += f"""
            <div class="bullet-point comparison-item" style="animation-delay: {(i+half) * 0.15}s;">
                <div class="bullet-text">{point}</div>
            </div>
            """
        bullet_points_html += '</div>'
        bullet_points_html += '</div>'
    elif layout_type == "image_focus":
        # More descriptive bullet points for image-focused layouts
        for i, point in enumerate(bullet_points):
            bullet_points_html += f"""
            <div class="bullet-point highlight" style="animation-delay: {i * 0.15}s;">
                <div class="bullet-number">{i+1}</div>
                <div class="bullet-text">{point}</div>
            </div>
            """
    else:
        # Standard bullet points
        for i, point in enumerate(bullet_points):
            bullet_points_html += f"""
            <div class="bullet-point" style="animation-delay: {i * 0.15}s;">
                <div class="bullet-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="{colors["secondary"]}"/>
                    </svg>
                </div>
                <div class="bullet-text">{point}</div>
            </div>
            """
    return bullet_points_html

def generate_html_content(slide_title, document_title, layout_type, bullet_points_html, image_info, colors, subtitle_color):
    """
    Generate HTML content for a slide.
    
    Args:
        slide_title (str): Slide title
        document_title (str): Document title
        layout_type (str): Layout type
        bullet_points_html (str): HTML for bullet points
        image_info: Image information
        colors (dict): Color scheme
        subtitle_color (str): Subtitle color
        
    Returns:
        str: HTML content for the slide
    """
    # Create a professional HTML slide template based on layout
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{slide_title} - {document_title}</title>
    <style>
        /* Reset and base styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        body {{
            font-family: 'Poppins', 'Segoe UI', Roboto, Arial, sans-serif;
            color: {colors["text"]};
            background-color: {colors["slide_bg"]};
            line-height: 1.6;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        /* Slide container */
        .slide {{
            width: 1280px;
            height: 720px;
            background-color: {colors["background"]};
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            overflow: hidden;
            position: relative;
            display: grid;
            grid-template-rows: auto 1fr auto;
        }}
        
        /* Header */
        .header {{
            padding: 20px 50px 10px;
            position: relative;
            z-index: 1;
        }}
        
        .title {{
            font-size: 32px;
            font-weight: 700;
            color: {colors["text"]};
            letter-spacing: -0.5px;
            display: block;
        }}
        
        .subtitle {{
            font-size: 22px;
            font-weight: 500;
            color: {subtitle_color};
            margin-top: 5px;
        }}
        
        /* Common content styles */
        .content {{
            position: relative;
            z-index: 1;
            padding: 30px 50px;
        }}
        
        /* Layout specific styles */
        /* 1. BALANCED LAYOUT - Standard split */
        {".content { display: grid; grid-template-columns: 3fr 2fr; gap: 30px; }" if layout_type == "balanced" else ""}
        
        /* 2. TEXT FOCUS LAYOUT - More space for text */
        {".content { display: grid; grid-template-columns: 4fr 1fr; gap: 30px; }" if layout_type == "text_focus" else ""}
        
        /* 3. IMAGE FOCUS LAYOUT - Image prominent */
        {".content { display: flex; flex-direction: column; } .image-container { margin-bottom: 30px; width: 100%; max-height: 450px; } .bullet-points { display: flex; flex-direction: row; justify-content: space-between; }" if layout_type == "image_focus" else ""}
        
        /* 4. COMPARISON LAYOUT - Side by side */
        {".content { display: block; } .comparison-container { display: flex; gap: 50px; } .comparison-column { flex: 1; }" if layout_type == "comparison" else ""}
        
        /* Text column */
        .text-column {{
            display: flex;
            flex-direction: column;
        }}
        
        /* Bullet points */
        .bullet-points {{
            display: flex;
            flex-direction: column;
            gap: 18px;
            margin-top: 10px;
        }}
        
        .bullet-point {{
            display: flex;
            align-items: flex-start;
            background-color: {colors["card_bg"]};
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transform: translateY(20px);
            opacity: 0;
            animation: slide-in 0.5s forwards ease-out;
            transition: all 0.3s ease;
        }}
        
        /* Add styles for different bullet point types */
        .bullet-point.compact {{
            padding: 10px 15px;
        }}
        
        .bullet-point.highlight {{
            background: linear-gradient(135deg, {colors["secondary"]}10, {colors["background"]});
            border-left: 4px solid {colors["secondary"]};
        }}
        
        .bullet-point.comparison-item {{
            text-align: center;
            justify-content: center;
        }}
        
        .bullet-icon {{
            margin-right: 15px;
            flex-shrink: 0;
            margin-top: 2px;
        }}
        
        .bullet-number {{
            width: 26px;
            height: 26px;
            border-radius: 50%;
            background-color: {colors["secondary"]};
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        
        .bullet-text {{
            font-size: 18px;
            font-weight: 500;
            color: {colors["text"]};
            line-height: 1.4;
        }}
        
        /* Image column */
        .image-column {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-container {{
            width: 100%;
            max-width: 450px;
            height: auto;
            max-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
        }}
        
        .image-container img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            transition: transform 0.3s ease;
        }}
        
        @keyframes slide-in {{
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}
        
        /* Footer */
        .footer {{
            padding: 15px 50px;
            text-align: right;
            color: {colors["light_text"]};
            font-size: 14px;
            font-weight: 300;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .footer-text {{
            flex-grow: 1;
        }}
        
        .company-logo {{
            height: 40px;
            width: auto;
            margin-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="header">
            <h1 class="title">{slide_title}</h1>
            <p class="subtitle">{document_title}</p>
        </div>
        
        <div class="content">
            {f'''
            <!-- IMAGE FOCUS LAYOUT -->
            <div class="image-container centered-image">
                <img src="data:image/jpeg;base64,{image_info.base64_data}" alt="{slide_title}">
            </div>
            <div class="bullet-points">
                {bullet_points_html}
            </div>
            ''' if layout_type == "image_focus" else f'''
            <!-- COMPARISON LAYOUT -->
            {bullet_points_html}
            ''' if layout_type == "comparison" else f'''
            <!-- BALANCED OR TEXT FOCUSED LAYOUT -->
            <div class="text-column">
                <div class="bullet-points">
                    {bullet_points_html}
                </div>
            </div>
            <div class="image-column">
                <div class="image-container">
                    <img src="data:image/jpeg;base64,{image_info.base64_data}" alt="{slide_title}">
                </div>
            </div>
            '''}
        </div>
        
        <div class="footer">
            <span class="footer-text">{document_title} | {slide_title}</span>
            <img src="data:image/png;base64,{load_company_logo()}" alt="Company Logo" class="company-logo">
        </div>
    </div>
</body>
</html>"""
    
    return html_content