"""
Service for updating Pokemon move-related data (level-up moves, TMs/HMs).
"""

from rom_wiki_core.utils.core.config_registry import get_config
from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.logger import get_logger
from rom_wiki_core.utils.data.models import MoveLearn
from rom_wiki_core.utils.services.base_service import BaseService

logger = get_logger(__name__)


class PokemonMoveService(BaseService):
    """Service for updating Pokemon move-related data."""

    @staticmethod
    def update_levelup_moves(pokemon_id: str, moves: list[MoveLearn]) -> bool:
        """Update level-up moves for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "deoxys-attack").
            moves: A list of MoveLearn objects representing the new level-up moves.

        Returns:
            True if the level-up moves were updated successfully, False otherwise.
        """
        try:
            # Load the Pokemon using PokeDBLoader
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Validate moves exist in database
            for move in moves:
                move_data = PokeDBLoader.load_move(move.name)
                if not move_data:
                    logger.warning(
                        f"Move '{move.name}' not found in database. Skipping validation but saving anyway."
                    )

            # Capture old moves for change tracking
            old_moves = [
                {"name": m.name, "level_learned_at": m.level_learned_at}
                for m in pokemon_data.moves.level_up
            ]
            new_moves_dict = [
                {"name": m.name, "level_learned_at": m.level_learned_at} for m in moves
            ]

            # Replace level_up moves
            pokemon_data.moves.level_up = moves

            # Record change
            old_value, new_value = BaseService.format_move_list_change(old_moves, new_moves_dict)
            BaseService.record_change(
                pokemon_data,
                field="Level-up Moves",
                old_value=old_value,
                new_value=new_value,
                source="pokemon_move_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated level-up moves for '{pokemon_id}': {len(moves)} moves")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating level-up moves for '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_move_category(pokemon_id: str, category: str, move_ids: list[str]) -> bool:
        """Update TM/HM/Tutor/Egg move compatibility for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            category: The category of move ("egg", "tutor", "machine").
            move_ids: A list of move IDs to add (e.g., ["thunderbolt", "ice-beam"]).

        Returns:
            True if the moves were updated successfully, False otherwise.
        """
        try:
            # Load the Pokemon using PokeDBLoader
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Determine which category to update
            if category == "machine":
                pokemon_moves = pokemon_data.moves.machine
            elif category == "tutor":
                pokemon_moves = pokemon_data.moves.tutor
            elif category == "egg":
                pokemon_moves = pokemon_data.moves.egg
            else:
                logger.warning(f"Invalid move category '{category}' specified")
                return False

            # Capture old moves for change tracking
            old_moves = [m.name for m in pokemon_moves]

            # Add new moves
            added_moves = []
            config = get_config()
            for move_id in move_ids:
                # Validate move exists in database
                move_data = PokeDBLoader.load_move(move_id)
                if not move_data:
                    logger.warning(
                        f"Move '{move_id}' not found in database. Skipping validation but saving anyway."
                    )

                # Check if move already exists in moves
                existing_move = None
                for m in pokemon_moves:
                    if m.name == move_id:
                        existing_move = m
                        break

                if existing_move:
                    # Update version groups if needed
                    if config.version_group not in existing_move.version_groups:
                        existing_move.version_groups.append(config.version_group)
                else:
                    # Add new move as a MoveLearn object
                    new_move = MoveLearn(
                        name=move_id,
                        level_learned_at=0,
                        version_groups=[config.version_group],
                    )
                    pokemon_moves.append(new_move)
                    added_moves.append(move_id)

            # Record change (only if moves were added)
            if added_moves:
                BaseService.record_change(
                    pokemon_data,
                    field=f"{category.capitalize()} Moves",
                    old_value=f"{len(old_moves)} moves",
                    new_value=f"{len(pokemon_moves)} moves (added: {', '.join(added_moves[:5])}{'...' if len(added_moves) > 5 else ''})",
                    source="pokemon_move_service",
                )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated {category} moves for '{pokemon_id}': added {len(added_moves)} moves")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating {category} moves for '{pokemon_id}': {e}")
            return False
