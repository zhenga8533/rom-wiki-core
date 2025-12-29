# Contributing to ROM Wiki Core

Thank you for considering contributing to ROM Wiki Core! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Config Management Best Practices](#config-management-best-practices)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/zhenga8533/rom-wiki-core.git
   cd rom-wiki-core
   ```

2. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

3. Verify installation:
   ```python
   python -c "import rom_wiki_core; print(rom_wiki_core.__version__)"
   ```

## Code Style

### General Guidelines

- **Python Version**: Use Python 3.12+
- **Formatter**: Black with 100 character line length
- **Type Hints**: Required for all function signatures
- **Docstrings**: Google-style docstrings for all public methods
- **Imports**: Use absolute imports, organize with `isort`

### Example

```python
from pathlib import Path
from typing import Optional

def process_data(
    input_file: Path,
    output_dir: Path,
    config: Optional[object] = None,
) -> bool:
    """Process data from input file and generate output.

    Args:
        input_file: Path to the input file
        output_dir: Directory for output files
        config: Optional WikiConfig instance

    Returns:
        True if successful, False otherwise

    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    # Implementation
    return True
```

## Config Management Best Practices

### For Generators

All generators **must** follow this pattern:

```python
class MyGenerator(BaseGenerator):
    """Generator for XYZ documentation.

    Args:
        BaseGenerator: Abstract base generator class
    """

    def __init__(
        self,
        config=None,
        output_dir: str = "docs/default",
        project_root: Optional[Path] = None,
    ):
        """Initialize the generator.

        Args:
            config: WikiConfig instance with project settings
            output_dir: Directory where markdown files will be generated
            project_root: The root directory of the project. If None, it's inferred
        """
        # ALWAYS call super().__init__ with config as first argument
        super().__init__(config=config, output_dir=output_dir, project_root=project_root)

        # Set generator-specific properties
        self.category = "my_category"
        # ... other initialization
```

**Key Points:**

1. `config` must be the **first parameter** (after `self`)
2. `config` must have a default value of `None`
3. Always pass `config=config` to `super().__init__()`
4. Config is automatically registered globally when passed to generator

### For Formatters

Formatters should support both global config and explicit config:

```python
def format_something(
    value: str,
    config=None,
) -> str:
    """Format a value with config-dependent styling.

    Args:
        value: The value to format
        config: WikiConfig instance. If None, uses global config

    Returns:
        Formatted string

    Raises:
        RuntimeError: If config is None and global config not set
    """
    # Use provided config or fall back to global
    from rom_wiki_core.utils.core.config_registry import get_config

    active_config = config if config is not None else get_config()

    # Use active_config for formatting
    return f"formatted_{value}"
```

**Key Points:**

1. Accept optional `config` parameter
2. Fall back to global config via `get_config()`
3. `get_config()` raises `RuntimeError` if config not set (this is intentional)
4. Document that config is required (either globally or explicitly)

### For Services

Services should accept config in constructor:

```python
class MyService:
    """Service for processing XYZ data.

    Args:
        config: WikiConfig instance with project settings
    """

    def __init__(self, config):
        """Initialize the service.

        Args:
            config: WikiConfig instance
        """
        self.config = config
        # Optionally register globally if service methods use formatters
        from rom_wiki_core.utils.core.config_registry import set_config
        set_config(config)
```

### For Parsers

All parsers **must** follow this pattern:

```python
from rom_wiki_core.parsers import BaseParser

class MyParser(BaseParser):
    """Parser for processing custom documentation files.

    Args:
        BaseParser: Abstract base parser class
    """

    def __init__(
        self,
        config=None,
        input_file: str = "",
        output_dir: str = "docs",
        project_root: Optional[Path] = None,
    ):
        """Initialize the parser.

        Args:
            config: WikiConfig instance with project settings
            input_file: Path to input file (relative to data/documentation/)
            output_dir: Directory where markdown files will be generated
            project_root: The root directory of the project. If None, uses config.project_root
        """
        # ALWAYS call super().__init__ with config as first argument
        super().__init__(
            config=config,
            input_file=input_file,
            output_dir=output_dir,
            project_root=project_root
        )

        # Define sections for your parser
        self._sections = ["Section 1", "Section 2", "Section 3"]

    def parse_section_1(self, line: str) -> None:
        """Handle lines in Section 1."""
        # Custom parsing logic
        self._markdown += f"{line}\n"

    # ... other section handlers
```

**Key Points:**

1. `config` must be the **first parameter** (after `self`)
2. `config` must have a default value of `None`
3. Always pass `config=config` to `super().__init__()`
4. Config is automatically registered globally when passed to parser
5. Define `_sections` list for section-based parsing
6. Implement `parse_<section_name>()` methods for each section

## Testing

### Test Structure

```
tests/
├── generators/
│   ├── test_pokemon_generator.py
│   └── test_move_generator.py
├── formatters/
│   ├── test_markdown_formatter.py
│   └── test_table_formatter.py
└── conftest.py
```

### Test Best Practices

1. **Always clean up global config** between tests:

```python
import pytest
from rom_wiki_core.utils.core.config_registry import clear_config

@pytest.fixture(autouse=True)
def reset_config():
    """Reset global config between tests."""
    yield
    clear_config()
```

2. **Create minimal config** for tests:

```python
from pathlib import Path
from rom_wiki_core.config import WikiConfig

@pytest.fixture
def test_config():
    """Create a minimal test config."""
    return WikiConfig(
        project_root=Path("/tmp/test"),
        game_title="Test ROM",
        version_group="black_2_white_2",
        version_group_friendly="Black 2 & White 2",
        pokedb_sprite_version="black_white",
    )
```

3. **Test both config patterns**:

```python
def test_generator_with_explicit_config(test_config):
    """Test generator with explicitly passed config."""
    gen = PokemonGenerator(config=test_config)
    assert gen.config == test_config

def test_generator_with_global_config(test_config):
    """Test generator using global config."""
    from rom_wiki_core.utils.core.config_registry import set_config

    set_config(test_config)
    gen = PokemonGenerator()
    assert gen.config == test_config
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rom_wiki_core --cov-report=html

# Run specific test file
pytest tests/generators/test_pokemon_generator.py

# Run specific test
pytest tests/generators/test_pokemon_generator.py::test_generate_page
```

## Pull Request Process

### Before Submitting

1. **Code Quality Checks:**
   ```bash
   # Format code
   black src/ tests/

   # Sort imports
   isort src/ tests/

   # Type check
   mypy src/

   # Lint
   ruff check src/ tests/
   ```

2. **Run Tests:**
   ```bash
   pytest
   ```

3. **Update Documentation:**
   - Update README.md if adding new features
   - Update MIGRATION_GUIDE.md if making breaking changes
   - Add docstrings to all new functions/classes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or MIGRATION_GUIDE.md updated)
```

### Review Process

1. **Automated Checks** must pass:
   - Linting
   - Type checking
   - Tests
   - Code coverage (>80%)

2. **Code Review** by maintainer:
   - Adherence to best practices
   - Config management pattern
   - Documentation quality
   - Test coverage

3. **Approval and Merge**:
   - At least one approval required
   - Squash and merge for cleaner history

## Common Patterns

### Adding a New Generator

1. Create generator file in `src/rom_wiki_core/generators/`:

```python
from pathlib import Path
from typing import Any, Optional

from rom_wiki_core.generators.base_generator import BaseGenerator

class MyGenerator(BaseGenerator):
    def __init__(
        self,
        config=None,
        output_dir: str = "docs/my_category",
        project_root: Optional[Path] = None,
    ):
        super().__init__(config=config, output_dir=output_dir, project_root=project_root)
        self.category = "my_category"

    def load_all_data(self) -> list[Any]:
        # Implementation
        pass

    def categorize_data(self, data: list[Any]) -> dict[str, list[Any]]:
        # Implementation
        pass
```

2. Add tests in `tests/generators/test_my_generator.py`
3. Update README.md with usage example
4. Update `__init__.py` exports if needed

### Adding a New Formatter

1. Add function to `src/rom_wiki_core/utils/formatters/markdown_formatter.py`:

```python
def format_my_thing(
    value: str,
    config=None,
) -> str:
    """Format my thing with config-dependent styling.

    Args:
        value: The value to format
        config: WikiConfig instance. If None, uses global config

    Returns:
        Formatted markdown string
    """
    from rom_wiki_core.utils.core.config_registry import get_config

    active_config = config if config is not None else get_config()

    # Use active_config for formatting
    return f"**{value}**"
```

2. Add tests
3. Add to exports and documentation

## Questions?

- Open a [Discussion](https://github.com/zhenga8533/rom-wiki-core/discussions) for general questions
- Open an [Issue](https://github.com/zhenga8533/rom-wiki-core/issues) for bugs or feature requests
- See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrade help

Thank you for contributing! 🎉
