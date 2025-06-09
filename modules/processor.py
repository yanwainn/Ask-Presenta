"""
Main processing logic for PDF to presentation conversion.
"""
import os
import asyncio
import streamlit as st

from modules.helpers import extract_text_from_pdf, generate_image_from_prompt, save_image_locally, load_image_info_from_pil
from modules.agents import extract_key_sections, create_visual_prompt
from modules.slide_generator import create_html_slide
from utils.openai_client import initialize_openai

async def process_pdf_to_presentation(pdf_file):
    """
    Complete PDF to presentation process.
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        dict: Processing results or None if processing failed
    """
    # Reset session state
    st.session_state.pdf_content = None
    st.session_state.key_sections = None
    st.session_state.image_prompts = []
    st.session_state.generated_images = []
    st.session_state.slides_html = []
    st.session_state.process_complete = False
    
    # Create progress indicators
    progress_bar = st.progress(0)
    
    # Display status indicators
    step1_status = st.empty()
    step2_status = st.empty()
    step3_status = st.empty()
    step4_status = st.empty()
    
    # Initialize clients
    _, dalle_client = initialize_openai()
    
    try:
        # Step 1: Extract PDF content
        step1_status.markdown('<div class="step-item status-processing">Extracting content from PDF...</div>', unsafe_allow_html=True)
        
        pdf_text = extract_text_from_pdf(pdf_file)
        if not pdf_text:
            step1_status.markdown('<div class="step-item status-error">Failed to extract PDF content</div>', unsafe_allow_html=True)
            return None
        
        progress_bar.progress(10)
        st.session_state.pdf_content = pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text
        
        # Extract key sections
        extraction_result = await extract_key_sections(pdf_text)
        st.session_state.key_sections = extraction_result
        
        step1_status.markdown('<div class="step-item status-complete">✅ PDF Content Extracted</div>', unsafe_allow_html=True)
        
        # Step 2: Create image prompts
        step2_status.markdown('<div class="step-item status-processing">Creating image prompts...</div>', unsafe_allow_html=True)
        
        # Generate prompts for each section
        prompts = []
        for i, section in enumerate(extraction_result.key_sections):
            progress_bar.progress(10 + (20 * (i+1) // len(extraction_result.key_sections)))
            prompt = await create_visual_prompt(section, extraction_result.document_title)
            prompts.append(prompt)
        
        st.session_state.image_prompts = prompts
        progress_bar.progress(30)
        
        step2_status.markdown('<div class="step-item status-complete">✅ Image Prompts Created</div>', unsafe_allow_html=True)
        
        # Step 3: Generate images
        step3_status.markdown('<div class="step-item status-processing">Generating images...</div>', unsafe_allow_html=True)
        
        # Generate images
        images = []
        image_infos = []
        os.makedirs(st.session_state.images_folder, exist_ok=True)
        
        # Process images in parallel to speed things up
        async def process_image(prompt, index):
            try:
                # Generate image
                image_result = generate_image_from_prompt(dalle_client, prompt.prompt)
                
                if image_result and "image" in image_result:
                    # Save image
                    is_placeholder = image_result.get("is_placeholder", False)
                    filename_prefix = "placeholder_" if is_placeholder else ""
                    
                    save_result = save_image_locally(
                        image_result["image"], 
                        f"{filename_prefix}{prompt.section_title}", 
                        index+1,
                        st.session_state.images_folder
                    )
                    
                    if save_result["success"]:
                        # Create image info
                        image_info = load_image_info_from_pil(
                            image_result["image"],
                            os.path.basename(save_result["filepath"]),
                            save_result["filepath"]
                        )
                        
                        if image_info:
                            return {
                                "index": index,
                                "image_result": image_result,
                                "save_result": save_result,
                                "image_info": image_info
                            }
            except Exception as e:
                st.warning(f"Error processing image {index+1}: {str(e)}")
            
            return None
        
        # Create tasks for parallel processing
        tasks = [process_image(prompt, i) for i, prompt in enumerate(prompts)]
        results = await asyncio.gather(*tasks)
        
        # Process results and update progress
        valid_results = [r for r in results if r is not None]
        for result in sorted(valid_results, key=lambda x: x["index"]):
            images.append({
                **result["image_result"],
                "save_result": result["save_result"],
                "image_info": result["image_info"]
            })
            image_infos.append(result["image_info"])
            
            # Update progress
            progress_updated = 30 + (30 * (len(images)) // len(prompts))
            progress_bar.progress(min(60, progress_updated))
        
        # Store images
        st.session_state.generated_images = images
        
        # Check if we have enough images
        if len(image_infos) < len(extraction_result.key_sections):
            step3_status.markdown('<div class="step-item status-error">⚠️ Some images failed to generate</div>', unsafe_allow_html=True)
        else:
            step3_status.markdown('<div class="step-item status-complete">✅ Images Generated</div>', unsafe_allow_html=True)
        
        progress_bar.progress(60)
        
        # Step 4: Create HTML slides
        step4_status.markdown('<div class="step-item status-processing">Creating HTML slides...</div>', unsafe_allow_html=True)
        
        # Process slides in parallel
        async def process_slide(section, image_info, index):
            try:
                slide = await create_html_slide(section, image_info, extraction_result.document_title)
                return {
                    "index": index,
                    "slide": slide
                }
            except Exception as e:
                st.warning(f"Error creating slide {index+1}: {str(e)}")
                return None
        
        # Create tasks for parallel processing (up to limit of valid images)
        max_slides = min(len(extraction_result.key_sections), len(image_infos))
        slide_tasks = [
            process_slide(extraction_result.key_sections[i], image_infos[i], i)
            for i in range(max_slides)
        ]
        
        slide_results = await asyncio.gather(*slide_tasks)
        
        # Process results
        slides = []
        valid_slide_results = [r for r in slide_results if r is not None]
        for result in sorted(valid_slide_results, key=lambda x: x["index"]):
            slides.append(result["slide"])
            
            # Update progress
            progress_updated = 60 + (40 * (len(slides)) // max_slides)
            progress_bar.progress(min(100, progress_updated))
        
        # Store slides
        st.session_state.slides_html = slides
        
        # Complete
        progress_bar.progress(100)
        
        if len(slides) > 0:
            step4_status.markdown('<div class="step-item status-complete">✅ HTML Slides Created</div>', unsafe_allow_html=True)
            st.session_state.process_complete = True
            return {
                "extraction_result": extraction_result,
                "prompts": prompts,
                "images": images,
                "slides": slides
            }
        else:
            step4_status.markdown('<div class="step-item status-error">❌ Slide Creation Failed</div>', unsafe_allow_html=True)
            return None
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.error(f"Error: {str(e)}")
        return None