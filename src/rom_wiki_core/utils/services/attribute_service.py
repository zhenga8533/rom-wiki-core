"""
Service for updating Pokemon attributes (stats, type, abilities, EVs, etc.).
"""

from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.logger import get_logger
from rom_wiki_core.utils.data.constants import StatSlug
from rom_wiki_core.utils.data.models import EVYield, PokemonAbility, Stats
from rom_wiki_core.utils.services.base_service import BaseService
from rom_wiki_core.utils.text.text_util import name_to_id

logger = get_logger(__name__)


class AttributeService(BaseService):
    """Service for updating Pokemon attributes in parsed data folder."""

    @staticmethod
    def update_base_stats(pokemon_id: str, stats: Stats) -> bool:
        """Update base stats for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "charizard-mega-x").
            stats: The new Stats object with all stat values.

        Returns:
            True if the base stats were updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_value, _ = BaseService.format_stat_change(pokemon_data.stats, None)

            # Update stats object
            pokemon_data.stats = stats

            # Record change
            _, new_value = BaseService.format_stat_change(None, stats)
            BaseService.record_change(
                pokemon_data,
                field="Base Stats",
                old_value=old_value,
                new_value=new_value,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(
                f"Updated base stats for '{pokemon_id}': "
                f"{stats.hp}/{stats.attack}/{stats.defense}/{stats.special_attack}/{stats.special_defense}/{stats.speed}"
            )
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating base stats for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_type(pokemon_id: str, types: list[str]) -> bool:
        """Update type for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            types: List of type slugs (e.g., ["fire", "dragon"] or ["fire"]).

        Returns:
            True if the type was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_types = pokemon_data.types.copy()

            # Update types list
            pokemon_data.types = types

            # Record change
            old_value, new_value = BaseService.format_type_change(old_types, types)
            BaseService.record_change(
                pokemon_data,
                field="Type",
                old_value=old_value,
                new_value=new_value,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            type_str = " / ".join(types)
            logger.info(f"Updated type for '{pokemon_id}': {type_str}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating type for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_abilities(pokemon_id: str, abilities: list[PokemonAbility]) -> bool:
        """Update abilities for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            abilities: List of PokemonAbility objects.

        Returns:
            True if the abilities were updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Validate abilities exist in database
            for ability in abilities:
                ability_data = PokeDBLoader.load_ability(ability.name)
                if not ability_data:
                    logger.warning(
                        f"Ability '{ability.name}' not found in database. Skipping validation but saving anyway."
                    )

            # Capture old value for change tracking
            old_abilities = []
            for a in pokemon_data.abilities:
                if isinstance(a, dict):
                    old_abilities.append(a)
                else:
                    old_abilities.append({"name": a.name, "is_hidden": a.is_hidden, "slot": a.slot})

            # Update abilities
            pokemon_data.abilities = abilities

            # Build new abilities list for change tracking
            new_abilities = [{"name": a.name, "is_hidden": a.is_hidden, "slot": a.slot} for a in abilities]

            # Record change
            old_value, new_value = BaseService.format_ability_change(old_abilities, new_abilities)
            BaseService.record_change(
                pokemon_data,
                field="Abilities",
                old_value=old_value,
                new_value=new_value,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            ability_names = [a.name for a in abilities]
            logger.info(f"Updated abilities for '{pokemon_id}': {' / '.join(ability_names)}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating abilities for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_ev_yield(pokemon_id: str, ev_yield: list[EVYield]) -> bool:
        """Update EV yields for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            ev_yield: List of EVYield objects.

        Returns:
            True if the EV yields were updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_ev_yield = []
            for ev in pokemon_data.ev_yield:
                if isinstance(ev, dict):
                    old_ev_yield.append(ev)
                else:
                    old_ev_yield.append({"stat": ev.stat, "effort": ev.effort})

            # Update EV yield
            pokemon_data.ev_yield = ev_yield

            # Build new ev_yield list for change tracking
            new_ev_yield = [{"stat": ev.stat, "effort": ev.effort} for ev in ev_yield]

            # Record change
            old_value, new_value = BaseService.format_ev_yield_change(old_ev_yield, new_ev_yield)
            BaseService.record_change(
                pokemon_data,
                field="EV Yield",
                old_value=old_value,
                new_value=new_value,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            ev_str = ", ".join([f"{ev.effort} {ev.stat}" for ev in ev_yield])
            logger.info(f"Updated EV yields for '{pokemon_id}': {ev_str}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating EV yield for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_base_happiness(pokemon_id: str, base_happiness: int) -> bool:
        """Update base happiness for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            base_happiness: The new base happiness value (0-255).

        Returns:
            True if the base happiness was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_happiness = pokemon_data.base_happiness

            # Update
            pokemon_data.base_happiness = base_happiness

            # Record change
            BaseService.record_change(
                pokemon_data,
                field="Base Happiness",
                old_value=str(old_happiness),
                new_value=str(base_happiness),
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated base happiness for '{pokemon_id}': {base_happiness}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating base happiness for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_base_experience(pokemon_id: str, base_experience: int) -> bool:
        """Update base experience for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            base_experience: The new base experience value.

        Returns:
            True if the base experience was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_experience = pokemon_data.base_experience

            # Update
            pokemon_data.base_experience = base_experience

            # Record change
            BaseService.record_change(
                pokemon_data,
                field="Base Experience",
                old_value=str(old_experience),
                new_value=str(base_experience),
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated base experience for '{pokemon_id}': {base_experience}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating base experience for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_catch_rate(pokemon_id: str, catch_rate: int) -> bool:
        """Update catch rate for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            catch_rate: The new catch rate value (0-255).

        Returns:
            True if the catch rate was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_catch_rate = pokemon_data.capture_rate

            # Update
            pokemon_data.capture_rate = catch_rate

            # Record change
            BaseService.record_change(
                pokemon_data,
                field="Catch Rate",
                old_value=str(old_catch_rate),
                new_value=str(catch_rate),
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated catch rate for '{pokemon_id}': {catch_rate}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating catch rate for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_gender_ratio(pokemon_id: str, gender_rate: int) -> bool:
        """Update gender ratio for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update.
            gender_rate: The new gender rate value (-1 to 8).
                -1 = genderless
                0 = 100% male
                1-7 = female percentage in eighths (1=12.5%, 4=50%, 7=87.5%)
                8 = 100% female

        Returns:
            True if the gender ratio was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_gender_rate = pokemon_data.gender_rate

            # Update
            pokemon_data.gender_rate = gender_rate

            # Record change
            old_value, new_value = BaseService.format_gender_ratio_change(old_gender_rate, gender_rate)
            BaseService.record_change(
                pokemon_data,
                field="Gender Ratio",
                old_value=old_value,
                new_value=new_value,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated gender ratio for '{pokemon_id}': rate={gender_rate}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating gender ratio for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_single_stat(pokemon_id: str, stat: str, new_value: int) -> bool:
        """Update a single stat for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "pikachu-cosplay").
            stat: The stat slug (e.g., "hp", "attack", "special_attack").
                  Must be one of StatSlug.all() values.
            new_value: The new stat value.

        Returns:
            True if the stat was updated successfully, False otherwise.
        """
        # Validate stat is a known slug
        if stat not in StatSlug.all():
            logger.warning(f"Unknown stat slug '{stat}' for Pokemon '{pokemon_id}'")
            return False

        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # stat slug matches Stats dataclass field name directly
            old_value = getattr(pokemon_data.stats, stat)

            # Skip if value is already the same (idempotency)
            if old_value == new_value:
                return True

            setattr(pokemon_data.stats, stat, new_value)

            # Record change (use slug as field name for consistency)
            BaseService.record_change(
                pokemon_data,
                field=f"Stat: {stat}",
                old_value=str(old_value),
                new_value=str(new_value),
                source="attribute_service",
            )

            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated {stat} for '{pokemon_id}': {old_value} -> {new_value}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating {stat} for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_ability_slot(pokemon_id: str, ability_name: str, slot: int | None = None) -> bool:
        """Update a specific ability slot for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "pikachu-cosplay").
            ability_name: The ability name (slug) to set.
            slot: The slot number (1, 2, or 3) to update, or None to add to next available.

        Returns:
            True if the ability was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            ability_id = name_to_id(ability_name)

            # Check if ability already exists in the same slot (idempotency)
            for ability in pokemon_data.abilities:
                if ability.name == ability_id:
                    if slot is None or ability.slot == slot:
                        return True  # Already exists, no change needed

            # Capture old value for change tracking
            old_value = None

            if slot is not None:
                # Update specific slot
                found = False
                for i, ability in enumerate(pokemon_data.abilities):
                    if ability.slot == slot:
                        if ability.name == ability_id:
                            return True  # Already same ability
                        old_value = ability.name
                        is_hidden = slot == 3
                        pokemon_data.abilities[i] = PokemonAbility(
                            name=ability_id, is_hidden=is_hidden, slot=slot
                        )
                        found = True
                        break

                if not found:
                    # Slot doesn't exist, add it
                    is_hidden = slot == 3
                    pokemon_data.abilities.append(
                        PokemonAbility(name=ability_id, is_hidden=is_hidden, slot=slot)
                    )
            else:
                # No slot specified - find next available slot
                existing_slots = {ability.slot for ability in pokemon_data.abilities}
                next_slot = None
                for s in [1, 2, 3]:
                    if s not in existing_slots:
                        next_slot = s
                        break

                if next_slot is None:
                    # All slots occupied - update slot 3
                    next_slot = 3
                    for i, ability in enumerate(pokemon_data.abilities):
                        if ability.slot == 3:
                            if ability.name == ability_id:
                                return True
                            old_value = ability.name
                            pokemon_data.abilities[i] = PokemonAbility(
                                name=ability_id, is_hidden=True, slot=3
                            )
                            break
                else:
                    is_hidden = next_slot == 3
                    pokemon_data.abilities.append(
                        PokemonAbility(name=ability_id, is_hidden=is_hidden, slot=next_slot)
                    )

            # Record change
            slot_str = f" (slot {slot})" if slot else ""
            BaseService.record_change(
                pokemon_data,
                field=f"Ability{slot_str}",
                old_value=old_value if old_value else "(none)",
                new_value=ability_id,
                source="attribute_service",
            )

            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated ability{slot_str} for '{pokemon_id}': {ability_name}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating ability for Pokemon '{pokemon_id}': {e}")
            return False

    @staticmethod
    def update_growth_rate(pokemon_id: str, growth_rate: str) -> bool:
        """Update growth rate for a Pokemon.

        Args:
            pokemon_id: The ID of the Pokemon to update (e.g., "pikachu", "pikachu-cosplay").
            growth_rate: The new growth rate slug (e.g., "fast", "medium-fast", "slow").

        Returns:
            True if the growth rate was updated successfully, False otherwise.
        """
        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                logger.warning(f"Pokemon '{pokemon_id}' not found in parsed data")
                return False

            # Capture old value for change tracking
            old_growth_rate = pokemon_data.growth_rate

            # Update
            pokemon_data.growth_rate = growth_rate

            # Record change
            BaseService.record_change(
                pokemon_data,
                field="Growth Rate",
                old_value=str(old_growth_rate),
                new_value=growth_rate,
                source="attribute_service",
            )

            # Save using PokeDBLoader
            PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
            logger.info(f"Updated growth rate for '{pokemon_id}': {growth_rate}")
            return True

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating growth rate for Pokemon '{pokemon_id}': {e}")
            return False
