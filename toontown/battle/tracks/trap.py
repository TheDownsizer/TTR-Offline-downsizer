"""
Trap Track Calculator

Handles all trap gag calculations including placement and activation.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class TrapTrackCalculator(BaseTrackCalculator):
    """Calculator for Trap track attacks"""
    
    def get_track_name(self):
        return "Trap"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if trap attack hits
        Traps always hit when placed
        """
        if self.battle_calculator.tutorialFlag:
            return (1, 95)
            
        if self.battle_calculator.toonsAlways5050:
            roll = random.randint(0, 99)
            return (1, 95) if roll < 50 else (0, 0)
        
        if self.battle_calculator.toonsAlwaysHit:
            return (1, 75)
        elif self.battle_calculator.toonsAlwaysMiss:
            return (0, 0)
        
        attack = self._get_attack_data(attack_index)
        
        if self.notify.getDebug():
            self.notify.debug('Attack is a trap, so it hits regardless')
        
        # Traps always hit when being placed
        attack[TOON_ACCBONUS_COL] = 0
        return (1, 100)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate trap placement and damage
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel, atkHp = self._get_actual_track_level_hp(attack)
        
        valid_target_available = False
        
        for target_idx, target in enumerate(attack_targets):
            target_id = target.getDoId()
            
            if self._combatant_dead(target_id, toon=False):
                continue
            
            # Check for multiple traps conflict
            if self.battle_calculator.CLEAR_MULTIPLE_TRAPS:
                if self._get_suit_trap_type(target_id) != NO_TRAP:
                    self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
                    return
            
            valid_target_available = True
            
            npc_damage = 0
            if attack[TOON_TRACK_COL] == NPCSOS:
                npc_damage = atkHp
            
            # Handle uber gag (train trap)
            if atkLevel == UBER_GAG_LEVEL_INDEX:
                self._add_suit_group_trap(target_id, atkLevel, attack[TOON_ID_COL], 
                                        attack_targets, npc_damage)
                
                # Check if train trap is on lured suit
                if self._suit_is_lured(target_id):
                    if self.notify.getDebug():
                        self.notify.debug(f'Train Trap on lured suit {target_id}, '
                                        'indicating with KBBONUS_COL flag')
                    
                    tgt_pos = self.battle.activeSuits.index(target)
                    attack[TOON_KBBONUS_COL][tgt_pos] = self.battle_calculator.KBBONUS_LURED_FLAG
            else:
                self._add_suit_trap(target_id, atkLevel, attack[TOON_ID_COL], npc_damage)
            
            # Traps don't do immediate damage
            targets = self._get_suit_targets(attack)
            if target in targets:
                target_index = targets.index(target)
                attack[TOON_HP_COL][target_index] = 0
        
        # Clear attack if no valid targets
        if not valid_target_available:
            prev_track = self._prev_atk_track(attack[TOON_ID_COL])
            if prev_track != TRAP:
                self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _get_suit_trap_type(self, suit_id):
        """Helper to get suit trap type"""
        return self.battle_calculator.getSuitTrapType(suit_id)
    
    def _add_suit_trap(self, suit_id, trap_level, attacker_id, npc_damage=0):
        """Helper to add trap to single suit"""
        return self.battle_calculator._BattleCalculatorAI__addSuitTrap(
            suit_id, trap_level, attacker_id, npc_damage)
    
    def _add_suit_group_trap(self, suit_id, trap_level, attacker_id, all_suits, npc_damage=0):
        """Helper to add trap to group of suits (train trap)"""
        return self.battle_calculator._BattleCalculatorAI__addSuitGroupTrap(
            suit_id, trap_level, attacker_id, all_suits, npc_damage)
    
    def _get_suit_targets(self, attack):
        """Helper to get suit targets"""
        return self.battle.activeSuits
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)