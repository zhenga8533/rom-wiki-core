"""
Global config registry for rom_wiki_core.

This module provides a thread-safe registry for storing and accessing the
WikiConfig instance globally, eliminating the need to pass config explicitly
to every function call.
"""

import threading
from typing import Optional

# Type hint for WikiConfig (imported at runtime to avoid circular imports)
_config: Optional[object] = None
_lock = threading.Lock()


def set_config(config) -> None:
    """Set the global WikiConfig instance.

    This should be called once at the start of your application or in each
    generator/parser's __init__ method.

    Args:
        config: WikiConfig instance to use globally

    Example:
        >>> from rom_wiki_core.config import WikiConfig
        >>> from rom_wiki_core.utils.core.config_registry import set_config
        >>> config = WikiConfig(...)
        >>> set_config(config)
    """
    global _config
    with _lock:
        _config = config


def get_config():
    """Get the global WikiConfig instance.

    Returns:
        WikiConfig instance, or None if not set

    Raises:
        RuntimeError: If config has not been set
    """
    with _lock:
        if _config is None:
            raise RuntimeError(
                "Config has not been set. Call set_config() first or pass config explicitly."
            )
        return _config


def has_config() -> bool:
    """Check if a config has been set.

    Returns:
        bool: True if config has been set, False otherwise
    """
    with _lock:
        return _config is not None


def clear_config() -> None:
    """Clear the global config (useful for testing)."""
    global _config
    with _lock:
        _config = None
