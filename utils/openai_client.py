"""
OpenAI client initialization and configuration.
"""
import os
from openai import AsyncAzureOpenAI, AzureOpenAI
from agents import set_default_openai_client

def initialize_openai():
    """
    Initialize both GPT and DALL-E clients.
    
    Returns:
        tuple: (async_client, dalle_client) - OpenAI clients for GPT and DALL-E
    """
    # Initialize the AsyncAzureOpenAI client for GPT
    async_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    set_default_openai_client(async_client)
    
    # Create a separate client for DALL-E
    dalle_client = AzureOpenAI(
        api_key=os.getenv("DALLE_API_KEY"),
        api_version=os.getenv("DALLE_API_VERSION", "2024-02-01"),
        azure_endpoint=os.getenv("DALLE_ENDPOINT")
    )
    
    return async_client, dalle_client

def update_openai_settings(gpt_settings, dalle_settings):
    """
    Update OpenAI settings in environment variables.
    
    Args:
        gpt_settings (dict): GPT API settings
        dalle_settings (dict): DALL-E API settings
    """
    # Update GPT settings
    os.environ["AZURE_OPENAI_API_KEY"] = gpt_settings.get("api_key", "")
    os.environ["AZURE_OPENAI_ENDPOINT"] = gpt_settings.get("endpoint", "")
    os.environ["AZURE_OPENAI_DEPLOYMENT"] = gpt_settings.get("deployment", "")
    os.environ["AZURE_OPENAI_API_VERSION"] = gpt_settings.get("api_version", "2024-02-01")
    
    # Update DALL-E settings
    os.environ["DALLE_API_KEY"] = dalle_settings.get("api_key", "")
    os.environ["DALLE_ENDPOINT"] = dalle_settings.get("endpoint", "")
    os.environ["DALLE_API_VERSION"] = dalle_settings.get("api_version", "2024-02-01")
    os.environ["DALLE_DEPLOYMENT"] = dalle_settings.get("deployment", "dall-e-3")