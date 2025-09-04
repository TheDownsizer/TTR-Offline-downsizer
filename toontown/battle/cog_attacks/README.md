# Modular Cog Attack Calculation System

This document describes the refactored cog attack calculation system for Toontown battle mechanics.

## Overview

The original `BattleCalculatorAI.py` contained a monolithic approach to calculating cog attacks, with all attack logic embedded in large methods. This has been refactored into a modular system where different attack types have their own dedicated calculator classes.

## Architecture

### Base Class
- **`BaseCogAttackCalculator`** (`cog_attacks/__init__.py`): Abstract base class that all cog attack calculators inherit from
  - Provides common helper methods and interfaces
  - Ensures consistent API across all attack calculators

### Attack Calculators
Each attack type has its own specialized calculator:

- **`SingleTargetAttackCalculator`** (`cog_attacks/single_target.py`): Handles single-target cog attacks
- **`GroupTargetAttackCalculator`** (`cog_attacks/group_target.py`): Handles group-target cog attacks
- **`SpecialAttackCalculator`** (`cog_attacks/special.py`): Handles special effect attacks and future extensions

### Manager
- **`CogAttackCalculatorManager`** (`cog_attacks/manager.py`): Coordinates all attack calculators
  - Routes attacks to appropriate attack calculators
  - Provides unified interface for the battle system
  - Handles error recovery and fallbacks

## Key Methods

Each attack calculator implements:
- `calculate_attack_type(attack_index)`: Determines which attack type to use
- `calculate_target(attack_index)`: Determines target(s) for the attack
- `calculate_hit(attack_index)`: Determines if the attack hits
- `calculate_damage(attack_index)`: Calculates damage and effects
- `affects_group(attack)`: Checks if attack affects group or single target
- `create_target_list(attack_index)`: Creates list of targets for the attack
- `get_attack_name()`: Returns attack type name for debugging

The manager provides:
- `calculate_suit_attack_type()`: Routes attack type calculation to appropriate calculator
- `calculate_suit_target()`: Routes target calculation to appropriate calculator
- `suit_attack_hits()`: Routes hit calculation to appropriate calculator
- `calculate_suit_attack_damage()`: Routes damage calculation to appropriate calculator
- `suit_attack_affects_group()`: Checks if attack affects group
- `create_suit_target_list()`: Creates target list based on attack type
- `apply_suit_attack_damages()`: Applies calculated damage to toons
- `calculate_full_suit_attacks()`: Orchestrates full attack calculation cycle

## Attack Types

### Single Target Attacks
- Target one specific toon
- Use revenge targeting (75% chance to target toons who attacked this cog)
- Fallback to random targeting if no revenge target available
- Examples: Most basic cog attacks like "Pound Key", "Fountain Pen", "Audit"

### Group Target Attacks
- Affect all active toons simultaneously
- Single accuracy roll affects all targets
- Damage is applied to every toon in battle
- Examples: "Beguile", "Shake", "Tremor", "Synergy"

### Special Attacks
- Reserved for future attacks with unique mechanics
- Can have custom targeting, accuracy, or damage rules
- Extensible for new attack types or special effects
- Examples: Future status effects, conditional attacks, unique mechanics

## Integration

The `BattleCalculatorAI` class has been updated to use the new system:
- Initializes `CogAttackCalculatorManager` in constructor
- Replaces monolithic methods with calls to attack manager
- Maintains fallback logic for error handling
- Preserves all existing functionality

## Attack Flow

1. **Attack Type Selection**: Manager determines which attack the cog should use
2. **Target Selection**: Calculator determines target(s) based on attack type
3. **Hit Calculation**: Calculator determines if attack hits target(s)
4. **Damage Calculation**: Calculator calculates damage for each target
5. **Damage Application**: Manager applies damage to affected toons
6. **Statistics Update**: Manager updates attack statistics

## Target Selection Logic

### Revenge Targeting (75% chance)
1. Check if cog has been attacked by toons this battle
2. Calculate damage weights for each attacking toon
3. Use weighted random selection to pick target
4. Prefer toons who dealt more damage to this cog

### Random Targeting (25% chance or fallback)
1. Collect all alive toons
2. Randomly select from available targets
3. Used when no revenge targets available

## Configuration Support

The system respects all existing configuration flags:
- `suits-always-hit`: Forces all attacks to hit
- `suits-always-miss`: Forces most attacks to miss (25% still hit)
- `immortal-suits`: Affects damage calculations
- `attack-type`: Can force specific attack types for testing

## Benefits

1. **Modularity**: Each attack type is self-contained and easier to understand
2. **Maintainability**: Changes to one attack type don't affect others
3. **Extensibility**: New attack types can be added easily
4. **Testability**: Individual attack types can be tested in isolation
5. **Debugging**: Attack-specific issues are easier to locate
6. **Code Reuse**: Common functionality is shared through base class
7. **Performance**: More efficient targeting and calculation logic

## Backward Compatibility

The refactoring maintains full backward compatibility:
- All existing battle mechanics work unchanged
- No changes to external interfaces
- All configuration flags and settings preserved
- Error handling provides fallbacks to original logic
- Attack statistics and damage calculations unchanged

## Error Handling

The modular system includes comprehensive error handling:
- Try-catch blocks around all manager calls
- Fallback to original calculation methods on errors
- Detailed error logging for debugging
- Graceful degradation without breaking battles

## Future Enhancements

The modular architecture enables:
- Attack-specific optimizations and effects
- Custom attack behaviors for special events
- A/B testing of different attack mechanics
- Easier balance adjustments per attack type
- Plugin-like attack extensions
- Status effects and special mechanics
- Dynamic attack behavior modifications

## Performance Considerations

- Minimal overhead compared to original system
- Efficient target selection algorithms
- Reduced code duplication
- Optimized group attack handling
- Smart fallback mechanisms

## Attack Data Structure

Cog attacks use the same data structure as before:
```python
attack = [
    SUIT_ID_COL,     # ID of attacking suit
    SUIT_ATK_COL,    # Attack type index
    SUIT_TGT_COL,    # Target index (for single attacks)
    SUIT_HP_COL,     # Damage array for each toon
    # ... other columns
]
```

## Integration with SuitBattleGlobals

The system seamlessly integrates with existing attack definitions:
- `SuitAttacks` dictionary defines attack animations and targeting
- `SuitAttributes` contains cog-specific attack lists
- `ATK_TGT_SINGLE` and `ATK_TGT_GROUP` constants determine targeting
- `getSuitAttack()` function provides attack properties

## Example Usage

```python
# Initialize the system (done automatically in BattleCalculatorAI.__init__)
cog_attack_manager = CogAttackCalculatorManager(battle_calculator)

# Calculate attack type for suit at index 0
attack_type = cog_attack_manager.calculate_suit_attack_type(0)

# Calculate target for the attack
target = cog_attack_manager.calculate_suit_target(0)

# Calculate if attack hits
hits = cog_attack_manager.suit_attack_hits(0)

# Calculate and apply damage
cog_attack_manager.calculate_suit_attack_damage(0)
cog_attack_manager.apply_suit_attack_damages(0)

# Or calculate all attacks for the round
cog_attack_manager.calculate_full_suit_attacks()
```

This modular system provides a solid foundation for future cog attack enhancements while maintaining the stability and functionality of the existing battle system.