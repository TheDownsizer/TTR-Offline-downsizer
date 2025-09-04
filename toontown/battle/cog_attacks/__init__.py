"""
Modular Cog Attack Calculation System

This module provides a refactored approach to calculating cog attacks in battle,
separating different attack types into specialized calculator classes for better
maintainability and extensibility.
"""

from ..BattleBase import *
from ..SuitBattleGlobals import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class BaseCogAttackCalculator:
    """Base class for all cog attack calculators"""
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.notify = battle_calculator.notify
    
    def calculate_attack_type(self, attack_index):
        """
        Calculate which attack type a cog should use
        Returns: attack type index
        """
        raise NotImplementedError("Subclasses must implement calculate_attack_type")
    
    def calculate_target(self, attack_index):
        """
        Calculate which target(s) the cog should attack
        Returns: target index or list of target indices
        """
        raise NotImplementedError("Subclasses must implement calculate_target")
    
    def calculate_hit(self, attack_index):
        """
        Calculate if the cog attack hits
        Returns: 1 if hit, 0 if miss
        """
        raise NotImplementedError("Subclasses must implement calculate_hit")
    
    def calculate_damage(self, attack_index):
        """
        Calculate damage and effects for the cog attack
        """
        raise NotImplementedError("Subclasses must implement calculate_damage")
    
    def affects_group(self, attack):
        """
        Check if attack affects group or single target
        Returns: True if group attack, False if single target
        """
        raise NotImplementedError("Subclasses must implement affects_group")
    
    def create_target_list(self, attack_index):
        """
        Create list of targets for the attack
        Returns: list of target IDs
        """
        raise NotImplementedError("Subclasses must implement create_target_list")
    
    def get_attack_name(self):
        """Return the attack type name for debugging"""
        raise NotImplementedError("Subclasses must implement get_attack_name")
    
    # Helper methods that can be used by all calculators
    def _get_attack_data(self, attack_index):
        """Helper to get attack data"""
        return self.battle.suitAttacks[attack_index]
    
    def _get_suit(self, attack_index):
        """Helper to get suit performing attack"""
        return self.battle.activeSuits[attack_index]
    
    def _combatant_dead(self, avId, toon=False):
        """Helper to check if combatant is dead"""
        return self.battle_calculator._BattleCalculatorAI__combatantDead(avId, toon)
    
    def _suit_is_lured(self, suit_id):
        """Helper to check if suit is lured"""
        return self.battle_calculator._BattleCalculatorAI__suitIsLured(suit_id)
    
    def _combatant_just_revived(self, suit_id):
        """Helper to check if suit just revived"""
        return self.battle_calculator._BattleCalculatorAI__combatantJustRevived(suit_id)
    
    def _pick_random_toon(self, suit_id):
        """Helper to pick random toon target"""
        return self.battle_calculator._BattleCalculatorAI__pickRandomToon(suit_id)
    
    def _get_toon_hp(self, toon_id):
        """Helper to get toon's current HP"""
        return self.battle_calculator._BattleCalculatorAI__getToonHp(toon_id)

class CogAttackCalculatorError(Exception):
    """Exception raised for cog attack calculation errors"""
    pass