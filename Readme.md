# PDF to Presentation Generator

This application transforms PDFs into professional presentations using Azure OpenAI GPT and DALL-E, with support for custom organization templates.

## Features

- Extract key sections from PDF documents
- Generate photorealistic images for each section using DALL-E
- Create professional HTML slides with multiple layout options
- Convert to PowerPoint format using your organization's template
- Include your company logo on all slides
- Streamlined UI focused on presentation preview and download options

## Project Structure

```
pdf_to_presentation/
│
├── app.py                         # Main Streamlit application
│
├── logo.png                       # Your company logo
├── template.pptx                  # Your organization's PowerPoint template
│
├── modules/
│   ├── __init__.py                # Make the folder a package
│   ├── helpers.py                 # Helper functions for image processing, PDF handling, etc.
│   ├── models.py                  # Data models (Pydantic classes)
│   ├── agents.py                  # OpenAI agent definitions and configurations
│   ├── processor.py               # Main processing logic
│   ├── slide_generator.py         # HTML slide generation functionality
│   ├── pptx_converter.py          # Standard PowerPoint conversion
│   └── template_pptx_converter.py # Template-based PowerPoint conversion
│
└── utils/
    ├── __init__.py                # Make the folder a package
    ├── openai_client.py           # OpenAI client setup and configuration
    └── logo_test.py               # Utility to test logo detection
```

## Requirements

- Python 3.8+
- Azure OpenAI API access (GPT and DALL-E)
- See requirements.txt for all dependencies

## Environment Variables

Create a `.env` file with the following variables:

```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=your_gpt_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

DALLE_API_KEY=your_dalle_api_key
DALLE_ENDPOINT=your_dalle_endpoint
DALLE_DEPLOYMENT=dall-e-3
DALLE_API_VERSION=2024-02-01
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file
4. Add your company resources:
   - Add your company logo as `logo.png` in the project directory
   - Add your PowerPoint template as `template.pptx` in the project directory
5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Upload a PDF document
2. Click "Generate Presentation"
3. Wait for the AI to process the document and build slides
4. Preview your slides in the "Preview Slides" tab
5. Download your presentation in the "Download Options" tab:
   - PowerPoint: Generates a PowerPoint presentation using your organization's template
   - HTML: Download all slides as HTML files in a ZIP archive

## Company Logo Integration

Place your company logo as `logo.png` in one of these locations:
- In the main project directory (same level as app.py)
- In a `static` folder in your project root
- In an `assets` folder in your project root

## Organization PowerPoint Template

To use your organization's PowerPoint template for generated presentations:

1. Add your PowerPoint template as `template.pptx` in one of these locations:
   - In the main project directory (same level as app.py)
   - In a `templates` folder in your project root
   - In a `static` folder in your project root

2. The application will automatically detect your template and use it when generating PowerPoint presentations.

3. You can toggle between using your organization template or a standard template in the interface.

Your template should include:
- A title slide layout (usually the first slide)
- Content slide layouts with placeholders for title and content

The system will use appropriate layouts from your template, preserving your organization's branding, colors, and styling while inserting the AI-generated content.

## License

MIT# PDF to Presentation Generator

This application transforms PDFs into both HTML presentations and PowerPoint presentations with AI-generated images using Azure OpenAI GPT and DALL-E.

## Features

- Extract key sections from PDF documents
- Generate photorealistic images for each section using DALL-E
- Create professional HTML slides with multiple layout options
- Convert to PowerPoint format that matches the HTML styling
- Include your company logo on all slides
- Download individual slides or complete presentations

## Project Structure

```
pdf_to_presentation/
│
├── app.py                  # Main Streamlit application
│
├── logo.png                # Your company logo (place your logo here)
│
├── modules/
│   ├── __init__.py         # Make the folder a package
│   ├── helpers.py          # Helper functions for image processing, PDF handling, etc.
│   ├── models.py           # Data models (Pydantic classes)
│   ├── agents.py           # OpenAI agent definitions and configurations
│   ├── processor.py        # Main processing logic
│   ├── slide_generator.py  # HTML slide generation functionality
│   └── pptx_converter.py   # PowerPoint conversion functionality
│
└── utils/
    ├── __init__.py         # Make the folder a package
    ├── openai_client.py    # OpenAI client setup and configuration
    └── logo_test.py        # Utility to test logo detection
```

## Requirements

- Python 3.8+
- Azure OpenAI API access (GPT and DALL-E)
- Streamlit
- PyPDF2
- Pillow
- Pydantic
- Openai SDK
- Agents SDK
- Python-pptx

See requirements.txt for all dependencies.

## Environment Variables

Create a `.env` file with the following variables:

```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT=your_gpt_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-01

DALLE_API_KEY=your_dalle_api_key
DALLE_ENDPOINT=your_dalle_endpoint
DALLE_DEPLOYMENT=dall-e-3
DALLE_API_VERSION=2024-02-01
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file
4. Add your company logo as `logo.png` in the project directory
5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Upload a PDF document
2. Click "Generate Presentation"
3. Wait for the AI to process the document, create image prompts, generate images, and build slides
4. Preview and download your presentation:
   - HTML Slides Tab: Preview, get HTML code, or download individual/all HTML slides
   - PowerPoint Tab: Generate and download a PowerPoint presentation matching the HTML styling

## Organization PowerPoint Template

To use your organization's PowerPoint template for generated presentations:

1. Add your PowerPoint template as `template.pptx` in one of these locations:
   - In the main project directory (same level as app.py)
   - In a `templates` folder in your project root
   - In a `static` folder in your project root

2. The application will automatically detect your template and use it when generating PowerPoint presentations.

3. You can toggle between using your organization template or a standard template in the interface.

Your template should include:
- A title slide layout (usually the first slide)
- Content slide layouts with placeholders for title and content

The system will attempt to use appropriate layouts from your template, preserving your organization's branding, colors, and styling while inserting the AI-generated content.

## License

MIT