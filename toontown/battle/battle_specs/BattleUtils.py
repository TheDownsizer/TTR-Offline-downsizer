"""
Battle Utility Functions

This module provides utility functions for battle operations including:
- Healing suits and toons
- Promoting/demoting suits
- Damaging suits and toons
- Status effects and buffs
- Battle scene generation
- Health and level calculations
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import random
import math
from game.toontown.suit import SuitDNA

class BattleUtils:
    """
    Utility class containing battle-related helper functions.
    """
    
    # Constants for battle calculations
    MAX_SUIT_LEVEL = 50
    MAX_TOON_LEVEL = 50
    BASE_HEAL_AMOUNT = 20
    BASE_DAMAGE_MULTIPLIER = 1.0
    PROMOTION_LEVEL_BONUS = 2
    DEMOTION_LEVEL_PENALTY = -1
    
    @staticmethod
    def heal_suit(suit, heal_amount: int, max_heal_percent: float = 1.0) -> Dict[str, Any]:
        """
        Heal a suit by the specified amount.
        
        Args:
            suit: The suit to heal
            heal_amount: Amount of HP to restore
            max_heal_percent: Maximum percentage of max HP that can be healed (0.0-1.0)
            
        Returns:
            Dict containing healing results
        """
        if not suit or suit.currHP <= 0:
            return {
                'success': False,
                'reason': 'Suit is dead or invalid',
                'healed_amount': 0,
                'new_hp': 0
            }
        
        current_hp = suit.getHP()
        max_hp = suit.maxHP
        max_healable = int(max_hp * max_heal_percent)
        
        # Calculate actual heal amount
        actual_heal = min(heal_amount, max_healable - current_hp)
        
        if actual_heal <= 0:
            return {
                'success': False,
                'reason': 'Suit is at max HP or heal amount is 0',
                'healed_amount': 0,
                'new_hp': current_hp
            }
        
        # Apply healing
        new_hp = min(current_hp + actual_heal, max_healable)
        suit.setHP(new_hp)
        
        return {
            'success': True,
            'healed_amount': actual_heal,
            'new_hp': new_hp,
            'max_hp': max_hp,
            'heal_percentage': actual_heal / max_hp
        }
    
    @staticmethod
    def heal_toon(toon, heal_amount: int, max_heal_percent: float = 1.0) -> Dict[str, Any]:
        """
        Heal a toon by the specified amount.
        
        Args:
            toon: The toon to heal
            heal_amount: Amount of HP to restore
            max_heal_percent: Maximum percentage of max HP that can be healed (0.0-1.0)
            
        Returns:
            Dict containing healing results
        """
        if not toon or toon.hp <= 0:
            return {
                'success': False,
                'reason': 'Toon is dead or invalid',
                'healed_amount': 0,
                'new_hp': 0
            }
        
        current_hp = toon.hp
        max_hp = toon.maxHp
        max_healable = int(max_hp * max_heal_percent)
        
        # Calculate actual heal amount
        actual_heal = min(heal_amount, max_healable - current_hp)
        
        if actual_heal <= 0:
            return {
                'success': False,
                'reason': 'Toon is at max HP or heal amount is 0',
                'healed_amount': 0,
                'new_hp': current_hp
            }
        
        # Apply healing
        new_hp = min(current_hp + actual_heal, max_healable)
        toon.hp = new_hp
        
        return {
            'success': True,
            'healed_amount': actual_heal,
            'new_hp': new_hp,
            'max_hp': max_hp,
            'heal_percentage': actual_heal / max_hp
        }
    
    @staticmethod
    def promote_suit(suit, level_bonus: int = None) -> Dict[str, Any]:
        """
        Promote a suit by increasing its level and recalculating stats.
        
        Args:
            suit: The suit to promote
            level_bonus: Amount to increase level by (defaults to PROMOTION_LEVEL_BONUS)
            
        Returns:
            Dict containing promotion results
        """
        if not suit:
            return {
                'success': False,
                'reason': 'Suit is invalid',
                'old_level': 0,
                'new_level': 0
            }
        
        if level_bonus is None:
            level_bonus = BattleUtils.PROMOTION_LEVEL_BONUS
        
        old_level = suit.getActualLevel()
        new_level = min(old_level + level_bonus, BattleUtils.MAX_SUIT_LEVEL)
        
        if new_level <= old_level:
            return {
                'success': False,
                'reason': 'Suit is already at max level',
                'old_level': old_level,
                'new_level': new_level
            }
        
        # Update suit level and stats
        suit.level = new_level
        old_max_hp = suit.maxHP
        suit.maxHP = (new_level + 1) * (new_level + 2)
        
        # Adjust current HP proportionally
        if old_max_hp > 0:
            hp_ratio = suit.getHP() / old_max_hp
            new_hp = int(suit.maxHP * hp_ratio)
            suit.setHP(new_hp)
        else:
            suit.setHP(suit.maxHP)  # Full HP for new suits
        
        return {
            'success': True,
            'old_level': old_level,
            'new_level': new_level,
            'old_max_hp': old_max_hp,
            'new_max_hp': suit.maxHP,
            'current_hp': suit.getHP()
        }
    
    @staticmethod
    def demote_suit(suit, level_penalty: int = None) -> Dict[str, Any]:
        """
        Demote a suit by decreasing its level and recalculating stats.
        
        Args:
            suit: The suit to demote
            level_penalty: Amount to decrease level by (defaults to DEMOTION_LEVEL_PENALTY)
            
        Returns:
            Dict containing demotion results
        """
        if not suit:
            return {
                'success': False,
                'reason': 'Suit is invalid',
                'old_level': 0,
                'new_level': 0
            }
        
        if level_penalty is None:
            level_penalty = BattleUtils.DEMOTION_LEVEL_PENALTY
        
        old_level = suit.getActualLevel()
        new_level = max(old_level + level_penalty, 1)  # Minimum level 1
        
        if new_level >= old_level:
            return {
                'success': False,
                'reason': 'Suit cannot be demoted further',
                'old_level': old_level,
                'new_level': new_level
            }
        
        # Update suit level and stats
        suit.level = new_level
        old_max_hp = suit.maxHP
        suit.maxHP = (new_level + 1) * (new_level + 2)
        
        # Adjust current HP proportionally
        if old_max_hp > 0:
            hp_ratio = suit.getHP() / old_max_hp
            new_hp = int(suit.maxHP * hp_ratio)
            suit.setHP(new_hp)
        else:
            suit.setHP(suit.maxHP)
        
        return {
            'success': True,
            'old_level': old_level,
            'new_level': new_level,
            'old_max_hp': old_max_hp,
            'new_max_hp': suit.maxHP,
            'current_hp': suit.getHP()
        }
    
    @staticmethod
    def damage_suit(suit, damage_amount: int, damage_type: str = 'normal') -> Dict[str, Any]:
        """
        Damage a suit by the specified amount.
        
        Args:
            suit: The suit to damage
            damage_amount: Amount of damage to deal
            damage_type: Type of damage ('normal', 'critical', 'piercing')
            
        Returns:
            Dict containing damage results
        """
        if not suit or suit.currHP <= 0:
            return {
                'success': False,
                'reason': 'Suit is already dead or invalid',
                'damage_dealt': 0,
                'new_hp': 0
            }
        
        current_hp = suit.getHP()
        
        # Apply damage type modifiers
        if damage_type == 'critical':
            damage_amount = int(damage_amount * 1.5)
        elif damage_type == 'piercing':
            # Piercing damage ignores some defenses
            damage_amount = int(damage_amount * 1.2)
        
        # Calculate actual damage
        actual_damage = min(damage_amount, current_hp)
        new_hp = max(0, current_hp - actual_damage)
        
        # Apply damage
        suit.setHP(new_hp)
        
        # Check if suit died
        is_dead = new_hp <= 0
        
        return {
            'success': True,
            'damage_dealt': actual_damage,
            'new_hp': new_hp,
            'is_dead': is_dead,
            'damage_type': damage_type
        }
    
    @staticmethod
    def damage_toon(toon, damage_amount: int, damage_type: str = 'normal') -> Dict[str, Any]:
        """
        Damage a toon by the specified amount.
        
        Args:
            toon: The toon to damage
            damage_amount: Amount of damage to deal
            damage_type: Type of damage ('normal', 'critical', 'piercing')
            
        Returns:
            Dict containing damage results
        """
        if not toon or toon.hp <= 0:
            return {
                'success': False,
                'reason': 'Toon is already dead or invalid',
                'damage_dealt': 0,
                'new_hp': 0
            }
        
        current_hp = toon.hp
        
        # Apply damage type modifiers
        if damage_type == 'critical':
            damage_amount = int(damage_amount * 1.5)
        elif damage_type == 'piercing':
            damage_amount = int(damage_amount * 1.2)
        
        # Calculate actual damage
        actual_damage = min(damage_amount, current_hp)
        new_hp = max(0, current_hp - actual_damage)
        
        # Apply damage
        toon.hp = new_hp
        
        # Check if toon died
        is_dead = new_hp <= 0
        
        return {
            'success': True,
            'damage_dealt': actual_damage,
            'new_hp': new_hp,
            'is_dead': is_dead,
            'damage_type': damage_type
        }
    
    @staticmethod
    def steal_hp_from_suit(source_suit, target_suit, steal_percentage: float = 0.5) -> Dict[str, Any]:
        """
        Steal HP from one suit and give it to another.
        
        Args:
            source_suit: The suit that will receive the stolen HP
            target_suit: The suit to steal HP from
            steal_percentage: Percentage of target's HP to steal (0.0-1.0)
            
        Returns:
            Dict containing steal results
        """
        if not source_suit or not target_suit:
            return {
                'success': False,
                'reason': 'Invalid suits provided',
                'stolen_amount': 0
            }
        
        if target_suit.currHP <= 0:
            return {
                'success': False,
                'reason': 'Target suit is dead',
                'stolen_amount': 0
            }
        
        target_hp = target_suit.getHP()
        steal_amount = int(target_hp * steal_percentage)
        
        if steal_amount <= 0:
            return {
                'success': False,
                'reason': 'No HP to steal',
                'stolen_amount': 0
            }
        
        # Steal HP from target
        new_target_hp = max(0, target_hp - steal_amount)
        target_suit.setHP(new_target_hp)
        
        # Give HP to source
        source_hp = source_suit.getHP()
        source_max_hp = source_suit.maxHP
        new_source_hp = min(source_hp + steal_amount, source_max_hp)
        source_suit.setHP(new_source_hp)
        
        return {
            'success': True,
            'stolen_amount': steal_amount,
            'target_old_hp': target_hp,
            'target_new_hp': new_target_hp,
            'source_old_hp': source_hp,
            'source_new_hp': new_source_hp
        }
    
    @staticmethod
    def apply_status_effect(entity, effect_type: str, duration: int = 1, magnitude: float = 1.0) -> Dict[str, Any]:
        """
        Apply a status effect to an entity (suit or toon).
        
        Args:
            entity: The entity to apply the effect to
            effect_type: Type of effect ('poison', 'stun', 'slow', 'haste', 'shield')
            duration: Number of rounds the effect lasts
            magnitude: Strength of the effect (0.0-2.0)
            
        Returns:
            Dict containing status effect results
        """
        if not entity:
            return {
                'success': False,
                'reason': 'Invalid entity provided',
                'effect_type': effect_type
            }
        
        # Initialize status effects if not present
        if not hasattr(entity, 'status_effects'):
            entity.status_effects = {}
        
        # Apply the effect
        entity.status_effects[effect_type] = {
            'duration': duration,
            'magnitude': magnitude,
            'rounds_remaining': duration
        }
        
        return {
            'success': True,
            'effect_type': effect_type,
            'duration': duration,
            'magnitude': magnitude
        }
    
    @staticmethod
    def remove_status_effect(entity, effect_type: str) -> Dict[str, Any]:
        """
        Remove a status effect from an entity.
        
        Args:
            entity: The entity to remove the effect from
            effect_type: Type of effect to remove
            
        Returns:
            Dict containing removal results
        """
        if not entity or not hasattr(entity, 'status_effects'):
            return {
                'success': False,
                'reason': 'Entity has no status effects',
                'effect_type': effect_type
            }
        
        if effect_type not in entity.status_effects:
            return {
                'success': False,
                'reason': f'Effect {effect_type} not found on entity',
                'effect_type': effect_type
            }
        
        removed_effect = entity.status_effects.pop(effect_type)
        
        return {
            'success': True,
            'effect_type': effect_type,
            'removed_effect': removed_effect
        }
    
    @staticmethod
    def update_status_effects(entity) -> List[Dict[str, Any]]:
        """
        Update status effects on an entity (decrease duration, apply effects).
        
        Args:
            entity: The entity to update effects for
            
        Returns:
            List of expired effects
        """
        if not entity or not hasattr(entity, 'status_effects'):
            return []
        
        expired_effects = []
        effects_to_remove = []
        
        for effect_type, effect_data in entity.status_effects.items():
            # Decrease duration
            effect_data['rounds_remaining'] -= 1
            
            # Apply effect based on type
            if effect_type == 'poison':
                damage = int(5 * effect_data['magnitude'])
                BattleUtils.damage_entity(entity, damage, 'poison')
            elif effect_type == 'stun':
                # Stun prevents actions
                pass
            elif effect_type == 'slow':
                # Slow reduces speed
                pass
            elif effect_type == 'haste':
                # Haste increases speed
                pass
            elif effect_type == 'shield':
                # Shield reduces damage
                pass
            
            # Check if effect expired
            if effect_data['rounds_remaining'] <= 0:
                expired_effects.append({
                    'effect_type': effect_type,
                    'effect_data': effect_data
                })
                effects_to_remove.append(effect_type)
        
        # Remove expired effects
        for effect_type in effects_to_remove:
            entity.status_effects.pop(effect_type)
        
        return expired_effects
    
    @staticmethod
    def damage_entity(entity, damage_amount: int, damage_type: str = 'normal') -> Dict[str, Any]:
        """
        Generic damage function that works with both suits and toons.
        
        Args:
            entity: The entity to damage (suit or toon)
            damage_amount: Amount of damage to deal
            damage_type: Type of damage
            
        Returns:
            Dict containing damage results
        """
        # Check if entity is a suit or toon
        if hasattr(entity, 'currHP'):  # Suit
            return BattleUtils.damage_suit(entity, damage_amount, damage_type)
        elif hasattr(entity, 'hp'):  # Toon
            return BattleUtils.damage_toon(entity, damage_amount, damage_type)
        else:
            return {
                'success': False,
                'reason': 'Unknown entity type',
                'damage_dealt': 0
            }
    
    @staticmethod
    def heal_entity(entity, heal_amount: int, max_heal_percent: float = 1.0) -> Dict[str, Any]:
        """
        Generic heal function that works with both suits and toons.
        
        Args:
            entity: The entity to heal (suit or toon)
            heal_amount: Amount of HP to restore
            max_heal_percent: Maximum percentage of max HP that can be healed
            
        Returns:
            Dict containing healing results
        """
        # Check if entity is a suit or toon
        if hasattr(entity, 'currHP'):  # Suit
            return BattleUtils.heal_suit(entity, heal_amount, max_heal_percent)
        elif hasattr(entity, 'hp'):  # Toon
            return BattleUtils.heal_toon(entity, heal_amount, max_heal_percent)
        else:
            return {
                'success': False,
                'reason': 'Unknown entity type',
                'healed_amount': 0
            }
    
    @staticmethod
    def create_battle_scene(scene_type: int, source_id: int, values: List, targets: List, 
                           duration: int = 0) -> List:
        """
        Create a battle scene for special effects.
        
        Args:
            scene_type: Type of scene (1=damage, 2=heal, 3=promote, 4=status)
            source_id: ID of the source entity
            values: List of values for the scene
            targets: List of target entity IDs
            duration: Duration of the scene
            
        Returns:
            Battle scene list
        """
        return [scene_type, source_id, values, targets, duration]
    
    @staticmethod
    def calculate_damage_multiplier(attacker_level: int, defender_level: int, 
                                  base_multiplier: float = 1.0) -> float:
        """
        Calculate damage multiplier based on level difference.
        
        Args:
            attacker_level: Level of the attacker
            defender_level: Level of the defender
            base_multiplier: Base damage multiplier
            
        Returns:
            Calculated damage multiplier
        """
        level_diff = attacker_level - defender_level
        
        # Level advantage/disadvantage multiplier
        if level_diff > 0:
            level_multiplier = 1.0 + (level_diff * 0.1)
        else:
            level_multiplier = 1.0 + (level_diff * 0.05)
        
        return base_multiplier * level_multiplier
    
    @staticmethod
    def get_random_target(targets: List, exclude: List = None) -> Any:
        """
        Get a random target from a list, optionally excluding certain targets.
        
        Args:
            targets: List of possible targets
            exclude: List of targets to exclude
            
        Returns:
            Randomly selected target or None
        """
        if not targets:
            return None
        
        if exclude:
            available_targets = [t for t in targets if t not in exclude]
        else:
            available_targets = targets
        
        if not available_targets:
            return None
        
        return random.choice(available_targets)
    
    @staticmethod
    def get_weakest_target(targets: List) -> Any:
        """
        Get the weakest target (lowest HP) from a list.
        
        Args:
            targets: List of possible targets
            
        Returns:
            Weakest target or None
        """
        if not targets:
            return None
        
        return min(targets, key=lambda t: t.getHP() if hasattr(t, 'getHP') else t.hp)
    
    @staticmethod
    def get_strongest_target(targets: List) -> Any:
        """
        Get the strongest target (highest HP) from a list.
        
        Args:
            targets: List of possible targets
            
        Returns:
            Strongest target or None
        """
        if not targets:
            return None
        
        return max(targets, key=lambda t: t.getHP() if hasattr(t, 'getHP') else t.hp)

# Convenience functions for easier access
def heal_suit(suit, heal_amount: int, max_heal_percent: float = 1.0) -> Dict[str, Any]:
    """Convenience function for healing suits."""
    return BattleUtils.heal_suit(suit, heal_amount, max_heal_percent)

def heal_toon(toon, heal_amount: int, max_heal_percent: float = 1.0) -> Dict[str, Any]:
    """Convenience function for healing toons."""
    return BattleUtils.heal_toon(toon, heal_amount, max_heal_percent)

def promote_suit(suit, level_bonus: int = None) -> Dict[str, Any]:
    """Convenience function for promoting suits."""
    return BattleUtils.promote_suit(suit, level_bonus)

def demote_suit(suit, level_penalty: int = None) -> Dict[str, Any]:
    """Convenience function for demoting suits."""
    return BattleUtils.demote_suit(suit, level_penalty)

def damage_suit(suit, damage_amount: int, damage_type: str = 'normal') -> Dict[str, Any]:
    """Convenience function for damaging suits."""
    return BattleUtils.damage_suit(suit, damage_amount, damage_type)

def damage_toon(toon, damage_amount: int, damage_type: str = 'normal') -> Dict[str, Any]:
    """Convenience function for damaging toons."""
    return BattleUtils.damage_toon(toon, damage_amount, damage_type)

def steal_hp_from_suit(source_suit, target_suit, steal_percentage: float = 0.5) -> Dict[str, Any]:
    """Convenience function for stealing HP between suits."""
    return BattleUtils.steal_hp_from_suit(source_suit, target_suit, steal_percentage)

def apply_status_effect(entity, effect_type: str, duration: int = 1, magnitude: float = 1.0) -> Dict[str, Any]:
    """Convenience function for applying status effects."""
    return BattleUtils.apply_status_effect(entity, effect_type, duration, magnitude)

def remove_status_effect(entity, effect_type: str) -> Dict[str, Any]:
    """Convenience function for removing status effects."""
    return BattleUtils.remove_status_effect(entity, effect_type)

def update_status_effects(entity) -> List[Dict[str, Any]]:
    """Convenience function for updating status effects."""
    return BattleUtils.update_status_effects(entity) 