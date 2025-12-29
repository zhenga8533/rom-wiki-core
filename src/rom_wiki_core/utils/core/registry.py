"""
Utility functions for loading and managing component registries.

This module provides a generic registry loading mechanism that eliminates code
duplication between parser and generator registry loading in main.py.
"""

import importlib
from typing import Any

from rom_wiki_core.utils.core.logger import get_logger

logger = get_logger(__name__)


def get_component_registry(
    component_config: dict[str, dict[str, Any]], config_keys: tuple[str, ...]
) -> dict[str, tuple[Any, ...]]:
    """Get the registry of available components by dynamically loading them from the config.

    Args:
        component_config (dict[str, dict[str, Any]]): Configuration dictionary for components
        config_keys (tuple[str, ...]): Tuple of additional config keys to extract for each component

    Returns:
        dict[str, tuple[Any, ...]]: Registry mapping component names to tuples of (ComponentClass, *additional_values)
    """
    registry = {}

    if config_keys is None:
        config_keys = ()

    for name, details in component_config.items():
        try:
            # Extract required fields
            module_name = details["module"]
            class_name = details["class"]

            # Dynamically import the module and get the class
            module = importlib.import_module(module_name)
            ComponentClass = getattr(module, class_name)

            # Extract additional config values
            additional_values = tuple(details[key] for key in config_keys)

            # Store in registry as (Class, *additional_values)
            registry[name] = (ComponentClass, *additional_values)

        except (KeyError, ImportError, AttributeError) as e:
            logger.error(f"Failed to load component '{name}': {e}", exc_info=True)
            continue

    return registry


def get_parser_registry(config) -> dict[str, tuple[Any, str, str]]:
    """Get the registry of available parsers.

    Args:
        config: WikiConfig instance containing parsers_registry

    Returns:
        dict[str, tuple[Any, str, str]]: Registry mapping parser names to (ParserClass, input_file, output_dir) tuples
    """
    return get_component_registry(config.parsers_registry, ("input_file", "output_dir"))


def get_generator_registry(config) -> dict[str, tuple[Any, Any, str]]:
    """
    Get the registry of available generators.

    Args:
        config: WikiConfig instance containing generators_registry

    Returns:
        dict[str, tuple[Any, Any, str]]: Registry mapping generator names to (GeneratorClass, config, output_dir) tuples
    """
    # Get the base registry with output_dir
    base_registry = get_component_registry(config.generators_registry, ("output_dir",))
    # Transform to 3-element tuples by inserting config
    registry_with_config = {}
    for name, (GeneratorClass, output_dir) in base_registry.items():
        registry_with_config[name] = (GeneratorClass, config, output_dir)

    return registry_with_config
