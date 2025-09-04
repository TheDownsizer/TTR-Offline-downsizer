# Modular Movie Sequence System

## Overview

The Modular Movie Sequence System is a complete refactoring of how battle animations (sequences/movies) are built in Toontown Rewritten. This system replaces the hardcoded sequence building in `Movie.py` with a flexible, extensible, and maintainable modular architecture.

## Architecture

### Core Components

1. **BaseSequenceBuilder** (`__init__.py`)
   - Abstract base class for all sequence builders
   - Provides common functionality and interface
   - Defines priority-based ordering system

2. **MovieSequenceManager** (`manager.py`)
   - Central coordinator for all sequence builders
   - Routes attacks to appropriate builders
   - Manages builder registration and lifecycle

3. **Specialized Builders** (`toon_attack_builders.py`, `suit_attack_builders.py`)
   - Individual builders for each attack type
   - Encapsulates attack-specific logic
   - Maintains backward compatibility with existing movie modules

4. **Main Integration** (`Movie.py`)
   - Refactored to use the new modular system
   - Maintains fallback to original system for safety
   - Error handling and graceful degradation

## Benefits

### Flexibility
- Easy to add new attack types without modifying core logic
- Configurable priority system for sequence ordering
- Runtime builder registration and management

### Maintainability
- Separation of concerns - each builder handles one attack type
- Clear interfaces and responsibilities
- Reduced code duplication

### Extensibility
- Custom builders can be registered at runtime
- Plugin-like architecture for extending functionality
- Backward compatible with existing systems

### Error Handling
- Robust fallback mechanism to original system
- Individual builder failures don't crash entire sequence
- Comprehensive logging and debugging support

## Usage

### Basic Usage

The system is automatically initialized in `Movie.__init__()`:

```python
# Initialize the new modular movie sequence system
self.sequence_manager = MovieSequenceManager(self)
```

The `Movie.play()` method uses the new system with automatic fallback:

```python
def play(self, ts, callback):
    try:
        # Use the new sequence manager to build the complete movie
        self.track = self.sequence_manager.build_complete_movie_sequence(
            self.toonAttackDicts, 
            self.suitAttackDicts, 
            callback
        )
        self.track.start(ts)
    except Exception as e:
        # Fallback to original system
        self._play_fallback(ts, callback)
```

### Adding Custom Builders

```python
# Create a custom builder
class CustomLaserAttackBuilder(BaseSequenceBuilder):
    def get_sequence_name(self):
        return "LaserAttack"
    
    def get_priority(self):
        return SequencePriority.THROW + 5  # Custom priority
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == CUSTOM_LASER
    
    def build_sequence(self, attack_dicts):
        # Custom implementation
        return custom_laser_sequence(attack_dicts)

# Register the builder
movie.sequence_manager.register_custom_builder(CustomLaserAttackBuilder(movie))
```

### Builder Management

```python
# Get builder information
builders = movie.sequence_manager.get_all_builders()
print(f"Toon builders: {len(builders['toon_builders'])}")
print(f"Suit builders: {len(builders['suit_builders'])}")
print(f"Custom builders: {len(builders['custom_builders'])}")

# Enable/disable specific builders
movie.sequence_manager.enable_builder('Fire', False)  # Disable fire attacks
movie.sequence_manager.enable_builder('Sound', True)  # Enable sound attacks

# Check builder status
is_enabled = movie.sequence_manager.is_builder_enabled('Heal')
```

## File Structure

```
toontown/battle/movie_sequences/
├── __init__.py                # Base classes and interfaces
├── manager.py                 # MovieSequenceManager
├── toon_attack_builders.py    # Toon attack sequence builders
├── suit_attack_builders.py    # Suit attack sequence builders
└── README.md                  # This documentation
```

## Builder Types

### Toon Attack Builders

| Builder | Track | Priority | Description |
|---------|-------|----------|-------------|
| FireSequenceBuilder | FIRE | 10 | Fire attack sequences |
| SOSSequenceBuilder | SOS | 20 | SOS card sequences |
| NPCSOSSequenceBuilder | NPCSOS | 30 | NPC SOS sequences |
| PetSOSSequenceBuilder | PETSOS | 40 | Pet SOS sequences |
| HealSequenceBuilder | HEAL | 50 | Heal attack sequences |
| TrapSequenceBuilder | TRAP | 60 | Trap attack sequences |
| LureSequenceBuilder | LURE | 70 | Lure attack sequences |
| SoundSequenceBuilder | SOUND | 80 | Sound attack sequences |
| ThrowSequenceBuilder | THROW | 90 | Throw attack sequences |
| SquirtSequenceBuilder | SQUIRT | 100 | Squirt attack sequences |
| DropSequenceBuilder | DROP | 110 | Drop attack sequences |

### Suit Attack Builders

| Builder | Priority | Description |
|---------|----------|-------------|
| SuitAttackSequenceBuilder | 200 | General suit attack sequences |
| GroupSuitAttackBuilder | 190 | Group-targeting suit attacks |
| SingleSuitAttackBuilder | 210 | Single-targeting suit attacks |

## Configuration

### Sequence Configuration

Sequence building can be controlled via configuration variables:

```python
# Configuration flags in SequenceConfig class
WANT_TOON_ATTACKS = 'want-toon-attack-anims'
WANT_SUIT_ATTACKS = 'want-suit-anims'
WANT_HEAL_BONUS = 'want-heal-bonus'
WANT_TRAP_SORTING = 'want-trap-sorting'
```

### Priority System

Builders are executed in priority order (lowest first):
- Lower numbers = higher priority
- Toon attacks: 10-110
- Suit attacks: 190-210
- Custom attacks: user-defined

## Error Handling

### Fallback Mechanism

If the new system encounters any error, it automatically falls back to the original system:

```python
except Exception as e:
    self.notify.warning(f'Error in new sequence system: {e}')
    # Fallback to original system
    self._play_fallback(ts, callback)
```

### Individual Builder Failures

If a specific builder fails, the system continues with other builders:

```python
except Exception as e:
    self.notify.warning(f'Error in {builder.get_sequence_name()} builder: {e}')
    # Continue with other builders
    continue
```

## Performance Considerations

### Lazy Loading
- Builders are only initialized when needed
- Movie modules are imported on-demand
- Minimal performance impact when disabled

### Memory Management
- Proper cleanup in Movie.cleanup()
- DelayDelete integration for safe object lifecycle
- No memory leaks from builder registration

### Backward Compatibility
- Original system remains intact as fallback
- No changes to existing attack data structures
- Seamless integration with existing battle system

## Development Guidelines

### Creating New Builders

1. Inherit from `BaseSequenceBuilder`
2. Implement required methods:
   - `get_sequence_name()`
   - `get_priority()`
   - `can_handle_attack()`
   - `build_sequence()`

3. Follow naming conventions:
   - Class: `{AttackType}SequenceBuilder`
   - File: descriptive module name
   - Priority: logical ordering

### Testing

1. Test individual builders in isolation
2. Test builder registration/unregistration
3. Test fallback mechanism
4. Test with various attack combinations
5. Validate memory cleanup

### Documentation

1. Document new attack types
2. Update priority documentation
3. Add usage examples
4. Document configuration options

## Migration Guide

### From Original System

The new system is designed to be a drop-in replacement:

1. No changes required to existing code
2. Attack data structures remain the same
3. Movie modules continue to work unchanged
4. Configuration variables are preserved

### Enabling New Features

To use new modular features:

1. Register custom builders
2. Configure builder priorities
3. Enable/disable specific attack types
4. Monitor logs for system behavior

## Troubleshooting

### Common Issues

1. **Builder Not Executed**: Check priority ordering and `can_handle_attack()` logic
2. **Sequence Empty**: Verify attack data structure and filtering logic
3. **Fallback Activated**: Check logs for error messages and fix builder issues
4. **Memory Leaks**: Ensure proper cleanup in custom builders

### Debugging

1. Enable debug logging in Movie notify
2. Check builder registration status
3. Validate attack dictionaries
4. Monitor sequence generation

### Support

For issues with the modular movie sequence system:

1. Check logs for error messages
2. Verify builder implementation
3. Test with fallback system
4. Report bugs with detailed reproduction steps

## Future Enhancements

### Planned Features

1. **Hot Reloading**: Runtime reloading of builder modules
2. **Performance Metrics**: Detailed timing and performance monitoring
3. **Advanced Filtering**: More sophisticated attack filtering options
4. **Configuration UI**: In-game interface for builder management

### Extension Points

1. **Custom Attack Types**: Framework for entirely new attack types
2. **Animation Plugins**: Pluggable animation systems
3. **Effect Builders**: Specialized builders for visual effects
4. **Sequence Optimization**: Automatic sequence optimization

## Conclusion

The Modular Movie Sequence System represents a significant improvement in code organization, maintainability, and extensibility for Toontown Rewritten's battle animation system. It provides a solid foundation for future enhancements while maintaining full backward compatibility and robust error handling.