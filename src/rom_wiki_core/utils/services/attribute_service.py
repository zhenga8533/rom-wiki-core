"""
Service for updating Pokemon attributes (stats, type, abilities, EVs, etc.).
"""

import re

from rom_wiki_core.utils.core.loader import PokeDBLoader
from rom_wiki_core.utils.core.logger import get_logger
from rom_wiki_core.utils.data.constants import StatSlug, normalize_stat
from rom_wiki_core.utils.data.models import Pokemon
from rom_wiki_core.utils.services.base_service import BaseService
from rom_wiki_core.utils.text.text_util import name_to_id, parse_pokemon_forme

logger = get_logger(__name__)


class AttributeService(BaseService):
    """Service for updating Pokemon attributes in parsed data folder."""

    @staticmethod
    def update_attribute(pokemon: str, attribute: str, value: str, forme: str = "") -> bool:
        """Update an attribute of an existing Pokemon in the parsed data folder.

        Args:
            pokemon (str): The name of the Pokemon to update.
            attribute (str): The attribute to update (e.g., "Base Stats", "Type", "Base Stats (Plant Forme)").
            value (str): The new value for the attribute.
            forme (str, optional): The forme of the Pokemon (e.g., "attack", "defense"). Defaults to "".
                                   If the attribute name contains a forme specification, that takes precedence.

        Returns:
            bool: True if the attribute was updated successfully, False otherwise.
        """
        # Extract forme from attribute name if present
        # Patterns:
        #   - "Base Stats (Plant Forme)" -> forme="plant"
        #   - "Ability (Complete / Sandy Forme)" -> forme="sandy"
        forme_from_attr = ""
        if " Forme)" in attribute:
            # Match pattern: "(Something Forme)" or "(Complete / Something Forme)"
            forme_match = re.search(r"(?:/\s*)?([A-Za-z\s]+)\s+Forme\)", attribute)
            if forme_match:
                forme_name = forme_match.group(1).strip()
                # Parse the forme name to handle complex cases
                _, forme_from_attr = parse_pokemon_forme(f"{pokemon} {forme_name}")

        # Use forme from attribute if present, otherwise use the passed forme parameter
        if forme_from_attr:
            forme = forme_from_attr

        # Normalize pokemon name and append forme if present
        pokemon_id = name_to_id(pokemon)
        if forme:
            pokemon_id = f"{pokemon_id}-{forme}"

        # Determine if we should process this attribute
        # Patterns:
        #   - "(Complete / Classic)": Same for both versions, process it
        #   - "(Complete)": Complete only, process it
        #   - "(Classic)": Classic only, skip it
        if "Complete" in attribute:
            # Complete version only, process it
            pass
        elif "Classic" in attribute:
            # Classic only, skip it
            logger.debug(f"Skipping Classic-only attribute '{attribute}' for '{pokemon}'")
            return False

        # Extract the base attribute name (remove version markers and forme markers)
        attribute_base = attribute.split(" (")[0].strip()

        try:
            # Load the Pokemon using PokeDBLoader
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                forme_str = f" ({forme} forme)" if forme else ""
                logger.warning(
                    f"Pokemon '{pokemon}'{forme_str} not found in parsed data (ID: {pokemon_id})"
                )
                return False

            # Route to appropriate handler based on attribute
            if attribute_base == "Base Stats":
                return AttributeService._update_base_stats(pokemon_id, pokemon_data, value)
            elif attribute_base == "Type":
                return AttributeService._update_type(pokemon_id, pokemon_data, value)
            elif attribute_base == "Ability":
                return AttributeService._update_ability(pokemon_id, pokemon_data, value)
            elif attribute_base == "EVs":
                return AttributeService._update_evs(pokemon_id, pokemon_data, value)
            elif attribute_base == "Base Happiness":
                return AttributeService._update_base_happiness(pokemon_id, pokemon_data, value)
            elif attribute_base == "Base Experience":
                return AttributeService._update_base_experience(pokemon_id, pokemon_data, value)
            elif attribute_base == "Catch Rate":
                return AttributeService._update_catch_rate(pokemon_id, pokemon_data, value)
            elif attribute_base == "Gender Ratio":
                return AttributeService._update_gender_ratio(pokemon_id, pokemon_data, value)
            else:
                logger.debug(f"Attribute '{attribute_base}' not yet implemented for '{pokemon}'")
                return False

        except (OSError, IOError, ValueError) as e:
            logger.warning(f"Error updating {attribute_base} of Pokemon '{pokemon}': {e}")
            return False

    @staticmethod
    def _update_base_stats(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update base stats for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new base stats string (e.g., "80 HP / 82 Atk / 83 Def / 100 SAtk / 100 SDef / 80 Spd / 525 BST").

        Returns:
            bool: True if the base stats were updated successfully, False otherwise.
        """
        # Parse: "80 HP / 82 Atk / 83 Def / 100 SAtk / 100 SDef / 80 Spd / 525 BST"
        parts = value.split(" / ")
        if len(parts) != 7:
            logger.warning(f"Invalid base stats format: {value}")
            return False

        try:
            hp = int(parts[0].split()[0])
            attack = int(parts[1].split()[0])
            defense = int(parts[2].split()[0])
            sp_attack = int(parts[3].split()[0])
            sp_defense = int(parts[4].split()[0])
            speed = int(parts[5].split()[0])

            # Capture old value for change tracking
            old_value, _ = BaseService.format_stat_change(pokemon_data.stats, None)

            # Update stats object
            pokemon_data.stats.hp = hp
            pokemon_data.stats.attack = attack
            pokemon_data.stats.defense = defense
            pokemon_data.stats.special_attack = sp_attack
            pokemon_data.stats.special_defense = sp_defense
            pokemon_data.stats.speed = speed

            # Record change
            _, new_value = BaseService.format_stat_change(None, pokemon_data.stats)
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
                f"{hp}/{attack}/{defense}/{sp_attack}/{sp_defense}/{speed}"
            )
            return True

        except (ValueError, IndexError) as e:
            logger.warning(f"Error parsing base stats '{value}': {e}")
            return False

    @staticmethod
    def _update_type(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update type for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new type string (e.g., "Fire / Dragon" or "Fire").

        Returns:
            bool: True if the type was updated successfully, False otherwise.
        """
        # Parse: "Fire / Dragon" or "Fire"
        types = [name_to_id(t.strip()) for t in value.split(" / ")]

        # Capture old value for change tracking
        old_types = pokemon_data.types.copy()

        # Update types list (single or dual)
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

    @staticmethod
    def _update_ability(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update abilities for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new ability string (e.g., "Overgrow / Overgrow / Chlorophyll").

        Returns:
            bool: True if the abilities were updated successfully, False otherwise.
        """
        # Parse: "ability1 / ability2 / hidden_ability" (1-3 abilities accepted)
        abilities = [name_to_id(a.strip()) for a in value.split(" / ")]

        if len(abilities) < 1 or len(abilities) > 3:
            logger.warning(f"Invalid ability format (expected 1-3 abilities): {value}")
            return False

        # Capture old value for change tracking
        # Handle both dict and object formats
        old_abilities = []
        for a in pokemon_data.abilities:
            if isinstance(a, dict):
                old_abilities.append(a)
            else:
                old_abilities.append({"name": a.name, "is_hidden": a.is_hidden, "slot": a.slot})

        # Build new abilities list
        # Structure: [{"name": str, "is_hidden": bool, "slot": int}]
        new_abilities = []

        for i, ability in enumerate(abilities):
            if ability == "-" or not ability:
                continue

            # Validate ability exists in database
            ability_data = PokeDBLoader.load_ability(ability)
            if not ability_data:
                logger.warning(
                    f"Ability '{ability}' not found in database. Skipping validation but saving anyway."
                )

            # Only the 3rd ability is hidden (when there are 3 abilities)
            is_hidden = (i == 2 and len(abilities) == 3)
            new_abilities.append({"name": ability, "is_hidden": is_hidden, "slot": i + 1})

        # Update abilities
        pokemon_data.abilities = new_abilities

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
        ability_str = " / ".join(abilities)
        logger.info(f"Updated abilities for '{pokemon_id}': {ability_str}")
        return True

    @staticmethod
    def _update_evs(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update EV yields for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new EV yield string (e.g., "2 Atk" or "1 SAtk, 1 Spd").

        Returns:
            bool: True if the EV yields were updated successfully, False otherwise.
        """
        # Parse: "2 Atk" or "1 SAtk, 1 Spd"
        # Mapping from canonical slug to kebab-case (EVYield model format)
        slug_to_kebab = {
            StatSlug.HP: "hp",
            StatSlug.ATTACK: "attack",
            StatSlug.DEFENSE: "defense",
            StatSlug.SPECIAL_ATTACK: "special-attack",
            StatSlug.SPECIAL_DEFENSE: "special-defense",
            StatSlug.SPEED: "speed",
        }

        ev_yields = []
        parts = [p.strip() for p in value.split(",")]

        for part in parts:
            tokens = part.split()
            if len(tokens) != 2:
                logger.warning(f"Invalid EV yield format: {part}")
                return False

            effort = int(tokens[0])
            stat_short = tokens[1]

            # Normalize to canonical slug, then convert to kebab-case for EVYield model
            stat_slug = normalize_stat(stat_short)
            if stat_slug is None:
                logger.warning(f"Unknown stat abbreviation: {stat_short}")
                return False

            ev_yields.append({"stat": slug_to_kebab[stat_slug], "effort": effort})

        # Capture old value for change tracking
        # Handle both dict and object formats
        old_ev_yield = []
        for ev in pokemon_data.ev_yield:
            if isinstance(ev, dict):
                old_ev_yield.append(ev)
            else:
                old_ev_yield.append({"stat": ev.stat, "effort": ev.effort})

        # Update EV yield
        pokemon_data.ev_yield = ev_yields

        # Record change
        old_value, new_value = BaseService.format_ev_yield_change(old_ev_yield, ev_yields)
        BaseService.record_change(
            pokemon_data,
            field="EV Yield",
            old_value=old_value,
            new_value=new_value,
            source="attribute_service",
        )

        # Save using PokeDBLoader
        PokeDBLoader.save_pokemon(pokemon_id, pokemon_data)
        logger.info(f"Updated EV yields for '{pokemon_id}': {value}")
        return True

    @staticmethod
    def _update_base_happiness(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update base happiness for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new base happiness string (e.g., "70").

        Returns:
            bool: True if the base happiness was updated successfully, False otherwise.
        """
        try:
            base_happiness = int(value.strip())

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

        except ValueError as e:
            logger.warning(f"Error parsing base happiness '{value}': {e}")
            return False

    @staticmethod
    def _update_base_experience(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update base experience for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new base experience string (e.g., "142").

        Returns:
            bool: True if the base experience was updated successfully, False otherwise.
        """
        try:
            base_experience = int(value.strip())

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

        except ValueError as e:
            logger.warning(f"Error parsing base experience '{value}': {e}")
            return False

    @staticmethod
    def _update_catch_rate(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update catch rate for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new catch rate string (e.g., "45").

        Returns:
            bool: True if the catch rate was updated successfully, False otherwise.
        """
        try:
            catch_rate = int(value.strip())

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

        except ValueError as e:
            logger.warning(f"Error parsing catch rate '{value}': {e}")
            return False

    @staticmethod
    def update_single_stat(pokemon: str, stat: str, new_value: int, forme: str = "") -> bool:
        """Update a single stat for a Pokemon.

        Args:
            pokemon (str): The name of the Pokemon to update.
            stat (str): The stat slug (e.g., "hp", "attack", "special_attack").
                       Use normalize_stat() to convert display names to slugs.
            new_value (int): The new stat value.
            forme (str, optional): The forme of the Pokemon. Defaults to "".

        Returns:
            bool: True if the stat was updated successfully, False otherwise.
        """
        # Validate stat is a known slug
        if stat not in StatSlug.all():
            logger.warning(f"Unknown stat slug '{stat}' for Pokemon '{pokemon}'")
            return False

        # Normalize pokemon name and append forme if present
        pokemon_id = name_to_id(pokemon)
        if forme:
            pokemon_id = f"{pokemon_id}-{forme}"

        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                forme_str = f" ({forme} forme)" if forme else ""
                logger.warning(f"Pokemon '{pokemon}'{forme_str} not found in parsed data")
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
            logger.warning(f"Error updating {stat} for Pokemon '{pokemon}': {e}")
            return False

    @staticmethod
    def update_ability_slot(pokemon: str, ability_name: str, slot: int | None = None, forme: str = "") -> bool:
        """Update a specific ability slot for a Pokemon.

        Args:
            pokemon (str): The name of the Pokemon to update.
            ability_name (str): The ability name to set.
            slot (int | None): The slot number (1, 2, or 3) to update, or None to add.
            forme (str, optional): The forme of the Pokemon. Defaults to "".

        Returns:
            bool: True if the ability was updated successfully, False otherwise.
        """
        from rom_wiki_core.utils.data.models import PokemonAbility

        # Normalize pokemon name and append forme if present
        pokemon_id = name_to_id(pokemon)
        if forme:
            pokemon_id = f"{pokemon_id}-{forme}"

        try:
            pokemon_data = PokeDBLoader.load_pokemon(pokemon_id)
            if pokemon_data is None:
                forme_str = f" ({forme} forme)" if forme else ""
                logger.warning(f"Pokemon '{pokemon}'{forme_str} not found in parsed data")
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
            logger.warning(f"Error updating ability for Pokemon '{pokemon}': {e}")
            return False

    @staticmethod
    def _update_gender_ratio(pokemon_id: str, pokemon_data: Pokemon, value: str) -> bool:
        """Update gender ratio for a Pokemon.

        Args:
            pokemon_id (str): The ID of the Pokemon to update.
            pokemon_data (Pokemon): The Pokemon dataclass object.
            value (str): The new gender ratio string (e.g., "87.5% Male, 12.5% Female").

        Returns:
            bool: True if the gender ratio was updated successfully, False otherwise.
        """
        value_lower = value.lower()

        if "genderless" in value_lower or "no gender" in value_lower:
            gender_rate = -1
        elif "100% male" in value_lower:
            gender_rate = 0
        elif "100% female" in value_lower:
            gender_rate = 8
        else:
            # Extract female percentage
            match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*female", value_lower)
            if not match:
                logger.warning(f"Could not parse gender ratio: {value}")
                return False

            female_percent = float(match.group(1))

            # Map to gender_rate (eighths)
            gender_rate_map = {
                0.0: 0,
                12.5: 1,
                25.0: 2,
                37.5: 3,
                50.0: 4,
                62.5: 5,
                75.0: 6,
                87.5: 7,
                100.0: 8,
            }

            if female_percent not in gender_rate_map:
                logger.warning(f"Unsupported gender ratio: {female_percent}% female")
                return False

            gender_rate = gender_rate_map[female_percent]

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
        logger.info(f"Updated gender ratio for '{pokemon_id}': {value} (rate={gender_rate})")
        return True
