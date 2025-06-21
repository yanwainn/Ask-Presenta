"""
PDF to HTML Presentation Generator - Main Streamlit Application.

This application transforms PDFs into HTML presentations with AI-generated images.
"""
import os
import asyncio
import zipfile
import streamlit as st
from io import BytesIO
from dotenv import load_dotenv

from modules.processor import process_pdf_to_presentation
from utils.openai_client import update_openai_settings

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="PDF to Presentation", page_icon="🖼️", layout="wide")

# ===== INITIALIZE SESSION STATES =====
def initialize_session_states():
    """Initialize all session state variables."""
    if 'pdf_content' not in st.session_state:
        st.session_state.pdf_content = None
    if 'key_sections' not in st.session_state:
        st.session_state.key_sections = None
    if 'image_prompts' not in st.session_state:
        st.session_state.image_prompts = []
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'slides_html' not in st.session_state:
        st.session_state.slides_html = []
    if 'process_complete' not in st.session_state:
        st.session_state.process_complete = False
    if 'images_folder' not in st.session_state:
        st.session_state.images_folder = os.path.join(os.getcwd(), 'generated_images')
    if 'uploaded_template' not in st.session_state:
        st.session_state.uploaded_template = None

# ===== SETTINGS SIDEBAR CONTENT =====
def render_settings_sidebar():
    """Render the settings sidebar."""
    with st.sidebar:
        st.header("Settings")
        
        # Image folder
        st.subheader("Image Output Folder")
        images_folder = st.text_input("Path to save images", value=st.session_state.images_folder)
        
        if st.button("Update Folder"):
            try:
                os.makedirs(images_folder, exist_ok=True)
                st.session_state.images_folder = images_folder
                st.success(f"Image folder updated")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # API Configuration
        with st.expander("API Settings"):
            # GPT settings
            st.markdown("**GPT Settings**")
            gpt_api_key = st.text_input("Azure OpenAI API Key", value=os.getenv("AZURE_OPENAI_API_KEY", ""), type="password")
            gpt_endpoint = st.text_input("Azure OpenAI Endpoint", value=os.getenv("AZURE_OPENAI_ENDPOINT", ""))
            gpt_deployment = st.text_input("Azure OpenAI Deployment", value=os.getenv("AZURE_OPENAI_DEPLOYMENT", ""))
            gpt_api_version = st.text_input("API Version", value=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"))
            
            # DALL-E settings
            st.markdown("**DALL-E Settings**")
            dalle_api_key = st.text_input("DALL-E API Key", value=os.getenv("DALLE_API_KEY", ""), type="password")
            dalle_endpoint = st.text_input("DALL-E Endpoint", value=os.getenv("DALLE_ENDPOINT", ""))
            dalle_api_version = st.text_input("API Version", value=os.getenv("DALLE_API_VERSION", "2024-02-01"))
            dalle_deployment = st.text_input("Deployment Name", value=os.getenv("DALLE_DEPLOYMENT", "dall-e-3"))
            
            if st.button("Update API Settings"):
                # Update environment variables using the central function
                gpt_settings = {
                    "api_key": gpt_api_key,
                    "endpoint": gpt_endpoint,
                    "deployment": gpt_deployment,
                    "api_version": gpt_api_version
                }
                dalle_settings = {
                    "api_key": dalle_api_key,
                    "endpoint": dalle_endpoint,
                    "api_version": dalle_api_version,
                    "deployment": dalle_deployment
                }
                update_openai_settings(gpt_settings, dalle_settings)
                st.success("API settings updated")

# ===== MAIN CONTENT AREA =====
def render_main_content():
    """Render the main content area."""
    st.title("Ask Presenta")
    st.markdown("Transform PDFs into PowerPoint presentations with Agentic-AI.")
    
    # File upload
    st.subheader("Upload Your PDF Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        st.write(f"Uploaded: {uploaded_file.name}")
        
        # Process button
        if st.button("Generate Presentation", use_container_width=True):
            with st.spinner("Processing..."):
                asyncio.run(process_pdf_to_presentation(uploaded_file))

# ===== RESULTS DISPLAY =====
def render_results():
    """Render the results if process is complete."""
    if st.session_state.process_complete:
        extraction_result = st.session_state.key_sections
        prompts = st.session_state.image_prompts
        images = st.session_state.generated_images
        slides = st.session_state.slides_html
        
        # Document overview
        st.subheader("Document Analysis")
        st.write(f"**Document:** {extraction_result.document_title}")
        st.write(f"**Summary:** {extraction_result.summary}")
        
        # Hide the generated images section
        # Directly show the presentation slides
        
        st.subheader("Presentation")
        if len(slides) > 0:
            # Create tabs for different outputs
            preview_tab, download_tab = st.tabs(["Preview Slides", "Download Options"])
            
            with preview_tab:
                # Create slide navigation
                slide_tabs = []
                for i, slide in enumerate(slides):
                    slide_tabs.append(f"{i+1}. {slide.title}")
                
                selected_tab = st.radio("Select slide:", slide_tabs, horizontal=True)
                selected_index = slide_tabs.index(selected_tab)
                
                # Preview selected slide
                if selected_index < len(slides):
                    selected_slide = slides[selected_index]
                    
                    # Show HTML slide
                    st.markdown("<div class='slide-container'>", unsafe_allow_html=True)
                    st.components.v1.html(selected_slide.html_content, height=600, scrolling=False)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with download_tab:
                # PowerPoint and HTML download options
                ppt_col, html_col = st.columns(2)
                
                with ppt_col:
                    st.markdown("### PowerPoint Presentation")
                    
                    # Check if we have a template file
                    template_file = None
                    template_paths = [
                        os.path.join(os.getcwd(), "template.pptx"),
                        os.path.join(os.getcwd(), "templates", "template.pptx"),
                        os.path.join(os.getcwd(), "static", "template.pptx")
                    ]
                    
                    for path in template_paths:
                        if os.path.exists(path):
                            template_file = path
                            break
                    
                    # Template upload option
                    st.markdown("#### PowerPoint Template")
                    template_upload = st.file_uploader("Upload your organization's PowerPoint template", type="pptx")
                    
                    if template_upload is not None:
                        # Save the uploaded template to session state
                        template_bytes = template_upload.getvalue()
                        st.session_state.uploaded_template = BytesIO(template_bytes)
                        st.success(f"Template '{template_upload.name}' uploaded successfully!")
                    
                    # Template selection
                    use_template = False
                    template_source = "None"
                    
                    if st.session_state.uploaded_template is not None:
                        use_template = st.checkbox("Use uploaded PowerPoint template", value=True)
                        if use_template:
                            template_source = "uploaded"
                    elif template_file:
                        use_template = st.checkbox("Use organization PowerPoint template", value=True)
                        if use_template:
                            template_source = "default"
                            st.caption(f"Using template: {os.path.basename(template_file)}")
                    
                    # Generate PowerPoint button
                    if st.button("Generate PowerPoint Presentation", use_container_width=True):
                        with st.spinner("Creating PowerPoint..."):
                            try:
                                pptx_buffer = None
                                
                                if use_template:
                                    # Use template-based converter
                                    from modules.template_pptx_converter import create_powerpoint_from_template
                                    
                                    if template_source == "uploaded" and st.session_state.uploaded_template is not None:
                                        # Use the uploaded template
                                        pptx_buffer = create_powerpoint_from_template(
                                            slides, 
                                            extraction_result, 
                                            template_file=None,
                                            template_stream=st.session_state.uploaded_template
                                        )
                                    elif template_source == "default" and template_file:
                                        # Use the default template file
                                        pptx_buffer = create_powerpoint_from_template(
                                            slides, 
                                            extraction_result, 
                                            template_file=template_file
                                        )
                                    else:
                                        raise ValueError("Template selected but not available")
                                else:
                                    # Use standard converter
                                    from modules.pptx_converter import create_powerpoint_from_slides
                                    pptx_buffer = create_powerpoint_from_slides(slides, extraction_result)
                                
                                # Display success message
                                st.success("PowerPoint presentation created successfully!")
                                
                                # Download button for PowerPoint
                                st.download_button(
                                    label="Download PowerPoint Presentation",
                                    data=pptx_buffer.getvalue(),
                                    file_name=f"{extraction_result.document_title}.pptx",
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"Error creating PowerPoint: {str(e)}")
                                st.info("Make sure you have the 'python-pptx' library installed: `pip install python-pptx`")
                
                    # Template info
                    if not template_file and st.session_state.uploaded_template is None:
                        st.info("You can upload your organization's PowerPoint template above, or add a file named 'template.pptx' to your project folder.")
                        st.caption("The template should include slide layouts for a title slide and content slides.")

                with html_col:
                    st.markdown("### HTML Slides")
                    # Create zip file for HTML slides
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for i, slide in enumerate(slides):
                            file_name = f"slide_{i+1}_{slide.title.replace(' ', '_')}.html"
                            zip_file.writestr(file_name, slide.html_content)
                    
                    # Download button for HTML zip
                    st.download_button(
                        label="Download All HTML Slides (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="presentation_slides_html.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    # Option to download individual slide
                    st.markdown("#### Download Individual Slide")
                    slide_select = st.selectbox(
                        "Select a slide to download:",
                        [f"{i+1}. {slide.title}" for i, slide in enumerate(slides)]
                    )
                    selected_index = [f"{i+1}. {slide.title}" for i, slide in enumerate(slides)].index(slide_select)
                    
                    if selected_index >= 0:
                        selected_slide = slides[selected_index]
                        st.download_button(
                            label=f"Download '{selected_slide.title}' Slide",
                            data=selected_slide.html_content,
                            file_name=f"slide_{selected_index+1}_{selected_slide.title.replace(' ', '_')}.html",
                            mime="text/html",
                            use_container_width=True
                        )


# ===== MAIN APPLICATION =====
def main():
    """Main application entry point."""
    # Initialize session states
    initialize_session_states()
    
    # Render sidebar
    render_settings_sidebar()
    
    # Render main content
    render_main_content()
    
    # Render results if available
    render_results()

if __name__ == "__main__":
    main()