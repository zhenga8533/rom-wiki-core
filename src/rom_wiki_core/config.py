"""
Base configuration class for ROM hack wiki generation.

This module provides the WikiConfig dataclass that serves as the foundation
for project-specific configurations. Each wiki project should create its own
instance of WikiConfig with appropriate values.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WikiConfig:
    """
    Base configuration for ROM hack wiki generation.

    This class should be instantiated in each wiki project with project-specific
    values. All reusable components (generators, services, etc.) accept a
    WikiConfig instance for dependency injection.

    Example:
        config = WikiConfig(
            project_root=Path("/path/to/project"),
            game_title="My ROM Hack",
            version_group="black_2_white_2",
            ...
        )
    """

    # ============================================================================
    # Project Root Configuration
    # ============================================================================

    project_root: Path

    # ============================================================================
    # Game Information
    # ============================================================================

    game_title: str
    version_group: str
    version_group_friendly: str

    # ============================================================================
    # PokeDB Configuration
    # ============================================================================

    pokedb_repo_url: str = "https://github.com/zhenga8533/pokedb"
    pokedb_branch: str = "data"
    pokedb_data_dir: str = ""  # Will be set in __post_init__ if empty
    pokedb_generations: list[str] = field(default_factory=lambda: ["gen5", "gen8"])
    pokedb_version_groups: list[str] = field(default_factory=lambda: ["black_white", "black_2_white_2"])
    pokedb_game_versions: list[str] = field(default_factory=lambda: ["black", "white", "black_2", "white_2"])
    pokedb_sprite_version: str = "black_white"

    # ============================================================================
    # Logging Configuration
    # ============================================================================

    logging_level: str = "DEBUG"
    logging_format: str = "text"
    logging_log_dir: str = ""  # Will be set in __post_init__ if empty
    logging_max_log_size_mb: int = 10
    logging_backup_count: int = 5
    logging_console_colors: bool = True
    logging_clear_on_run: bool = True

    # ============================================================================
    # Parser Registry
    # ============================================================================

    parsers_registry: dict[str, dict[str, Any]] = field(default_factory=dict)
    parser_dex_relative_path: str = ".."

    # ============================================================================
    # Generator Registry
    # ============================================================================

    generators_registry: dict[str, dict[str, Any]] = field(default_factory=dict)
    generator_dex_relative_path: str = "../.."
    generator_index_relative_path: str = ".."

    # Location generator configuration
    location_index_columns: list[str] | None = None  # None = all columns shown

    def __post_init__(self):
        """Set default paths based on project_root if not provided."""
        if not self.pokedb_data_dir:
            self.pokedb_data_dir = str(self.project_root / "data" / "pokedb")

        if not self.logging_log_dir:
            self.logging_log_dir = str(self.project_root / "logs")
