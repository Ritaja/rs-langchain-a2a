import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


def get_azure_llm():
    """Initialize and return Azure OpenAI LLM instance."""
    load_dotenv()

    # Validate required environment variables
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}")

    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.7,
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME",
                        "<default-azure-openai-model-name>")
    )
