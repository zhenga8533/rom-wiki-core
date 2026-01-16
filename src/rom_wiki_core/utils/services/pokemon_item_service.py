"""
Service for updating Pokemon held item data.
"""

from rom_wiki_core.utils.core.config_registry import get_config
from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.logger import get_logger
from rom_wiki_core.utils.services.base_service import BaseService

logger = get_logger(__name__)


class PokemonItemService(BaseService):
    """Service for updating Pokemon held item data."""

    @staticmethod
    def update_held_item(pokemon_id: str, item_id: str, rarity: int) -> bool:
        """Update held item for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "deoxys-attack").
            item_id: The ID of the held item (e.g., "light-ball", "oran-berry").
            rarity: The percentage chance (0-100) of the item being held.

        Returns:
            True if the held item was updated successfully, False otherwise.
        """
        try:
            # Load the Pokemon using PokeDBLoader
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Validate item exists in database
            item_data = PokeDBLoader.load_item(item_id)
            if not item_data:
                logger.warning(
                    f"Item '{item_id}' not found in database. Skipping validation but saving anyway."
                )

            # Capture old held items for change tracking
            old_held_items = list(pokemon_data.held_items.keys())

            # Update held_items
            # Structure: {item_name: {version_group: rarity}}
            if item_id not in pokemon_data.held_items:
                pokemon_data.held_items[item_id] = {}

            config = get_config()
            pokemon_data.held_items[item_id][config.version_group] = rarity

            # Record change (only if new item added)
            new_held_items = list(pokemon_data.held_items.keys())
            if item_id not in old_held_items:
                BaseService.record_change(
                    pokemon_data,
                    field="Held Items",
                    old_value=", ".join(old_held_items) if old_held_items else "None",
                    new_value=", ".join(new_held_items),
                    source="pokemon_item_service",
                )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated held item for '{pokemon_id}': {item_id} at {rarity}% rate")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating held item for '{pokemon_id}': {e}")
            return False
