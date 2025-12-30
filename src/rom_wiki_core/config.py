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
        """Set default paths based on project_root if not provided and validate configuration.

        Raises:
            ValueError: If configuration validation fails
            TypeError: If configuration types are incorrect
        """
        # Validate required fields
        self._validate_required_fields()

        # Set default paths
        if not self.pokedb_data_dir:
            self.pokedb_data_dir = str(self.project_root / "data" / "pokedb")

        if not self.logging_log_dir:
            self.logging_log_dir = str(self.project_root / "logs")

        # Validate configuration values
        self._validate_configuration()

    def _validate_required_fields(self) -> None:
        """Validate that all required fields are populated.

        Raises:
            ValueError: If required fields are missing or invalid
            TypeError: If field types are incorrect
        """
        # Validate project_root
        if not isinstance(self.project_root, Path):
            raise TypeError(
                f"project_root must be a Path object, got {type(self.project_root).__name__}"
            )

        # Validate game information
        if not self.game_title or not self.game_title.strip():
            raise ValueError("game_title cannot be empty")

        if not self.version_group or not self.version_group.strip():
            raise ValueError("version_group cannot be empty")

        if not self.version_group_friendly or not self.version_group_friendly.strip():
            raise ValueError("version_group_friendly cannot be empty")

        # Validate PokeDB configuration
        if not self.pokedb_repo_url or not self.pokedb_repo_url.strip():
            raise ValueError("pokedb_repo_url cannot be empty")

        if not self.pokedb_branch or not self.pokedb_branch.strip():
            raise ValueError("pokedb_branch cannot be empty")

        if not self.pokedb_generations:
            raise ValueError("pokedb_generations cannot be empty")

        if not self.pokedb_version_groups:
            raise ValueError("pokedb_version_groups cannot be empty")

        if not self.pokedb_game_versions:
            raise ValueError("pokedb_game_versions cannot be empty")

        if not self.pokedb_sprite_version or not self.pokedb_sprite_version.strip():
            raise ValueError("pokedb_sprite_version cannot be empty")

    def _validate_configuration(self) -> None:
        """Validate configuration values and ranges.

        Raises:
            ValueError: If configuration values are invalid
        """
        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging_level.upper() not in valid_log_levels:
            raise ValueError(
                f"logging_level must be one of {valid_log_levels}, got '{self.logging_level}'"
            )

        valid_log_formats = ["text", "json"]
        if self.logging_format not in valid_log_formats:
            raise ValueError(
                f"logging_format must be one of {valid_log_formats}, got '{self.logging_format}'"
            )

        if self.logging_max_log_size_mb <= 0:
            raise ValueError(
                f"logging_max_log_size_mb must be positive, got {self.logging_max_log_size_mb}"
            )

        if self.logging_backup_count < 0:
            raise ValueError(
                f"logging_backup_count must be non-negative, got {self.logging_backup_count}"
            )

        # Validate URL format
        if not self.pokedb_repo_url.startswith(("http://", "https://")):
            raise ValueError(
                f"pokedb_repo_url must start with http:// or https://, got '{self.pokedb_repo_url}'"
            )

        # Validate registries are dictionaries
        if not isinstance(self.parsers_registry, dict):
            raise TypeError(
                f"parsers_registry must be a dict, got {type(self.parsers_registry).__name__}"
            )

        if not isinstance(self.generators_registry, dict):
            raise TypeError(
                f"generators_registry must be a dict, got {type(self.generators_registry).__name__}"
            )
