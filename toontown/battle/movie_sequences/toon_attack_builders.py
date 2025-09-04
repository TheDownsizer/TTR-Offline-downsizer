"""
Toon Attack Sequence Builders

Specialized builders for different types of toon attack sequences.
"""

from . import BaseSequenceBuilder, SequencePriority, SequenceConfig
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import config

# Import existing movie modules
from .. import MovieFire
from .. import MovieSOS
from .. import MovieNPCSOS
from .. import MoviePetSOS
from .. import MovieHeal
from .. import MovieTrap
from .. import MovieLure
from .. import MovieSound
from .. import MovieThrow
from .. import MovieSquirt
from .. import MovieDrop

class FireSequenceBuilder(BaseSequenceBuilder):
    """Builder for Fire attack sequences"""
    
    def get_sequence_name(self):
        return "Fire"
    
    def get_priority(self):
        return SequencePriority.FIRE
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == FIRE
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        fire_attacks = self._filter_attacks_by_type(attack_dicts, FIRE)
        if not fire_attacks:
            return (None, None)
        
        return MovieFire.doFires(fire_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class SOSSequenceBuilder(BaseSequenceBuilder):
    """Builder for SOS attack sequences"""
    
    def get_sequence_name(self):
        return "SOS"
    
    def get_priority(self):
        return SequencePriority.SOS
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == SOS
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        sos_attacks = self._filter_attacks_by_type(attack_dicts, SOS)
        if not sos_attacks:
            return (None, None)
        
        return MovieSOS.doSOSs(sos_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class NPCSOSSequenceBuilder(BaseSequenceBuilder):
    """Builder for NPC SOS attack sequences"""
    
    def get_sequence_name(self):
        return "NPCSOS"
    
    def get_priority(self):
        return SequencePriority.NPCSOS
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == NPCSOS or 'special' in attack_dict
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        # Filter for NPCSOS or special attacks
        npcsos_attacks = []
        for attack in attack_dicts:
            if attack.get('track') == NPCSOS or 'special' in attack:
                npcsos_attacks.append(attack)
        
        if not npcsos_attacks:
            return (None, None)
        
        return MovieNPCSOS.doNPCSOSs(npcsos_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class PetSOSSequenceBuilder(BaseSequenceBuilder):
    """Builder for Pet SOS attack sequences"""
    
    def get_sequence_name(self):
        return "PetSOS"
    
    def get_priority(self):
        return SequencePriority.PETSOS
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == PETSOS
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        petsos_attacks = self._filter_attacks_by_type(attack_dicts, PETSOS)
        if not petsos_attacks:
            return (None, None)
        
        return MoviePetSOS.doPetSOSs(petsos_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class HealSequenceBuilder(BaseSequenceBuilder):
    """Builder for Heal attack sequences"""
    
    def get_sequence_name(self):
        return "Heal"
    
    def get_priority(self):
        return SequencePriority.HEAL
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == HEAL
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        heal_attacks = self._filter_attacks_by_type(attack_dicts, HEAL)
        if not heal_attacks:
            return (None, None)
        
        # Check for heal bonus from interactive props
        has_heal_bonus = self.battle.getInteractivePropTrackBonus() == HEAL
        return MovieHeal.doHeals(heal_attacks, has_heal_bonus)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class TrapSequenceBuilder(BaseSequenceBuilder):
    """Builder for Trap attack sequences"""
    
    def get_sequence_name(self):
        return "Trap"
    
    def get_priority(self):
        return SequencePriority.TRAP
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == TRAP
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        trap_attacks = self._filter_attacks_by_type(attack_dicts, TRAP)
        if not trap_attacks:
            return (None, None)
        
        return MovieTrap.doTraps(trap_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class LureSequenceBuilder(BaseSequenceBuilder):
    """Builder for Lure attack sequences"""
    
    def get_sequence_name(self):
        return "Lure"
    
    def get_priority(self):
        return SequencePriority.LURE
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == LURE
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        lure_attacks = self._filter_attacks_by_type(attack_dicts, LURE)
        if not lure_attacks:
            return (None, None)
        
        return MovieLure.doLures(lure_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class SoundSequenceBuilder(BaseSequenceBuilder):
    """Builder for Sound attack sequences"""
    
    def get_sequence_name(self):
        return "Sound"
    
    def get_priority(self):
        return SequencePriority.SOUND
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == SOUND
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        sound_attacks = self._filter_attacks_by_type(attack_dicts, SOUND)
        if not sound_attacks:
            return (None, None)
        
        return MovieSound.doSounds(sound_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class ThrowSequenceBuilder(BaseSequenceBuilder):
    """Builder for Throw attack sequences"""
    
    def get_sequence_name(self):
        return "Throw"
    
    def get_priority(self):
        return SequencePriority.THROW
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == THROW
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        throw_attacks = self._filter_attacks_by_type(attack_dicts, THROW)
        if not throw_attacks:
            return (None, None)
        
        return MovieThrow.doThrows(throw_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class SquirtSequenceBuilder(BaseSequenceBuilder):
    """Builder for Squirt attack sequences"""
    
    def get_sequence_name(self):
        return "Squirt"
    
    def get_priority(self):
        return SequencePriority.SQUIRT
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == SQUIRT
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        squirt_attacks = self._filter_attacks_by_type(attack_dicts, SQUIRT)
        if not squirt_attacks:
            return (None, None)
        
        return MovieSquirt.doSquirts(squirt_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()

class DropSequenceBuilder(BaseSequenceBuilder):
    """Builder for Drop attack sequences"""
    
    def get_sequence_name(self):
        return "Drop"
    
    def get_priority(self):
        return SequencePriority.DROP
    
    def can_handle_attack(self, attack_dict):
        return attack_dict.get('track') == DROP
    
    def build_sequence(self, attack_dicts):
        if self._should_skip_sequence():
            return (None, None)
        
        drop_attacks = self._filter_attacks_by_type(attack_dicts, DROP)
        if not drop_attacks:
            return (None, None)
        
        return MovieDrop.doDrops(drop_attacks)
    
    def _should_skip_sequence(self):
        return not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue()