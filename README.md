# ROM Wiki Core

A reusable Python library for generating MkDocs wikis for Pokemon ROM hacks. This package contains all the core functionality (generators, services, formatters, data models) that can be shared across different ROM hack wiki projects.

## Features

- **Modular Architecture** - Reusable generators, services, and formatters
- **Dependency Injection** - Clean configuration system via WikiConfig
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
from rom_wiki_core.utils.data import models
from rom_wiki_core.utils.core import logger
from my_romhack_wiki.config import CONFIG

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

# Generate Pokemon pages
pokemon_gen = PokemonGenerator(CONFIG)
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

All generators accept `WikiConfig` in their constructor:

```python
generator = PokemonGenerator(config)
generator.generate()
```

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

## Configuration Requirements

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

## Migration Guide

### From bbvw2-redux-wiki (or Similar)

**Before:**

```python
from bbvw2_redux_wiki.generators.pokemon_generator import PokemonGenerator
from bbvw2_redux_wiki.utils.core import config

generator = PokemonGenerator()
generator.generate()
```

**After:**

```python
from rom_wiki_core.generators import PokemonGenerator
from my_wiki.config import CONFIG

generator = PokemonGenerator(CONFIG)
generator.generate()
```

**Key Changes:**

1. Create a `WikiConfig` instance for your project
2. Call `models.configure_models(config)` on startup
3. Call `logger.configure_logging_system(config)` on startup
4. Pass config to all generators and services
5. Use `rom_wiki_core` imports instead of project-specific imports

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

generators = [
    PokemonGenerator(CONFIG),
    MoveGenerator(CONFIG),
    AbilityGenerator(CONFIG),
    ItemGenerator(CONFIG),
    LocationGenerator(CONFIG),
]

for generator in generators:
    generator.generate()
```

### Use Services

```python
from rom_wiki_core.utils.services import MoveService
from rom_wiki_core.utils.core.loader import PokeDBLoader

# Update moves from newer generation
move_service = MoveService(CONFIG)
move_service.copy_new_moves()

# Load Pokemon data
loader = PokeDBLoader(CONFIG)
pokemon = loader.load_pokemon("pikachu")
print(f"{pokemon.name}: {pokemon.base_stats.hp} HP")
```

### Format Output

```python
from rom_wiki_core.utils.formatters import format_pokemon, format_move, format_type_badge

# Format a Pokemon with sprite and link
formatted = format_pokemon("pikachu", relative_path="..")
# Output: ![](sprites/pikachu.png) [Pikachu](../pokedex/pokemon/pikachu.md)

# Format a type badge
badge = format_type_badge("electric")
# Output: <span class="type-badge" style="background: ...">Electric</span>
```

## Contributing

Contributions are welcome! This library is designed to support any Pokemon ROM hack wiki project.

### Development Setup

```bash
git clone https://github.com/zhenga8533/rom-wiki-core.git
cd rom-wiki-core
pip install -e ".[dev]"
```

### Guidelines

- Follow existing code style (Black formatter, 100 char line length)
- Add type hints to all functions
- Update documentation for new features
- Test with multiple ROM hack configurations

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Extracted from [bbvw2-redux-wiki](https://github.com/zhenga8533/bbvw2-redux-wiki)
- Uses data from [PokeDB](https://github.com/zhenga8533/pokedb)
- Designed for [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)

## Support

For issues, questions, or contributions:

- Open an issue on [GitHub](https://github.com/zhenga8533/rom-wiki-core/issues)
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed migration instructions
- Check [REVIEW_SUMMARY.md](REVIEW_SUMMARY.md) for recent changes and fixes
