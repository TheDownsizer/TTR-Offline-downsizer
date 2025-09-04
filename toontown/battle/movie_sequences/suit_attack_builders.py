"""
Suit Attack Sequence Builders

Specialized builders for suit attack sequences.
"""

from . import BaseSequenceBuilder, SequencePriority, SequenceConfig
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
from ..SuitBattleGlobals import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import config

# Import existing movie modules
from .. import MovieSuitAttacks

class SuitAttackSequenceBuilder(BaseSequenceBuilder):
    """Builder for Suit Attack sequences"""
    
    def get_sequence_name(self):
        return "SuitAttacks"
    
    def get_priority(self):
        return SequencePriority.SUIT_ATTACKS
    
    def can_handle_attack(self, attack_dict):
        # Suit attacks have different structure than toon attacks
        return 'suit' in attack_dict and 'name' in attack_dict
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        if not attack_dicts:
            return (None, None)
        
        track = self._create_sequence('suit-attacks')
        cam_track = self._create_sequence('suit-attacks-cam')
        
        # Track if local toon becomes sad (dies)
        is_local_toon_sad = False
        
        for attack_dict in attack_dicts:
            ival, cam_ival = MovieSuitAttacks.doSuitAttack(attack_dict)
            if ival:
                track.append(ival)
                cam_track.append(cam_ival)
            
            # Check if local toon dies from this attack
            target_field = attack_dict.get('target')
            if target_field is None:
                continue
            
            if attack_dict['group'] == ATK_TGT_GROUP:
                # Group attack - check all targets
                for target in target_field:
                    if (target['died'] and 
                        hasattr(base, 'localAvatar') and 
                        target['toon'].doId == base.localAvatar.doId):
                        is_local_toon_sad = True
            elif attack_dict['group'] == ATK_TGT_SINGLE:
                # Single attack - check single target
                if (target_field['died'] and 
                    hasattr(base, 'localAvatar') and 
                    target_field['toon'].doId == base.localAvatar.doId):
                    is_local_toon_sad = True
            
            # Break if local toon becomes sad
            if is_local_toon_sad:
                break
        
        if len(track) == 0:
            return (None, None)
        
        return (track, cam_track)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_SUIT_ATTACKS, 1).getValue()

class CustomSuitAttackBuilder(BaseSequenceBuilder):
    """Extensible builder for custom suit attacks"""
    
    def __init__(self, movie, attack_name, movie_function, priority=None):
        super().__init__(movie)
        self.attack_name = attack_name
        self.movie_function = movie_function
        self.custom_priority = priority or SequencePriority.SUIT_ATTACKS
    
    def get_sequence_name(self):
        return f"Custom{self.attack_name}"
    
    def get_priority(self):
        return self.custom_priority
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('name') == self.attack_name
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        filtered_attacks = []
        for attack in attack_dicts:
            if self.can_handle_attack(attack):
                filtered_attacks.append(attack)
        
        if not filtered_attacks:
            return (None, None)
        
        return self.movie_function(filtered_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_SUIT_ATTACKS, 1).getValue()

class GroupSuitAttackBuilder(BaseSequenceBuilder):
    """Builder specifically for group suit attacks"""
    
    def get_sequence_name(self):
        return "GroupSuitAttacks"
    
    def get_priority(self):
        return SequencePriority.SUIT_ATTACKS - 10  # Slightly higher priority
    
    def can_handle_attack(self, attack_dict):
        return (attack_dict.get('group') == ATK_TGT_GROUP and 
                'suit' in attack_dict)
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        group_attacks = []
        for attack in attack_dicts:
            if self.can_handle_attack(attack):
                group_attacks.append(attack)
        
        if not group_attacks:
            return (None, None)
        
        # Use standard suit attack builder but only for group attacks
        track = self._create_sequence('group-suit-attacks')
        cam_track = self._create_sequence('group-suit-attacks-cam')
        
        for attack_dict in group_attacks:
            ival, cam_ival = MovieSuitAttacks.doSuitAttack(attack_dict)
            if ival:
                track.append(ival)
                cam_track.append(cam_ival)
        
        return (track, cam_track) if len(track) > 0 else (None, None)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_SUIT_ATTACKS, 1).getValue()

class SingleSuitAttackBuilder(BaseSequenceBuilder):
    """Builder specifically for single-target suit attacks"""
    
    def get_sequence_name(self):
        return "SingleSuitAttacks"
    
    def get_priority(self):
        return SequencePriority.SUIT_ATTACKS + 10  # Slightly lower priority
    
    def can_handle_attack(self, attack_dict):
        return (attack_dict.get('group') == ATK_TGT_SINGLE and 
                'suit' in attack_dict)
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        single_attacks = []
        for attack in attack_dicts:
            if self.can_handle_attack(attack):
                single_attacks.append(attack)
        
        if not single_attacks:
            return (None, None)
        
        # Use standard suit attack builder but only for single attacks
        track = self._create_sequence('single-suit-attacks')
        cam_track = self._create_sequence('single-suit-attacks-cam')
        
        for attack_dict in single_attacks:
            ival, cam_ival = MovieSuitAttacks.doSuitAttack(attack_dict)
            if ival:
                track.append(ival)
                cam_track.append(cam_ival)
        
        return (track, cam_track) if len(track) > 0 else (None, None)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_SUIT_ATTACKS, 1).getValue()