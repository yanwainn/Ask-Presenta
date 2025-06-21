# Ask-Presenta: High-Level Overview & Module Breakdown

## 1. High-Level Overview

Ask-Presenta is an AI-powered application that transforms PDF documents into professional presentations using Azure OpenAI services (GPT and DALL-E). The workflow is:

1. **Document Processing**: Extract key content from uploaded PDFs
2. **Content Analysis**: Identify key sections and themes using AI
3. **Image Generation**: Create relevant images for each slide using DALL-E
4. **Slide Creation**: Generate professional HTML slides with the content and images
5. **PowerPoint Export**: Convert to PowerPoint format (with optional organization template support)

The application provides a streamlined interface for previewing and downloading presentations in both HTML and PowerPoint formats.

## 2. Module Contributions by Feature

### Document Processing & Content Extraction
- **helpers.py**: Contains `extract_text_from_pdf()` function
- **processor.py**: Main orchestration for the PDF processing pipeline

### AI Content Analysis
- **agents.py**: Contains `extract_key_sections()` function that uses Azure OpenAI to analyze text
- **openai_client.py**: Handles OpenAI API initialization and configuration

### Image Generation
- **agents.py**: Contains `create_visual_prompt()` function that generates DALL-E prompts
- **helpers.py**: Contains `generate_image_from_prompt()` for DALL-E API calls
- **logo_test.py**: Utility for logo detection and integration

### Slide Generation
- **slide_generator.py**: Creates HTML slides with different layouts
- **models.py**: Defines data structures for slides and content

### PowerPoint Conversion
- **pptx_converter.py**: Standard PowerPoint conversion
- **template_pptx_converter.py**: Template-based PowerPoint conversion using organization templates

### User Interface
- **app.py**: Main Streamlit application with UI components and interaction logic

### Infrastructure & Utilities
- **openai_client.py**: Client setup for Azure OpenAI services
- **.env**: Configuration for API keys and endpoints

Each step in the workflow is handled by specific modules that work together to transform the PDF document into a presentation, with both the processing pipeline and the generated presentations highly customizable through the interface.