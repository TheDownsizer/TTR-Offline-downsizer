"""
Modular Gag Track Calculation System

This module provides a refactored approach to calculating toon attacks in battle,
separating each gag track into its own specialized calculator class.
"""

from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toon import NPCToons
from toontown.pets import PetTricks, DistributedPetProxyAI
from direct.showbase.PythonUtil import lerp
import random

class BaseTrackCalculator:
    """Base class for all gag track calculators"""
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.notify = battle_calculator.notify
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if the attack hits
        Returns: (hit_success, accuracy_result)
        """
        raise NotImplementedError("Subclasses must implement calculate_hit")
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate damage and effects for the attack
        """
        raise NotImplementedError("Subclasses must implement calculate_damage")
    
    def get_track_name(self):
        """Return the track name for debugging"""
        raise NotImplementedError("Subclasses must implement get_track_name")
    
    def _get_attack_data(self, attack_index):
        """Helper to get attack data"""
        return self.battle.toonAttacks[attack_index]
    
    def _get_actual_track_level(self, attack):
        """Helper to get actual track and level"""
        return self.battle_calculator._BattleCalculatorAI__getActualTrackLevel(attack)
    
    def _get_actual_track_level_hp(self, attack):
        """Helper to get actual track, level and HP"""
        return self.battle_calculator._BattleCalculatorAI__getActualTrackLevelHp(attack)
    
    def _suit_is_lured(self, suit_id, prev_round=False):
        """Helper to check if suit is lured"""
        return self.battle_calculator._BattleCalculatorAI__suitIsLured(suit_id, prev_round)
    
    def _combatant_dead(self, avId, toon=False):
        """Helper to check if combatant is dead"""
        return self.battle_calculator._BattleCalculatorAI__combatantDead(avId, toon)
    
    def _toon_track_exp(self, toon_id, track):
        """Helper to get toon track experience"""
        return self.battle_calculator._BattleCalculatorAI__toonTrackExp(toon_id, track)
    
    def _toon_check_gag_bonus(self, toon_id, track, level):
        """Helper to check gag bonus"""
        return self.battle_calculator._BattleCalculatorAI__toonCheckGagBonus(toon_id, track, level)
    
    def _check_prop_bonus(self, track):
        """Helper to check prop bonus"""
        return self.battle_calculator._BattleCalculatorAI__checkPropBonus(track)
    
    def _target_defense(self, suit, track):
        """Helper to get target defense"""
        return self.battle_calculator._BattleCalculatorAI__targetDefense(suit, track)
    
    def _calc_toon_acc_bonus(self, attack_index):
        """Helper to calculate accuracy bonus"""
        return self.battle_calculator._BattleCalculatorAI__calcToonAccBonus(attack_index)
    
    def _add_attack_exp(self, attack, track=-1, level=-1, attacker_id=-1):
        """Helper to add attack experience"""
        return self.battle_calculator._BattleCalculatorAI__addAttackExp(attack, track, level, attacker_id)

class TrackCalculatorError(Exception):
    """Exception raised for track calculation errors"""
    pass