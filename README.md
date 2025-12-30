# ROM Wiki Core

A reusable Python library for generating MkDocs wikis for Pokemon ROM hacks. This package contains all the core functionality (generators, services, formatters, data models) that can be shared across different ROM hack wiki projects.

## Features

- **Modular Architecture** - Reusable generators, services, and formatters
- **Config Registry Pattern** - Clean, global configuration management with thread-safe access
- **Dependency Injection** - Pass config once, use everywhere
- **PokeDB Integration** - Automatic data loading from PokeDB repository
- **MkDocs Compatible** - Generates markdown pages ready for MkDocs Material
- **Type Safe** - Comprehensive dataclasses for Pokemon, moves, items, abilities
- **Extensible** - Easy to customize for different ROM hacks

## Installation

### As a Git Dependency

Add to your `pyproject.toml`:

```toml
dependencies = [
    "rom-wiki-core @ git+https://github.com/zhenga8533/rom-wiki-core.git",
]
```

Then install:

```bash
pip install -e .
```

### Local Development

For developing the library itself:

```bash
git clone https://github.com/zhenga8533/rom-wiki-core.git
cd rom-wiki-core
pip install -e .
```

## Quick Start

### 1. Create Your Wiki Project

```python
# my_romhack_wiki/config.py
from pathlib import Path
from rom_wiki_core.config import WikiConfig

PROJECT_ROOT = Path(__file__).parent

CONFIG = WikiConfig(
    project_root=PROJECT_ROOT,
    game_title="My ROM Hack Name",
    version_group="black_2_white_2",
    version_group_friendly="Black 2 & White 2",

    # PokeDB settings
    pokedb_generations=["gen5", "gen8"],
    pokedb_version_groups=["black_white", "black_2_white_2"],
    pokedb_game_versions=["black", "white", "black_2", "white_2"],
    pokedb_sprite_version="black_white",

    # Generator outputs
    generators_registry={
        "pokemon": {
            "module": "rom_wiki_core.generators.pokemon_generator",
            "class": "PokemonGenerator",
            "output_dir": str(PROJECT_ROOT / "docs" / "pokedex"),
        },
        # Add other generators...
    }
)
```

### 2. Initialize the System

```python
# my_romhack_wiki/main.py
from rom_wiki_core.utils.core.config_registry import set_config
from rom_wiki_core.utils.data import models
from rom_wiki_core.utils.core import logger
from my_romhack_wiki.config import CONFIG

# Set config globally (enables formatters to work automatically)
set_config(CONFIG)

# Configure modules
models.configure_models(CONFIG)
logger.configure_logging_system(CONFIG)
```

### 3. Generate Documentation

```python
from rom_wiki_core.generators import PokemonGenerator
from rom_wiki_core.utils.core.initializer import PokeDBInitializer

# Initialize PokeDB data (first time only)
initializer = PokeDBInitializer(CONFIG)
initializer.run()

# Generate Pokemon pages (config auto-registered when passed to generator)
pokemon_gen = PokemonGenerator(config=CONFIG)
pokemon_gen.generate()
```

## Architecture

```
rom-wiki-core/
├── src/
│   └── rom_wiki_core/
│       ├── config.py              # WikiConfig dataclass
│       ├── generators/            # Page generators
│       │   ├── pokemon_generator.py
│       │   ├── move_generator.py
│       │   ├── ability_generator.py
│       │   ├── item_generator.py
│       │   └── location_generator.py
│       └── utils/
│           ├── core/              # Core utilities
│           │   ├── loader.py      # PokeDB data loader
│           │   ├── logger.py      # Logging system
│           │   ├── registry.py    # Component registry
│           │   └── initializer.py # PokeDB initializer
│           ├── formatters/        # Markdown formatters
│           │   ├── markdown_formatter.py
│           │   ├── table_formatter.py
│           │   └── yaml_formatter.py
│           ├── services/          # Business logic
│           │   ├── move_service.py
│           │   ├── item_service.py
│           │   └── pokemon_move_service.py
│           ├── data/              # Data models & constants
│           │   ├── models.py      # Pokemon, Move, Ability, Item classes
│           │   ├── constants.py   # Type chart, colors, etc.
│           │   └── pokemon.py     # Pokemon utilities
│           └── text/              # Text processing
│               ├── text_util.py   # Name formatting, ID generation
│               └── dict_util.py   # Dictionary utilities
```

## Core Components

### WikiConfig

Central configuration object that's passed to all generators and services:

```python
@dataclass
class WikiConfig:
    project_root: Path
    game_title: str
    version_group: str
    version_group_friendly: str

    # PokeDB settings
    pokedb_repo_url: str
    pokedb_branch: str
    pokedb_data_dir: str
    pokedb_generations: list[str]
    pokedb_version_groups: list[str]
    pokedb_game_versions: list[str]
    pokedb_sprite_version: str

    # Logging settings
    logging_level: str
    logging_log_dir: str
    logging_format: str

    # Component registries
    parsers_registry: dict[str, dict[str, Any]]
    generators_registry: dict[str, dict[str, Any]]
```

### Generators

Generate markdown documentation pages from PokeDB data:

- **PokemonGenerator** - Individual Pokemon pages with stats, moves, evolutions
- **MoveGenerator** - Move pages with power, accuracy, effects
- **AbilityGenerator** - Ability pages with descriptions and Pokemon
- **ItemGenerator** - Item pages with effects and locations
- **LocationGenerator** - Location pages with wild encounters and trainers

All generators accept an optional `config` parameter:

```python
# Recommended: Pass config explicitly
generator = PokemonGenerator(config=config)
generator.generate()

# Alternative: Rely on global config (must call set_config() first)
from rom_wiki_core.utils.core.config_registry import set_config
set_config(config)
generator = PokemonGenerator()  # Uses global config
generator.generate()
```

When you pass config to a generator, it's automatically registered globally, making it available to all formatters.

### Services

Business logic for processing game data:

- **MoveService** - Copy and update moves from newer generations
- **ItemService** - Manage item data
- **PokemonMoveService** - Handle Pokemon learnsets
- **EvolutionService** - Process evolution chains

### Data Models

Strongly-typed dataclasses for all game data:

```python
@dataclass
class Pokemon:
    id: int
    name: str
    types: list[str]
    abilities: list[Ability]
    base_stats: BaseStats
    moves: list[MoveLearn]
    # ... and many more fields
```

## Configuration Management

### Config Registry

The config registry provides global, thread-safe access to your WikiConfig:

```python
from rom_wiki_core.utils.core.config_registry import set_config, get_config

# Set config globally (call once at startup)
set_config(config)

# Now formatters work automatically without passing config
from rom_wiki_core.utils.formatters import format_pokemon
result = format_pokemon("pikachu")  # Uses global config
```

**When is config set?**

1. **Automatically** when you pass config to a generator:

   ```python
   generator = PokemonGenerator(config=config)  # Config auto-registered
   ```

2. **Manually** for parsers or standalone use:
   ```python
   from rom_wiki_core.utils.core.config_registry import set_config
   set_config(config)  # Set explicitly
   ```

### Module Initialization

Some modules require initialization with your WikiConfig:

```python
# Required for version-specific Pokemon data
from rom_wiki_core.utils.data import models
models.configure_models(config)

# Required for logging
from rom_wiki_core.utils.core import logger
logger.configure_logging_system(config)
```

### PokeDB Data

Download Pokemon data from the PokeDB repository:

```python
from rom_wiki_core.utils.core.initializer import PokeDBInitializer

initializer = PokeDBInitializer(config)
initializer.run()  # Downloads to config.pokedb_data_dir
```

## Dependencies

- Python >= 3.12
- mkdocs
- mkdocs-material
- dacite
- orjson
- requests
- pyyaml

See `pyproject.toml` for complete dependency list.

## Examples

### Generate All Documentation

```python
from rom_wiki_core.generators import (
    PokemonGenerator,
    MoveGenerator,
    AbilityGenerator,
    ItemGenerator,
    LocationGenerator
)
from rom_wiki_core.utils.core.config_registry import set_config

# Set config once
set_config(CONFIG)

# Create generators (config auto-registered when passed)
generators = [
    PokemonGenerator(config=CONFIG),
    MoveGenerator(config=CONFIG),
    AbilityGenerator(config=CONFIG),
    ItemGenerator(config=CONFIG),
    LocationGenerator(config=CONFIG),
]

for generator in generators:
    generator.generate()
```

### Use Services

```python
from rom_wiki_core.utils.services import MoveService
from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.config_registry import set_config

# Set config for services
set_config(CONFIG)

# Update moves from newer generation
move_service = MoveService(CONFIG)
move_service.copy_new_moves()

# Load Pokemon data (uses static methods, no config needed)
pokemon = PokeDBLoader.load_pokemon("pikachu")
print(f"{pokemon.name}: {pokemon.stats.hp} HP")
```

### Format Output

```python
from rom_wiki_core.utils.formatters import format_pokemon, format_move, format_type_badge
from rom_wiki_core.utils.core.config_registry import set_config

# Set config once (required for sprite functionality)
set_config(CONFIG)

# Format a Pokemon with sprite and link
formatted = format_pokemon("pikachu", relative_path="..")
# Output: ![](sprites/pikachu.png) [Pikachu](../pokedex/pokemon/pikachu.md)

# Format a type badge
badge = format_type_badge("electric")
# Output: <span class="type-badge" style="background: ...">Electric</span>

# Or pass config explicitly
formatted = format_pokemon("pikachu", relative_path="..", config=CONFIG)
```

## Contributing

Contributions are welcome! This library is designed to support any Pokemon ROM hack wiki project.

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code style guidelines
- Config management best practices
- Testing requirements
- Pull request process

### Quick Start for Contributors

```bash
git clone https://github.com/zhenga8533/rom-wiki-core.git
cd rom-wiki-core
pip install -e ".[dev]"
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Extracted from [bbvw2-redux-wiki](https://github.com/zhenga8533/bbvw2-redux-wiki)
- Uses data from [PokeDB](https://github.com/zhenga8533/pokedb)
- Designed for [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

## Support

For issues, questions, or contributions:

- Open an issue on [GitHub](https://github.com/zhenga8533/rom-wiki-core/issues)
