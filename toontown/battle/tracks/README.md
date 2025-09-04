# Modular Gag Track Calculation System

This document describes the refactored gag track calculation system for Toontown battle mechanics.

## Overview

The original `BattleCalculatorAI.py` contained a monolithic approach to calculating toon attacks, with all gag track logic embedded in large methods. This has been refactored into a modular system where each gag track has its own dedicated calculator class.

## Architecture

### Base Class
- **`BaseTrackCalculator`** (`tracks/__init__.py`): Abstract base class that all track calculators inherit from
  - Provides common helper methods and interfaces
  - Ensures consistent API across all track calculators

### Track Calculators
Each gag track has its own specialized calculator:

- **`HealTrackCalculator`** (`tracks/heal.py`): Handles Toon-Up gags
- **`TrapTrackCalculator`** (`tracks/trap.py`): Handles trap placement and activation
- **`LureTrackCalculator`** (`tracks/lure.py`): Handles lure mechanics and trap interactions
- **`SoundTrackCalculator`** (`tracks/sound.py`): Handles sound attacks and unluring
- **`ThrowTrackCalculator`** (`tracks/throw.py`): Handles throw attacks and knockback
- **`SquirtTrackCalculator`** (`tracks/squirt.py`): Handles squirt attacks and knockback
- **`DropTrackCalculator`** (`tracks/drop.py`): Handles drop attacks and lure interactions
- **`SpecialTrackCalculator`** (`tracks/special.py`): Handles FIRE, PETSOS, and NPCSOS attacks

### Manager
- **`TrackCalculatorManager`** (`tracks/manager.py`): Coordinates all track calculators
  - Routes attacks to appropriate track calculators
  - Provides unified interface for the battle system
  - Handles error recovery and fallbacks

## Key Methods

Each track calculator implements:
- `calculate_hit(attack_index, attack_targets)`: Determines if the attack hits
- `calculate_damage(attack_index, attack_targets)`: Calculates damage and effects
- `get_track_name()`: Returns track name for debugging

The manager provides:
- `calculate_toon_attack_hit()`: Routes hit calculation to appropriate calculator
- `calculate_toon_attack_damage()`: Routes damage calculation to appropriate calculator
- `is_knockback_attack()`: Checks if attack causes knockback
- `is_unlure_attack()`: Checks if attack breaks lure
- `create_toon_target_list()`: Creates target list based on track type

## Integration

The `BattleCalculatorAI` class has been updated to use the new system:
- Initializes `TrackCalculatorManager` in constructor
- Replaces monolithic methods with calls to track manager
- Maintains fallback logic for error handling
- Preserves all existing functionality

## Benefits

1. **Modularity**: Each track is self-contained and easier to understand
2. **Maintainability**: Changes to one track don't affect others
3. **Extensibility**: New tracks can be added easily
4. **Testability**: Individual tracks can be tested in isolation
5. **Debugging**: Track-specific issues are easier to locate
6. **Code Reuse**: Common functionality is shared through base class

## Backward Compatibility

The refactoring maintains full backward compatibility:
- All existing battle mechanics work unchanged
- No changes to external interfaces
- All configuration flags and settings preserved
- Error handling provides fallbacks to original logic

## Future Enhancements

The modular architecture enables:
- Track-specific optimizations
- Custom track behaviors for events
- A/B testing of different track mechanics
- Easier balance adjustments
- Plugin-like track extensions

## Example Usage

```python
# Initialize the system (done automatically in BattleCalculatorAI.__init__)
track_manager = TrackCalculatorManager(battle_calculator)

# Calculate if a throw attack hits
hit_success, accuracy = track_manager.calculate_toon_attack_hit(attack_index, targets)

# Calculate damage for the attack
track_manager.calculate_toon_attack_damage(attack_index, targets)

# Check attack properties
is_knockback = track_manager.is_knockback_attack(attack_index)
is_unlure = track_manager.is_unlure_attack(attack_index)
```

This modular system provides a solid foundation for future battle system enhancements while maintaining the stability and functionality of the existing code.