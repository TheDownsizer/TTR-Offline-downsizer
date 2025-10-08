"""
Examples and Documentation for the Suit Battle Logic System

This file contains examples of how to create custom battle logic for specific suits.
Use these examples as templates for creating your own suit-specific battle mechanics.
"""

from typing import Dict, List, Any
from .SuitAttacks import SuitBattleLogic

class ExampleOpportunistLogic(SuitBattleLogic):
    """
    Example: Opportunist suit that steals HP from other suits.
    This demonstrates basic suit logic with battle scenes.
    """
    
    def should_activate(self) -> bool:
        # Only activate if this suit is alive and there are other suits to steal from
        return (self.suit.currHP >= 1 and 
                any(other_suit != self.suit and other_suit.currHP > 0 
                    for other_suit in self.battle.activeSuits))
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Find other suits to steal from
        other_suits = [s for s in self.battle.activeSuits 
                      if s != self.suit and s.currHP > 0]
        
        if not other_suits:
            return []
        
        # Pick a random suit to steal from
        import random
        target_suit = random.choice(other_suits)
        damage = target_suit.getHP()
        
        # Kill the target suit and add battle scene
        target_suit.setHP(0)
        self.battle.neededDeadSuits.append(target_suit)
        
        # Return battle scene: [sceneType, suitId, [damage], [targetIds], isToon]
        return [[2, self.suit.doId, [damage], [target_suit.doId], 0]]
    
    def on_round_end(self):
        # Add damage bonus to this suit based on stolen damage
        if hasattr(self, 'stolen_damage'):
            self.suit.damageBonus += self.stolen_damage

class ExampleBossLogic(SuitBattleLogic):
    """
    Example: Boss suit with multiple phases and special abilities.
    This demonstrates complex logic with phases and extra attacks.
    """
    
    def __init__(self, battle_calculator, suit):
        super().__init__(battle_calculator, suit)
        self.phase = 0
        self.phase_threshold = 0.5  # Activate special abilities at 50% HP
        self.rage_mode = False
    
    def should_activate(self) -> bool:
        return self.suit.getHP() <= (self.suit.maxHP * self.phase_threshold)
    
    def get_extra_attacks(self) -> List[Dict[str, Any]]:
        if not self.should_activate():
            return []
        
        # Boss gets extra attacks when below threshold
        extra_attacks = []
        
        # Phase 1: Extra attack
        if self.phase == 0:
            extra_attacks.append({
                'attack_id': 0,  # Use first attack
                'count': 1,
                'multiplier': 1.5
            })
        
        # Phase 2: Multiple attacks with higher damage
        elif self.phase == 1:
            extra_attacks.append({
                'attack_id': 0,
                'count': 2,
                'multiplier': 2.0
            })
        
        return extra_attacks
    
    def on_round_start(self):
        # Check if we should enter a new phase
        if self.should_activate() and self.phase == 0:
            self.phase = 1
            # Could trigger special animations or effects here
            self.notify.debug(f"Boss {self.suit_name} entering phase 2!")
        
        # Enter rage mode at 25% HP
        if self.suit.getHP() <= (self.suit.maxHP * 0.25) and not self.rage_mode:
            self.rage_mode = True
            self.phase = 2
            self.notify.debug(f"Boss {self.suit_name} entering RAGE MODE!")

class ExampleHealerLogic(SuitBattleLogic):
    """
    Example: Healer suit that can heal other suits.
    This demonstrates support abilities and conditional logic.
    """
    
    def should_activate(self) -> bool:
        # Only heal if there are injured suits
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
        
        # Return healing scene: [sceneType, suitId, [heal_amount], [targetIds], isToon]
        return [[4, self.suit.doId, [heal_amount], [target_suit.doId], 0]]

class ExampleTankLogic(SuitBattleLogic):
    """
    Example: Tank suit that can taunt and protect other suits.
    This demonstrates defensive abilities and team mechanics.
    """
    
    def __init__(self, battle_calculator, suit):
        super().__init__(battle_calculator, suit)
        self.taunt_active = False
        self.protection_targets = []
    
    def should_activate(self) -> bool:
        # Activate if there are other suits to protect
        return any(other_suit != self.suit and other_suit.currHP > 0 
                  for other_suit in self.battle.activeSuits)
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Find suits to protect
        other_suits = [s for s in self.battle.activeSuits 
                      if s != self.suit and s.currHP > 0]
        
        if not other_suits:
            return []
        
        # Activate taunt to draw attention
        if not self.taunt_active:
            self.taunt_active = True
            return [[5, self.suit.doId, [0], [], 0]]  # Taunt scene
        
        return []
    
    def on_toon_attack(self, toon_id, attack_data):
        # If taunt is active, redirect some damage to this suit
        if self.taunt_active:
            # Reduce damage to other suits and take it ourselves
            pass

class ExampleSummonerLogic(SuitBattleLogic):
    """
    Example: Summoner suit that can call reinforcements.
    This demonstrates complex mechanics with multiple targets.
    """
    
    def __init__(self, battle_calculator, suit):
        super().__init__(battle_calculator, suit)
        self.summon_cooldown = 0
        self.max_summons = 2
    
    def should_activate(self) -> bool:
        # Can summon if cooldown is ready and we haven't reached max summons
        return (self.summon_cooldown <= 0 and 
                len([s for s in self.battle.activeSuits if s.summoned_by == self.suit.doId]) < self.max_summons)
    
    def get_battle_scenes(self) -> List[List]:
        if not self.should_activate():
            return []
        
        # Create a summoned suit (this would need to be implemented in the battle system)
        # For now, just show the summoning animation
        return [[6, self.suit.doId, [0], [], 0]]  # Summon scene
    
    def on_round_end(self):
        # Reduce summon cooldown
        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1

# Configuration examples
EXAMPLE_SUIT_CONFIGS = {
    'opportunist': {
        'type': 'opportunist',
        'steal_threshold': 0.5,  # Only steal if target has >50% HP
        'steal_amount': 0.75,    # Steal 75% of target's HP
        'cooldown': 3,           # Can only steal every 3 rounds
    },
    'boss': {
        'type': 'boss',
        'phase_threshold': 0.3,  # Enter phase 2 at 30% HP
        'rage_threshold': 0.1,   # Enter rage mode at 10% HP
        'extra_attacks': 2,
        'damage_multiplier': 1.5,
    },
    'healer': {
        'type': 'healer',
        'heal_amount': 20,
        'heal_threshold': 0.8,   # Only heal if target <80% HP
        'heal_cooldown': 2,      # Can only heal every 2 rounds
    },
    'tank': {
        'type': 'tank',
        'taunt_duration': 3,     # Taunt lasts 3 rounds
        'damage_redirection': 0.5, # Redirect 50% of damage
    },
    'summoner': {
        'type': 'summoner',
        'max_summons': 2,
        'summon_cooldown': 3,
        'summoned_suit_type': 'basic',
    }
}

# Usage example
def create_custom_suit_logic(suit_name: str, config: Dict) -> type:
    """
    Create a custom suit logic class based on configuration.
    This allows for dynamic creation of suit logic without writing new classes.
    """
    
    class DynamicSuitLogic(SuitBattleLogic):
        def __init__(self, battle_calculator, suit):
            super().__init__(battle_calculator, suit)
            self.config = config
            self.cooldown = 0
        
        def should_activate(self) -> bool:
            if self.config['type'] == 'opportunist':
                return (self.suit.currHP >= 1 and 
                        any(other_suit != self.suit and other_suit.currHP > 0 
                            for other_suit in self.battle.activeSuits) and
                        self.cooldown <= 0)
            elif self.config['type'] == 'healer':
                return (any(suit.getHP() < suit.maxHP and suit != self.suit 
                          for suit in self.battle.activeSuits) and
                        self.cooldown <= 0)
            return True
        
        def get_battle_scenes(self) -> List[List]:
            if not self.should_activate():
                return []
            
            if self.config['type'] == 'opportunist':
                return self._create_opportunist_scene()
            elif self.config['type'] == 'healer':
                return self._create_healer_scene()
            return []
        
        def _create_opportunist_scene(self) -> List[List]:
            other_suits = [s for s in self.battle.activeSuits 
                          if s != self.suit and s.currHP > 0]
            if not other_suits:
                return []
            
            import random
            target_suit = random.choice(other_suits)
            damage = int(target_suit.getHP() * self.config.get('steal_amount', 0.75))
            
            target_suit.setHP(target_suit.getHP() - damage)
            self.cooldown = self.config.get('cooldown', 3)
            
            return [[2, self.suit.doId, [damage], [target_suit.doId], 0]]
        
        def _create_healer_scene(self) -> List[List]:
            injured_suits = [s for s in self.battle.activeSuits 
                            if s.getHP() < s.maxHP and s != self.suit]
            if not injured_suits:
                return []
            
            target_suit = min(injured_suits, key=lambda s: s.getHP())
            heal_amount = min(self.config.get('heal_amount', 20), 
                            target_suit.maxHP - target_suit.getHP())
            
            target_suit.setHP(target_suit.getHP() + heal_amount)
            self.cooldown = self.config.get('heal_cooldown', 2)
            
            return [[4, self.suit.doId, [heal_amount], [target_suit.doId], 0]]
        
        def on_round_end(self):
            if self.cooldown > 0:
                self.cooldown -= 1
    
    return DynamicSuitLogic

# Example of how to register custom logic
def register_custom_suit_logic(suit_name: str, config: Dict):
    """
    Register a custom suit logic for a specific suit.
    """
    from .SuitAttacks import SUIT_LOGIC_REGISTRY
    
    logic_class = create_custom_suit_logic(suit_name, config)
    SUIT_LOGIC_REGISTRY[suit_name] = logic_class

# Example usage:
# register_custom_suit_logic('my_custom_suit', EXAMPLE_SUIT_CONFIGS['opportunist']) 