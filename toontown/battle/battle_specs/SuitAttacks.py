"""
Battle Logic System for Specific Suits

This module provides a comprehensive system for defining custom battle logic
for specific suits. It includes support for:
- Custom attacks with multipliers and counts
- Special battle scenes
- Suit-specific abilities and mechanics
- Conditional logic based on battle state
"""

from typing import Dict, List, Any, Optional, Callable
from game.toontown.suit import SuitDNA

# Base configuration for suit attacks
SUIT_ATTACKS = {
    'op': {  # TTC Miniboss
        0: {'count': 2, 'multiplier': 1.0},
    },
    # Add more suits and their custom attacks as needed
}

# Base configuration for battle scenes
SUIT_BATTLE_SCENES = {
    # Add more suits and their custom battle scenes as needed
}

class SuitBattleLogic:
    """
    Base class for defining custom battle logic for specific suits.
    Inherit from this class to create suit-specific battle mechanics.
    """
    
    def __init__(self, battle_calculator, suit):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.suit = suit
        self.suit_name = suit.dna.name
        self.suit_level = suit.getLevel()
        
    def should_activate(self) -> bool:
        """
        Check if this suit's special logic should activate.
        Override in subclasses.
        """
        return True
    
    def get_extra_attacks(self) -> List[Dict[str, Any]]:
        """
        Return list of extra attacks this suit should perform.
        Override in subclasses.
        """
        return []
    
    def get_battle_scenes(self) -> List[List]:
        """
        Return list of battle scenes this suit should trigger.
        Override in subclasses.
        """
        return []
    
    def on_round_start(self):
        """
        Called at the start of each round.
        Override in subclasses.
        """
        pass
    
    def on_round_end(self):
        """
        Called at the end of each round.
        Override in subclasses.
        """
        pass
    
    def on_suit_turn(self):
        """
        Called when it's this suit's turn to attack.
        Override in subclasses.
        """
        pass
    
    def on_toon_attack(self, toon_id, attack_data):
        """
        Called when a toon attacks this suit.
        Override in subclasses.
        """
        pass

class OpportunistLogic(SuitBattleLogic):
    """
    Logic for Opportunist suit - they can steal HP from other suits.
    """
    
    def should_activate(self) -> bool:
        return (self.suit.currHP >= 1 and 
                any(other_suit != self.suit and other_suit.currHP > 0 
                    for other_suit in self.battle.activeSuits))
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Find other suits to steal from
        other_suits = [s for s in self.battle.activeSuits 
                      if s != self.suit and s not in self.battle.neededDeadSuits]
        
        if not other_suits:
            return []
        
        # Pick a random suit to steal from
        import random
        target_suit = random.choice(other_suits)
        self.stolen_damage = target_suit.getActualLevel()
        damage = target_suit.getHP()
        
        # Kill the target suit and add battle scene
        target_suit.setHP(0)
        self.battle.neededDeadSuits.append(target_suit)
        
        return [[2, self.suit.doId, [damage], [target_suit.doId], 0]]
    
    def on_round_end(self):
        # Add damage bonus to this suit
        if hasattr(self, 'stolen_damage'):
            self.suit.damageBonus += self.stolen_damage

class EmployerLogic(SuitBattleLogic):
    """
    Logic for Employer suits - they can buff other suits.
    """
    
    def should_activate(self) -> bool:
        return (self.suit.cogPosition == 1 and 
                self.suit_name not in SuitDNA.SuitConfig.EMPLOYER_TYPES and
                any(other_suit != self.suit and other_suit.currHP > 0 
                    for other_suit in self.battle.activeSuits))
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Find other suits to buff
        other_suits = [s for s in self.battle.activeSuits 
                      if s != self.suit and s.currHP > 0]
        
        if not other_suits:
            return []
        
        # Pick a random suit to buff
        import random
        target_suit = random.choice(other_suits)
        level_bonus = 2
        
        # Buff the target suit
        target_suit.level += level_bonus
        target_suit.maxHP = (target_suit.getActualLevel() + 1) * (target_suit.getActualLevel() + 2)
        target_suit.setHP((target_suit.getActualLevel() + 1) * (target_suit.getActualLevel() + 2))
        
        return [[3, self.suit.doId, [level_bonus], [target_suit.doId], 0]]

class BossLogic(SuitBattleLogic):
    """
    Logic for Boss suits - they have special abilities.
    """
    
    def __init__(self, battle_calculator, suit):
        super().__init__(battle_calculator, suit)
        self.phase = 0
        self.phase_threshold = 0.5  # Activate special abilities at 50% HP
    
    def should_activate(self) -> bool:
        return self.suit.getHP() <= (self.suit.maxHP * self.phase_threshold)
    
    def get_extra_attacks(self) -> List[Dict[str, Any]]:
        if not self.should_activate():
            return []
        
        # Boss gets extra attacks when below threshold
        return [{
            'attack_id': 0,  # Use first attack
            'count': 2,
            'multiplier': 1.5
        }]
    
    def on_round_start(self):
        # Check if we should enter a new phase
        if self.should_activate() and self.phase == 0:
            self.phase = 1
            # Could trigger special animations or effects here

class HealerLogic(SuitBattleLogic):
    """
    Logic for Healer suits - they can heal other suits.
    """
    
    def should_activate(self) -> bool:
        return any(suit.getHP() < suit.maxHP and suit != self.suit 
                  for suit in self.battle.activeSuits)
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Find suits to heal
        injured_suits = [s for s in self.battle.activeSuits 
                        if s.getHP() < s.maxHP and s != self.suit]
        
        if not injured_suits:
            return []
        
        # Heal the most injured suit
        target_suit = min(injured_suits, key=lambda s: s.getHP())
        heal_amount = min(20, target_suit.maxHP - target_suit.getHP())
        
        target_suit.setHP(target_suit.getHP() + heal_amount)
        
        return [[4, self.suit.doId, [heal_amount], [target_suit.doId], 0]]

# Registry of suit logic classes
SUIT_LOGIC_REGISTRY = {
    'op': OpportunistLogic,
    'employer': EmployerLogic,
    'boss': BossLogic,
    'healer': HealerLogic,
}

def get_suit_logic_class(suit_name: str) -> Optional[type]:
    """
    Get the appropriate logic class for a suit.
    """
    # Map suit names to logic types
    suit_logic_mapping = {
        'op': 'op',  # Opportunist
        'ceo': 'boss',  # CEO (example)
        'healer': 'healer',  # Healer suits (example)
    }
    
    logic_type = suit_logic_mapping.get(suit_name)
    if logic_type:
        return SUIT_LOGIC_REGISTRY.get(logic_type)
    
    return None

def create_suit_logic(battle_calculator, suit) -> Optional[SuitBattleLogic]:
    """
    Create a battle logic instance for a suit.
    """
    
    if suit.cogPosition == 1 and suit.dna.name not in SuitDNA.SuitConfig.EMPLOYER_TYPES:
        logic_class = SUIT_LOGIC_REGISTRY.get('employer')
        return logic_class(battle_calculator, suit)
    else:
        logic_class = get_suit_logic_class(suit.dna.name)
        if logic_class:
            return logic_class(battle_calculator, suit)
    return None

# Legacy support functions
def get_suit_attacks(suit_name: str) -> Dict:
    """Get custom attacks for a suit (legacy support)."""
    return SUIT_ATTACKS.get(suit_name, {})

def get_suit_battle_scenes(suit_name: str) -> Dict:
    """Get custom battle scenes for a suit (legacy support)."""
    return SUIT_BATTLE_SCENES.get(suit_name, {})

# Example usage and configuration
EXAMPLE_CONFIG = {
    'suit_logic': {
        'op': {
            'type': 'opportunist',
            'steal_threshold': 0.5,  # Only steal if target has >50% HP
            'steal_amount': 0.75,    # Steal 75% of target's HP
        },
        'boss': {
            'type': 'boss',
            'phase_threshold': 0.3,  # Enter phase 2 at 30% HP
            'extra_attacks': 2,
            'damage_multiplier': 1.5,
        },
        'healer': {
            'type': 'healer',
            'heal_amount': 20,
            'heal_threshold': 0.8,   # Only heal if target <80% HP
        }
    }
}