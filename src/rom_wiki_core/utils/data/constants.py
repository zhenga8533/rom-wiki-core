"""
Shared constants for Pokemon-related data and formatting.

This module centralizes all commonly-used constants across the codebase to ensure
consistency and make updates easier. Rather than duplicating these values across
multiple files, they are defined once here and imported where needed.
"""

# ============================================================================
# Display Name Special Cases
# ============================================================================
POKEMON_DISPLAY_CASES: dict[str, str] = {
    "mr mime": "Mr. Mime",
    "mime jr": "Mime Jr.",
    "farfetchd": "Farfetchˈd",
    "nidoran m": "Nidoran♂",
    "nidoran f": "Nidoran♀",
    "ho oh": "Ho-Oh",
}

ITEM_DISPLAY_CASES: dict[str, str] = {
    "pp": "PP",
    "tm": "TM",
    "hm": "HM",
    "hp": "HP",
    "x-sp": "X Sp.",
    "gs": "GS",
    "ss": "S.S.",
}

ITEM_DISPLAY_ABBREVIATIONS: dict[str, str] = {
    "exp share": "Exp. Share",
    "kings rock": "King's Rock",
}

MOVE_DISPLAY_CASES: dict[str, str] = {
    "u turn": "U-turn",
    "x scissor": "X-Scissor",
    "will o wisp": "Will-O-Wisp",
    "v create": "V-create",
}

# ============================================================================
# Type-Related Constants
# ============================================================================

TYPE_COLORS: dict[str, str] = {
    "normal": "#A8A878",
    "fire": "#F08030",
    "water": "#6890F0",
    "electric": "#F8D030",
    "grass": "#78C850",
    "ice": "#98D8D8",
    "fighting": "#C03028",
    "poison": "#A040A0",
    "ground": "#E0C068",
    "flying": "#A890F0",
    "psychic": "#F85888",
    "bug": "#A8B820",
    "rock": "#B8A038",
    "ghost": "#705898",
    "dragon": "#7038F8",
    "dark": "#705848",
    "steel": "#B8B8D0",
    "fairy": "#EE99AC",
    "shadow": "#4B4B7B",
}

TYPE_CATEGORY_COLORS: dict[str, str] = {
    "physical": "#C03028",
    "special": "#6890F0",
    "status": "#A8A878",
}

TYPE_CHART: dict[str, dict[str, list[str]]] = {
    "normal": {
        "weak_to": ["fighting"],
        "resistant_to": [],
        "immune_to": ["ghost"],
    },
    "fire": {
        "weak_to": ["water", "ground", "rock"],
        "resistant_to": ["fire", "grass", "ice", "bug", "steel", "fairy"],
        "immune_to": [],
    },
    "water": {
        "weak_to": ["electric", "grass"],
        "resistant_to": ["fire", "water", "ice", "steel"],
        "immune_to": [],
    },
    "electric": {
        "weak_to": ["ground"],
        "resistant_to": ["electric", "flying", "steel"],
        "immune_to": [],
    },
    "grass": {
        "weak_to": ["fire", "ice", "poison", "flying", "bug"],
        "resistant_to": ["water", "electric", "grass", "ground"],
        "immune_to": [],
    },
    "ice": {
        "weak_to": ["fire", "fighting", "rock", "steel"],
        "resistant_to": ["ice"],
        "immune_to": [],
    },
    "fighting": {
        "weak_to": ["flying", "psychic", "fairy"],
        "resistant_to": ["bug", "rock", "dark"],
        "immune_to": [],
    },
    "poison": {
        "weak_to": ["ground", "psychic"],
        "resistant_to": ["grass", "fighting", "poison", "bug", "fairy"],
        "immune_to": [],
    },
    "ground": {
        "weak_to": ["water", "grass", "ice"],
        "resistant_to": ["poison", "rock"],
        "immune_to": ["electric"],
    },
    "flying": {
        "weak_to": ["electric", "ice", "rock"],
        "resistant_to": ["grass", "fighting", "bug"],
        "immune_to": ["ground"],
    },
    "psychic": {
        "weak_to": ["bug", "ghost", "dark"],
        "resistant_to": ["fighting", "psychic"],
        "immune_to": [],
    },
    "bug": {
        "weak_to": ["fire", "flying", "rock"],
        "resistant_to": ["grass", "fighting", "ground"],
        "immune_to": [],
    },
    "rock": {
        "weak_to": ["water", "grass", "fighting", "ground", "steel"],
        "resistant_to": ["normal", "fire", "poison", "flying"],
        "immune_to": [],
    },
    "ghost": {
        "weak_to": ["ghost", "dark"],
        "resistant_to": ["poison", "bug"],
        "immune_to": ["normal", "fighting"],
    },
    "dragon": {
        "weak_to": ["ice", "dragon", "fairy"],
        "resistant_to": ["fire", "water", "electric", "grass"],
        "immune_to": [],
    },
    "dark": {
        "weak_to": ["fighting", "bug", "fairy"],
        "resistant_to": ["ghost", "dark"],
        "immune_to": ["psychic"],
    },
    "steel": {
        "weak_to": ["fire", "fighting", "ground"],
        "resistant_to": [
            "normal",
            "grass",
            "ice",
            "flying",
            "psychic",
            "bug",
            "rock",
            "dragon",
            "steel",
            "fairy",
        ],
        "immune_to": ["poison"],
    },
    "fairy": {
        "weak_to": ["poison", "steel"],
        "resistant_to": ["fighting", "bug", "dark"],
        "immune_to": ["dragon"],
    },
}

# ============================================================================
# Pokemon Form Subfolders
# ============================================================================

POKEMON_FORM_SUBFOLDERS = ["default", "transformation", "variant", "cosmetic"]


# ============================================================================
# Stat Constants
# ============================================================================

# Canonical stat slugs matching the Stats dataclass field names (snake_case)
class StatSlug:
    """Canonical stat identifiers matching Stats dataclass fields."""

    HP = "hp"
    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"

    @classmethod
    def all(cls) -> list[str]:
        """Return all valid stat slugs."""
        return [cls.HP, cls.ATTACK, cls.DEFENSE, cls.SPECIAL_ATTACK, cls.SPECIAL_DEFENSE, cls.SPEED]


# Display name -> canonical slug mapping
# Keys are lowercase for case-insensitive lookup
STAT_ALIASES: dict[str, str] = {
    # Canonical (already correct)
    "hp": StatSlug.HP,
    "attack": StatSlug.ATTACK,
    "defense": StatSlug.DEFENSE,
    "special_attack": StatSlug.SPECIAL_ATTACK,
    "special_defense": StatSlug.SPECIAL_DEFENSE,
    "speed": StatSlug.SPEED,
    # Kebab-case (used in StatChange, EVYield models)
    "special-attack": StatSlug.SPECIAL_ATTACK,
    "special-defense": StatSlug.SPECIAL_DEFENSE,
    # Full display names
    "special attack": StatSlug.SPECIAL_ATTACK,
    "special defense": StatSlug.SPECIAL_DEFENSE,
    "sp. attack": StatSlug.SPECIAL_ATTACK,
    "sp. defense": StatSlug.SPECIAL_DEFENSE,
    "sp. atk": StatSlug.SPECIAL_ATTACK,
    "sp. def": StatSlug.SPECIAL_DEFENSE,
    # Common abbreviations
    "atk": StatSlug.ATTACK,
    "def": StatSlug.DEFENSE,
    "satk": StatSlug.SPECIAL_ATTACK,
    "sdef": StatSlug.SPECIAL_DEFENSE,
    "spatk": StatSlug.SPECIAL_ATTACK,
    "spdef": StatSlug.SPECIAL_DEFENSE,
    "spa": StatSlug.SPECIAL_ATTACK,
    "spd": StatSlug.SPECIAL_DEFENSE,
    "spe": StatSlug.SPEED,
}


def normalize_stat(name: str, aliases: dict[str, str] | None = None) -> str | None:
    """Convert any stat name variant to canonical slug (snake_case).

    Args:
        name: The stat name to normalize (any case, any format)
        aliases: Optional custom alias mapping. Defaults to STAT_ALIASES.

    Returns:
        Canonical stat slug (e.g., "special_attack") or None if not recognized.

    Examples:
        >>> normalize_stat("Special Attack")
        'special_attack'
        >>> normalize_stat("SAtk")
        'special_attack'
        >>> normalize_stat("special-defense")
        'special_defense'
    """
    if aliases is None:
        aliases = STAT_ALIASES
    return aliases.get(name.lower().strip())


# Canonical slug -> short display name (for formatted output)
STAT_DISPLAY_NAMES: dict[str, str] = {
    StatSlug.HP: "HP",
    StatSlug.ATTACK: "Atk",
    StatSlug.DEFENSE: "Def",
    StatSlug.SPECIAL_ATTACK: "SAtk",
    StatSlug.SPECIAL_DEFENSE: "SDef",
    StatSlug.SPEED: "Spd",
    # Also handle kebab-case (EVYield model format)
    "special-attack": "SAtk",
    "special-defense": "SDef",
}


def stat_to_display(slug: str) -> str:
    """Convert a stat slug to its short display name.

    Args:
        slug: The stat slug (snake_case or kebab-case)

    Returns:
        Short display name (e.g., "SAtk") or the original slug if not found.
    """
    return STAT_DISPLAY_NAMES.get(slug, slug)
