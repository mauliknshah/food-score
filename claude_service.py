import anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_api_key() -> str:
    """
    Get Anthropic API key from environment variables.

    Returns:
        API key string

    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY must be set as environment variable")
    return api_key


def get_claude_client(api_key: str = None) -> anthropic.Anthropic:
    """
    Get an initialized Anthropic Claude client.

    Args:
        api_key: Optional API key. If None, reads from environment variables.

    Returns:
        Initialized Anthropic client

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    if api_key is None:
        api_key = get_api_key()

    return anthropic.Anthropic(api_key=api_key)


# Default model to use across all agents
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
