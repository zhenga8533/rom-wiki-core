"""
Service for copying new moves from newer generation to parsed data folder.
"""

from typing import Any

import orjson

from rom_wiki_core.utils.core.config_registry import get_config
from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.logger import get_logger
from rom_wiki_core.utils.services.base_service import BaseService
from rom_wiki_core.utils.text.dict_util import get_most_common_value

logger = get_logger(__name__)


class MoveService(BaseService):
    """Service for copying moves from newer generation to parsed folder."""

    @staticmethod
    def _normalize_version_group_fields(data: dict[str, Any], field_name: str) -> None:
        """Normalize version group fields to only include configured version groups.

        Args:
            data: The move data dictionary.
            field_name: The name of the field to process (e.g., "accuracy", "type").
        """
        if field_name not in data:
            return

        field_value = data[field_name]

        # Only process if it's a dict (version group mapping)
        if not isinstance(field_value, dict):
            return

        # Get most common value from existing version groups
        most_common = get_most_common_value(field_value)

        # Create new dict with only configured version groups
        normalized_value = {}
        config = get_config()
        for version_group in config.pokedb_version_groups:
            # Use existing value if present, otherwise use most common
            normalized_value[version_group] = field_value.get(version_group, most_common)
            if version_group not in field_value:
                logger.debug(f"Added {version_group} to {field_name}: {most_common}")

        # Replace the field value with normalized version
        data[field_name] = normalized_value

    @staticmethod
    def _process_move_data(data: dict[str, Any]) -> dict[str, Any]:
        """Process move data by normalizing version group fields to match config.

        Args:
            data: The move data dictionary.

        Returns:
            The modified move data with normalized version group fields.
        """
        # Fields that use GameVersionIntMap or GameVersionStringMap
        version_fields = [
            "accuracy",
            "power",
            "pp",
            "type",
            "effect_chance",
            "effect",
            "short_effect",
            "flavor_text",
        ]

        for field in version_fields:
            MoveService._normalize_version_group_fields(data, field)

        return data

    @staticmethod
    def copy_new_move(move_name: str) -> bool:
        """Copy a new move from newer generation to parsed data folder.

        Args:
            move_name: Name of the move to copy (will be converted to ID).

        Returns:
            True if copied, False if skipped or error.
        """
        from rom_wiki_core.utils.text.text_util import name_to_id

        # Normalize move name
        move_id = name_to_id(move_name)

        # Use PokeDBLoader to get paths
        data_dir = PokeDBLoader.get_data_dir()
        config = get_config()
        source_gen = config.pokedb_generations[-1]  # Use the latest generation as source
        source_move_dir = data_dir.parent / source_gen / "move"
        parsed_move_dir = PokeDBLoader.get_category_path("move")

        # Construct file paths
        source_path = source_move_dir / f"{move_id}.json"
        dest_path = parsed_move_dir / f"{move_id}.json"

        # Check if source exists
        if not source_path.exists():
            logger.warning(f"Move '{move_name}' not found in {source_gen}: {source_path}")
            return False

        # Skip if destination already exists (return True since move is available)
        if dest_path.exists():
            logger.debug(f"Move '{move_name}' already exists in parsed data, skipping")
            return True

        # Create destination directory if needed
        parsed_move_dir.mkdir(parents=True, exist_ok=True)

        # Load, process, and save the move data
        try:
            # Load move data using orjson (2-3x faster than json)
            with open(source_path, "rb") as f:
                move_data = orjson.loads(f.read())

            # Process to add configured version group fields
            processed_data = MoveService._process_move_data(move_data)

            # Save to parsed folder using orjson
            with open(dest_path, "wb") as f:
                f.write(
                    orjson.dumps(
                        processed_data,
                        option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS,
                    )
                )

            logger.info(f"Copied and processed move '{move_name}' from {source_gen} to parsed")
            return True
        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error copying move '{move_name}': {e}")
            return False

    @staticmethod
    def update_move_power(move_id: str, power: int | None) -> bool:
        """Update the power of a move.

        Args:
            move_id: The ID of the move (e.g., "thunderbolt", "hyper-beam").
            power: The new power value, or None for status moves.

        Returns:
            True if updated successfully, False otherwise.
        """
        try:
            move = PokeDBLoader.load_move(move_id)
            if move is None:
                logger.warning(f"Move '{move_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            config = get_config()
            old_value = getattr(move.power, config.version_group, None)

            # Update all version groups
            for version_key in move.power.keys():
                setattr(move.power, version_key, power)

            # Record change
            BaseService.record_change(
                move,
                field="Power",
                old_value=str(old_value) if old_value is not None else "None",
                new_value=str(power) if power is not None else "None",
                source="move_service",
            )

            PokeDBLoader.save_move(move_id, move)
            logger.info(f"Updated power of move '{move_id}' to {power}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating power of move '{move_id}': {e}")
            return False

    @staticmethod
    def update_move_pp(move_id: str, pp: int) -> bool:
        """Update the PP of a move.

        Args:
            move_id: The ID of the move.
            pp: The new PP value.

        Returns:
            True if updated successfully, False otherwise.
        """
        try:
            move = PokeDBLoader.load_move(move_id)
            if move is None:
                logger.warning(f"Move '{move_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            config = get_config()
            old_value = getattr(move.pp, config.version_group, None)

            # Update all version groups
            for version_key in move.pp.keys():
                setattr(move.pp, version_key, pp)

            # Record change
            BaseService.record_change(
                move,
                field="PP",
                old_value=str(old_value) if old_value is not None else "None",
                new_value=str(pp),
                source="move_service",
            )

            PokeDBLoader.save_move(move_id, move)
            logger.info(f"Updated PP of move '{move_id}' to {pp}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating PP of move '{move_id}': {e}")
            return False

    @staticmethod
    def update_move_accuracy(move_id: str, accuracy: int | None) -> bool:
        """Update the accuracy of a move.

        Args:
            move_id: The ID of the move.
            accuracy: The new accuracy value (0-100), or None for moves that never miss.

        Returns:
            True if updated successfully, False otherwise.
        """
        try:
            move = PokeDBLoader.load_move(move_id)
            if move is None:
                logger.warning(f"Move '{move_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            config = get_config()
            old_value = getattr(move.accuracy, config.version_group, None)

            # Update all version groups
            for version_key in move.accuracy.keys():
                setattr(move.accuracy, version_key, accuracy)

            # Record change
            BaseService.record_change(
                move,
                field="Accuracy",
                old_value=str(old_value) if old_value is not None else "Never Misses",
                new_value=str(accuracy) if accuracy is not None else "Never Misses",
                source="move_service",
            )

            PokeDBLoader.save_move(move_id, move)
            logger.info(f"Updated accuracy of move '{move_id}' to {accuracy}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating accuracy of move '{move_id}': {e}")
            return False

    @staticmethod
    def update_move_priority(move_id: str, priority: int) -> bool:
        """Update the priority of a move.

        Args:
            move_id: The ID of the move.
            priority: The new priority value (-7 to +5).

        Returns:
            True if updated successfully, False otherwise.
        """
        try:
            move = PokeDBLoader.load_move(move_id)
            if move is None:
                logger.warning(f"Move '{move_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_value = move.priority

            # Update priority (plain int, not version-grouped)
            move.priority = priority

            # Record change
            BaseService.record_change(
                move,
                field="Priority",
                old_value=str(old_value),
                new_value=str(priority),
                source="move_service",
            )

            PokeDBLoader.save_move(move_id, move)
            logger.info(f"Updated priority of move '{move_id}' to {priority}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating priority of move '{move_id}': {e}")
            return False

    @staticmethod
    def update_move_type(move_id: str, type_id: str) -> bool:
        """Update the type of a move.

        Args:
            move_id: The ID of the move.
            type_id: The new type ID (e.g., "fire", "water", "electric").

        Returns:
            True if updated successfully, False otherwise.
        """
        try:
            move = PokeDBLoader.load_move(move_id)
            if move is None:
                logger.warning(f"Move '{move_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            config = get_config()
            old_value = getattr(move.type, config.version_group, None)

            # Update all version groups
            for version_key in move.type.keys():
                setattr(move.type, version_key, type_id)

            # Record change
            BaseService.record_change(
                move,
                field="Type",
                old_value=str(old_value) if old_value else "None",
                new_value=type_id,
                source="move_service",
            )

            PokeDBLoader.save_move(move_id, move)
            logger.info(f"Updated type of move '{move_id}' to {type_id}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating type of move '{move_id}': {e}")
            return False
