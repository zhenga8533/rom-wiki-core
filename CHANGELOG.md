# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-01-16

### Added

- **Stat Normalization Utilities**: New stat slug normalization and display mapping in `constants.py`
  - `STAT_ALIASES` for flexible stat name lookups
  - `STAT_DISPLAY_NAMES` for formatted stat display
  - `normalize_stat()` function for consistent stat handling
- **Ability Update Methods**: New methods to update individual ability slots for Pokémon
  - `update_ability_1()`, `update_ability_2()`, `update_hidden_ability()` in `AttributeService`
- **Individual Stat Update Methods**: New methods to update specific stats
  - `update_hp()`, `update_attack()`, `update_defense()`, etc. in `AttributeService`

### Changed

- **Explicit ID Parameters**: Refactored services to use explicit IDs instead of names
  - `AttributeService`, `ItemService`, `MoveService`, `PokemonItemService`, `PokemonMoveService`
  - Method signatures now use `pokemon_id`, `item_id`, `move_id` for clarity
  - Reduces ambiguity and improves code readability
- **EV Yield Handling**: Refactored EV yield parsing and formatting to use new stat utilities
- **Service Layer Cleanup**: Removed unnecessary name normalization from service layers
  - Centralizes canonical ID usage throughout

### Fixed

- **STAT_ALIASES 'spd' Mapping**: Corrected `'spd'` alias to map to `StatSlug.SPEED` instead of `StatSlug.SPECIAL_DEFENSE`

## [1.0.4] - 2026-01-15

### Added

- **PEP 561 Support**: Added `py.typed` marker file for type checker compatibility
- **Roman Numeral Formatting**: `format_display_name()` now automatically capitalizes valid Roman numerals (I, II, III, IV, etc.)

### Changed

- **Generator Config Parameter**: `config` is now a required parameter in all generators (previously optional)
  - Simplifies initialization and ensures config is always available
  - `project_root` defaults to `config.project_root` when not explicitly provided
- **ROM Changes Display**: Changed from `!!! info` to `??? note` (collapsible admonition), now includes entity name in title
- **Evolution Change Tracking**: Improved change records to show actual evolution method details
  - Old: "Updated" → "Modified evolution method or target"
  - New: "bulbasaur > ivysaur: level-up (level 16)" with full details
  - Supports multiple changes per field for branching evolutions
- **Item Formatting**: Items now wrapped in nowrap span to keep sprite and text on one line
- **Pokemon Card Grid**: Fixed multi-line extra info formatting with proper indentation

### Fixed

- **Duplicate Change Detection**: `BaseService.record_change()` now checks both field AND old_value
  - Allows tracking multiple changes for the same field (e.g., different evolution branches)
  - Previously would overwrite changes for the same field regardless of old_value

### Removed

- **MoveService.update_move_type()**: Removed redundant method, use `update_move_attribute()` instead

## [1.0.3] - 2025-12-30

### Added

- **Config Validation**: Comprehensive validation for WikiConfig fields and values
  - Raises clear errors for misconfiguration
  - Improved error messages for invalid settings
- **Trainer Team Variations**: Support for double battle team variations in markdown
  - LocationGenerator handles 'team_variations' for Left/Right side team listings
  - Trainers with same name and team variations now grouped using tabs
  - Shared metadata displayed once for trainer variations
  - Trainer metadata formatting extracted into `_build_trainer_metadata()` method
- **Configurable Location Index Columns**: New configuration option for location index table
  - `index_columns` parameter in LocationGenerator
  - Allows customization of which columns to display
  - Defaults to all columns if not specified
- **Custom Location Separators**: LocationParser supports custom separators
  - More flexible location/sublocation parsing
  - Configurable separator characters
- **Item Display Cases**: Added display cases for new abbreviations
  - 'gs' → 'GS'
  - 'ss' → 'S.S.'

### Changed

- **PokeDBInitializer Improvements**: Enhanced robustness and developer experience
  - Improved error handling and logging
  - Better standalone execution example
- **Error Handling**: More informative error logging in BaseGenerator
  - Handles various entry types
  - Better error messages for debugging
- **Moves Rendering**: LocationGenerator checks for moves presence before rendering
  - Prevents errors when moves list is missing or empty
- **Ability Handling**: Enhanced attribute service flexibility
  - Accepts 1-3 abilities
  - Correct hidden ability logic
  - Improved validation and logging
  - LocationGenerator only displays ability if present

### Removed

- **settings.local.json**: Removed local settings file from repository

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

[1.0.5]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.5
[1.0.4]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.4
[1.0.3]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.3
[1.0.2]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.2
[1.0.1]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.1
[1.0.0]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v1.0.0
[0.1.0]: https://github.com/zhenga8533/rom-wiki-core/releases/tag/v0.1.0
