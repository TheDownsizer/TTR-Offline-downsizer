"""
Modular Movie Sequence Builder System

This module provides a refactored approach to building battle movie sequences,
separating different sequence types into specialized builder classes for better
maintainability, extensibility, and flexibility.
"""

from direct.interval.IntervalGlobal import *
from direct.showbase import DirectObject
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *

class BaseSequenceBuilder(DirectObject.DirectObject):
    """Base class for all movie sequence builders"""
    
    def __init__(self, movie):
        self.movie = movie
        self.battle = movie.battle
        self.notify = movie.notify
    
    def build_sequence(self, attack_dicts):
        """
        Build animation sequence for the given attacks
        Returns: (main_sequence, camera_sequence) or (None, None)
        """
        raise NotImplementedError("Subclasses must implement build_sequence")
    
    def get_sequence_name(self):
        """Return the sequence type name for debugging"""
        raise NotImplementedError("Subclasses must implement get_sequence_name")
    
    def can_handle_attack(self, attack_dict):
        """Check if this builder can handle the given attack"""
        raise NotImplementedError("Subclasses must implement can_handle_attack")
    
    def get_priority(self):
        """Get sequence priority for ordering (lower = earlier)"""
        return 100  # Default priority
    
    # Helper methods available to all builders
    def _create_sequence(self, name):
        """Helper to create a named sequence"""
        return Sequence(name=name)
    
    def _create_parallel(self, name):
        """Helper to create a named parallel interval"""
        return Parallel(name=name)
    
    def _should_skip_sequence(self):
        """Check if sequences should be skipped based on config"""
        return False  # Override in subclasses
    
    def _filter_attacks_by_type(self, attack_dicts, track_type):
        """Filter attacks by track type"""
        filtered = []
        for attack in attack_dicts:
            if attack.get('track') == track_type:
                filtered.append(attack)
        return filtered
    
    def _filter_attacks_by_special(self, attack_dicts, special_key):
        """Filter attacks by special attribute"""
        filtered = []
        for attack in attack_dicts:
            if special_key in attack:
                filtered.append(attack)
        return filtered

class SequenceBuilderError(Exception):
    """Exception raised for sequence builder errors"""
    pass

# Priority constants for sequence ordering
class SequencePriority:
    FIRE = 10
    SOS = 20
    NPCSOS = 30
    PETSOS = 40
    HEAL = 50
    TRAP = 60
    LURE = 70
    SOUND = 80
    THROW = 90
    SQUIRT = 100
    DROP = 110
    SUIT_ATTACKS = 200
    
# Sequence configuration flags
class SequenceConfig:
    WANT_TOON_ATTACKS = 'want-toon-attack-anims'
    WANT_SUIT_ATTACKS = 'want-suit-anims'
    RANDOM_BATTLE_TIMESTAMP = 'random-battle-timestamp'