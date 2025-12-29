# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - Base Parser

### Added

- **BaseParser Class**: New abstract base class for documentation file parsing
  - Section-based parsing with automatic method routing
  - Markdown generation from text documentation files
  - Configurable input/output paths using WikiConfig
  - Unicode normalization for section names (e.g., "Pokémon" → "pokemon")
  - Instance-level `self.logger` for child classes to use
  - `parse()` method for automatic section detection and routing
  - `read_input_lines()` with skip pattern filtering
  - `save_markdown()` for output file generation
  - `peek_line()` utility for lookahead parsing
  - `run()` workflow method for complete parsing pipeline
  - Module available via `from rom_wiki_core import BaseParser`
- **LocationParser Class**: Specialized parser for location data management
  - Extends BaseParser with location-specific functionality
  - Load/merge/save location data to JSON files
  - Support for nested sublocations (e.g., "City - Building/Floor")
  - Duplicate prevention tracking across parse runs
  - Safe concurrent updates to location files
  - `_initialize_location_data()` for location setup
  - `_clear_location_data_on_first_encounter()` for idempotent parsing
  - Automatic JSON file persistence in `finalize()`
  - Module available via `from rom_wiki_core import LocationParser`

### Changed

- **Parser Config Pattern**: BaseParser follows same config registry pattern as BaseGenerator
  - Accepts optional `config` parameter (first argument after `self`)
  - Automatically registers config globally when provided
  - Falls back to global config if not provided
  - Uses `config.project_root` for path resolution

### Documentation

- **CONTRIBUTING.md**: Added comprehensive parser guidelines
  - How to create custom parsers extending BaseParser
  - Config registry usage in parsers
  - Section-based parsing patterns
  - Required method signatures and patterns

## [1.0.1] - Fixed Release

### Fixed

- **Config Registry Type Annotations**: Added proper type hints using `TYPE_CHECKING` pattern
  - `get_config()` now correctly returns `WikiConfig` type
  - Prevents type checker errors when accessing config attributes
  - Avoids circular import issues using forward references
- **Service Layer**: Fixed undefined `POKEDB_GENERATIONS` variable in services
  - `MoveService.copy_new_move()` now uses `get_config().pokedb_generations`
  - `ItemService.copy_new_item()` now uses `get_config().pokedb_generations`
- **Logging System**: Major improvements to logger configuration and lifecycle
  - Fixed log directory clearing on Windows with proper file lock handling
  - Logger handlers now correctly recreate after `configure_logging_system()` call
  - Existing loggers (created before config) now get file handlers added back
  - Improved handler detection to only skip when both console and file handlers exist
  - Added fallback to individual file deletion when directory removal fails (Windows)

### Added

- **ItemService Export**: Added `ItemService` to `utils.services.__all__` for proper module exports

### Changed

- **Logging Configuration**: Replaced `logging.shutdown()` with selective file handler closing
  - Prevents disabling the entire logging system during log cleanup
  - Only closes and removes file handlers while keeping console handlers active
  - Automatically re-setups existing loggers after configuration to restore file handlers

## [1.0.0] - Initial Release

### Added

- **Config Registry Pattern**: Global config management system via `config_registry.py`
  - `set_config()` - Set global WikiConfig
  - `get_config()` - Retrieve global WikiConfig
  - `has_config()` - Check if config is set
  - `clear_config()` - Clear config (useful for testing)
- **Automatic Config Registration**: Generators automatically register config globally when instantiated
- **WikiConfig Dataclass**: Centralized configuration with all project settings
- **Formatter Config Support**: All formatters support config for sprite functionality
- **Thread-Safe Config Access**: Config registry uses threading locks for safety
- **Documentation**: Comprehensive README, CONTRIBUTING guide, and examples

### Changed

- **Generator Constructors**: All generators accept `config` as first optional parameter
  - `BaseGenerator.__init__(config=None, output_dir, project_root)`
  - Config is automatically registered globally when passed to generators
- **Formatter Pattern**: Formatters use global config registry with explicit override option
  - Can pass config explicitly or rely on global config
  - `format_pokemon(pokemon, config=None)` - uses global if config not provided
- **Service Pattern**: Services use config registry via `get_config()`

## [0.1.0] - Pre Release

### Added

- Initial extraction from bbvw2-redux-wiki
- Core generators: Pokemon, Move, Ability, Item, Location
- Data models: Pokemon, Move, Ability, Item with dataclasses
- PokeDB integration with automatic data loading
- Markdown formatters with MkDocs Material support
- Type-safe data models with comprehensive validation
- Logging system with rotating file handlers
- Service layer for data manipulation

[1.0.2]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.2
[1.0.1]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.1
[1.0.0]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.0
[0.1.0]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v0.1.0
