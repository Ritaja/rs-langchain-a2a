"""
Langfuse Configuration Module

This module provides configuration for Langfuse tracing and monitoring
of the insurance analyst agent.
"""

from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

# Load environment variables
load_dotenv()


def get_langfuse_handler():
    """
    Initialize and return a Langfuse callback handler for LangChain tracing.

    Returns:
        CallbackHandler:
            Configured Langfuse callback handler or None if not available
    """

    # Initialize handler with Langfuse client
    langfuse_handler = CallbackHandler()
    if not langfuse_handler:
        print("⚠️  Langfuse not installed. Tracing will be disabled.")
        print("   To enable tracing, run: pip install langfuse")
        return None

    return langfuse_handler
