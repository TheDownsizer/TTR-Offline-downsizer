"""
Track Calculator Manager

Manages and coordinates all track calculators for battle calculations.
"""

from .heal import HealTrackCalculator
from .trap import TrapTrackCalculator
from .lure import LureTrackCalculator
from .sound import SoundTrackCalculator
from .throw import ThrowTrackCalculator
from .squirt import SquirtTrackCalculator
from .drop import DropTrackCalculator
from .special import SpecialTrackCalculator
from . import TrackCalculatorError
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *

class TrackCalculatorManager:
    """
    Manages all track calculators and routes attacks to appropriate handlers
    """
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.notify = battle_calculator.notify
        
        # Initialize all track calculators
        self.track_calculators = {
            HEAL: HealTrackCalculator(battle_calculator),
            TRAP: TrapTrackCalculator(battle_calculator),
            LURE: LureTrackCalculator(battle_calculator),
            SOUND: SoundTrackCalculator(battle_calculator),
            THROW: ThrowTrackCalculator(battle_calculator),
            SQUIRT: SquirtTrackCalculator(battle_calculator),
            DROP: DropTrackCalculator(battle_calculator),
            FIRE: SpecialTrackCalculator(battle_calculator),
            PETSOS: SpecialTrackCalculator(battle_calculator),
            NPCSOS: SpecialTrackCalculator(battle_calculator)
        }
    
    def calculate_toon_attack_hit(self, attack_index, attack_targets):
        """
        Calculate if a toon attack hits using the appropriate track calculator
        """
        attack = self.battle.toonAttacks[attack_index]
        track = self._get_actual_track(attack)
        
        if track in self.track_calculators:
            calculator = self.track_calculators[track]
            return calculator.calculate_hit(attack_index, attack_targets)
        else:
            raise TrackCalculatorError(f"No calculator found for track: {track}")
    
    def calculate_toon_attack_damage(self, attack_index, attack_targets):
        """
        Calculate damage for a toon attack using the appropriate track calculator
        """
        attack = self.battle.toonAttacks[attack_index]
        track = self._get_actual_track(attack)
        
        if track in self.track_calculators:
            calculator = self.track_calculators[track]
            return calculator.calculate_damage(attack_index, attack_targets)
        else:
            raise TrackCalculatorError(f"No calculator found for track: {track}")
    
    def is_knockback_attack(self, attack_index):
        """
        Check if an attack is a knockback attack
        """
        attack = self.battle.toonAttacks[attack_index]
        track = self._get_actual_track(attack)
        
        if track in [THROW, SQUIRT]:
            return True
        return False
    
    def is_unlure_attack(self, attack_index):
        """
        Check if an attack unlures targets
        """
        attack = self.battle.toonAttacks[attack_index]
        track = self._get_actual_track(attack)
        
        if track in [THROW, SQUIRT, SOUND]:
            return True
        return False
    
    def get_track_calculator(self, track):
        """
        Get the calculator for a specific track
        """
        if track in self.track_calculators:
            return self.track_calculators[track]
        else:
            raise TrackCalculatorError(f"No calculator found for track: {track}")
    
    def _get_actual_track(self, attack):
        """
        Get the actual track of an attack (handles NPCSOS)
        """
        return self.battle_calculator._BattleCalculatorAI__getActualTrack(attack)
    
    def create_toon_target_list(self, attack_index):
        """
        Create target list for toon attack based on track type
        """
        attack = self.battle.toonAttacks[attack_index]
        track, level = self.battle_calculator._BattleCalculatorAI__getActualTrackLevel(attack)
        target_list = []
        
        if track == NPCSOS:
            return target_list
        
        if not attackAffectsGroup(track, level, attack[TOON_TRACK_COL]):
            # Single target attack
            if track == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle.findSuit(attack[TOON_TGT_COL])
            
            if target is not None:
                target_list.append(target)
        
        elif track == HEAL or track == PETSOS:
            # Group heal
            if attack[TOON_TRACK_COL] == NPCSOS or track == PETSOS:
                target_list = self.battle.activeToons
            else:
                # Heal others (not self)
                for toon in self.battle.activeToons:
                    if attack[TOON_ID_COL] != toon:
                        target_list.append(toon)
        else:
            # Group attack on suits
            target_list = self.battle.activeSuits
        
        return target_list
    
    def get_all_calculators(self):
        """
        Get all track calculators for debugging/inspection
        """
        return self.track_calculators
    
    def validate_attack(self, attack_index):
        """
        Validate that an attack can be processed by a calculator
        """
        try:
            attack = self.battle.toonAttacks[attack_index]
            track = self._get_actual_track(attack)
            return track in self.track_calculators
        except Exception as e:
            if self.notify.getDebug():
                self.notify.debug(f"Attack validation failed: {e}")
            return False