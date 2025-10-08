# Suit Battle Logic System

This system provides a modular and extensible way to add custom battle logic for specific suits in Toontown Online+. Instead of hardcoding battle mechanics, you can now create reusable logic classes that define how specific suits behave in battle.

## Overview

The battle logic system consists of:

1. **SuitBattleLogic** - Base class for all suit logic
2. **Logic Classes** - Specific implementations for different suit types
3. **Registry System** - Maps suit names to their logic classes
4. **Integration** - Seamless integration with the existing battle system

## Key Features

- **Modular Design**: Each suit type has its own logic class
- **Conditional Activation**: Logic only activates when conditions are met
- **Battle Scenes**: Support for custom battle animations and effects
- **Extra Attacks**: Suits can perform additional attacks beyond normal
- **Round Events**: Logic can respond to round start/end events
- **Configuration**: Easy to configure and modify suit behavior

## Basic Usage

### Creating a Simple Logic Class

```python
from game.toontown.battle.battle_specs.SuitAttacks import SuitBattleLogic

class MyCustomSuitLogic(SuitBattleLogic):
    def should_activate(self) -> bool:
        # Define when this logic should activate
        return self.suit.currHP >= 1
    
    def get_battle_scenes(self) -> List[List]:
        # Return custom battle scenes
        return [[2, self.suit.doId, [10], [target_id], 0]]
    
    def get_extra_attacks(self) -> List[Dict[str, Any]]:
        # Return extra attacks this suit should perform
        return [{
            'attack_id': 0,
            'count': 1,
            'multiplier': 1.5
        }]
```

### Registering Your Logic

```python
from game.toontown.battle.battle_specs.SuitAttacks import SUIT_LOGIC_REGISTRY

# Register your logic class
SUIT_LOGIC_REGISTRY['my_suit_name'] = MyCustomSuitLogic
```

## Built-in Logic Types

### Opportunist Logic
Suits that can steal HP from other suits.

**Features:**
- Steals HP from other suits
- Kills target suit and gains damage bonus
- Configurable steal amount and cooldown

**Example:**
```python
class OpportunistLogic(SuitBattleLogic):
    def should_activate(self) -> bool:
        return (self.suit.currHP >= 1 and 
                any(other_suit != self.suit and other_suit.currHP > 0 
                    for other_suit in self.battle.activeSuits))
    
    def get_battle_scenes(self) -> List[List]:
        # Find target suit and steal its HP
        target_suit = random.choice([s for s in self.battle.activeSuits 
                                   if s != self.suit and s.currHP > 0])
        damage = target_suit.getHP()
        target_suit.setHP(0)
        return [[2, self.suit.doId, [damage], [target_suit.doId], 0]]
```

### Boss Logic
Suits with multiple phases and special abilities.

**Features:**
- Multiple phases based on HP thresholds
- Extra attacks in later phases
- Rage mode at low HP
- Configurable phase thresholds

**Example:**
```python
class BossLogic(SuitBattleLogic):
    def __init__(self, battle_calculator, suit):
        super().__init__(battle_calculator, suit)
        self.phase = 0
        self.phase_threshold = 0.5
    
    def should_activate(self) -> bool:
        return self.suit.getHP() <= (self.suit.maxHP * self.phase_threshold)
    
    def get_extra_attacks(self) -> List[Dict[str, Any]]:
        if self.phase == 1:
            return [{'attack_id': 0, 'count': 2, 'multiplier': 2.0}]
        return []
```

### Healer Logic
Suits that can heal other suits.

**Features:**
- Heals injured suits
- Prioritizes most injured suits
- Configurable heal amount and cooldown

**Example:**
```python
class HealerLogic(SuitBattleLogic):
    def should_activate(self) -> bool:
        return any(suit.getHP() < suit.maxHP and suit != self.suit 
                  for suit in self.battle.activeSuits)
    
    def get_battle_scenes(self) -> List[List]:
        injured_suits = [s for s in self.battle.activeSuits 
                        if s.getHP() < s.maxHP and s != self.suit]
        target_suit = min(injured_suits, key=lambda s: s.getHP())
        heal_amount = min(20, target_suit.maxHP - target_suit.getHP())
        target_suit.setHP(target_suit.getHP() + heal_amount)
        return [[4, self.suit.doId, [heal_amount], [target_suit.doId], 0]]
```

## Advanced Features

### Round Events

Logic classes can respond to round events:

```python
def on_round_start(self):
    # Called at the start of each round
    pass

def on_round_end(self):
    # Called at the end of each round
    pass

def on_suit_turn(self):
    # Called when it's this suit's turn to attack
    pass

def on_toon_attack(self, toon_id, attack_data):
    # Called when a toon attacks this suit
    pass
```

### Configuration System

You can create dynamic logic classes based on configuration:

```python
def create_custom_suit_logic(suit_name: str, config: Dict) -> type:
    class DynamicSuitLogic(SuitBattleLogic):
        def __init__(self, battle_calculator, suit):
            super().__init__(battle_calculator, suit)
            self.config = config
        
        def should_activate(self) -> bool:
            # Use configuration to determine activation
            return self.config.get('enabled', True)
        
        def get_battle_scenes(self) -> List[List]:
            # Use configuration for behavior
            damage = self.config.get('damage', 10)
            return [[2, self.suit.doId, [damage], [target_id], 0]]
    
    return DynamicSuitLogic
```

### Battle Scene Types

Different scene types for different effects:

- `2` - Damage scene (suit damages target)
- `3` - Buff scene (suit buffs target)
- `4` - Heal scene (suit heals target)
- `5` - Taunt scene (suit taunts)
- `6` - Summon scene (suit summons reinforcements)

## Integration with Existing System

The new system integrates seamlessly with the existing battle system:

1. **Automatic Detection**: Suits are automatically checked for custom logic
2. **Backward Compatibility**: Existing battle mechanics continue to work
3. **Performance**: Logic only runs when needed
4. **Debugging**: Full debug support for troubleshooting

## Migration from Old System

If you have existing hardcoded battle logic, you can migrate it:

### Before (Hardcoded):
```python
if suit.dna.name == 'op':
    if suit.currHP >= 1:
        # Hardcoded logic here
        pass
```

### After (Modular):
```python
# Logic is automatically handled by the system
# Just register your logic class
SUIT_LOGIC_REGISTRY['op'] = OpportunistLogic
```

## Best Practices

1. **Keep Logic Simple**: Each logic class should handle one specific behavior
2. **Use Configuration**: Make values configurable rather than hardcoded
3. **Test Thoroughly**: Test your logic with different battle scenarios
4. **Document Behavior**: Add clear comments explaining what your logic does
5. **Handle Edge Cases**: Consider what happens when conditions aren't met

## Troubleshooting

### Common Issues

1. **Logic not activating**: Check `should_activate()` method
2. **No battle scenes**: Ensure `get_battle_scenes()` returns valid scenes
3. **Performance issues**: Make sure logic doesn't run unnecessarily
4. **Integration problems**: Verify suit names match registry entries

### Debug Tips

- Use `self.notify.debug()` to log important events
- Check battle state in `should_activate()` method
- Verify suit properties are accessible
- Test with different suit combinations

## Examples

See `SuitLogicExamples.py` for comprehensive examples of different logic types and advanced usage patterns.

## Contributing

When adding new suit logic:

1. Create a new logic class inheriting from `SuitBattleLogic`
2. Implement required methods (`should_activate`, `get_battle_scenes`, etc.)
3. Register your logic in the `SUIT_LOGIC_REGISTRY`
4. Add tests and documentation
5. Update this README if adding new features

This system provides a powerful and flexible foundation for creating complex battle mechanics while maintaining code organization and reusability. 