"""
Drop Track Calculator

Handles all drop gag calculations including accuracy, damage, and lure interactions.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class DropTrackCalculator(BaseTrackCalculator):
    """Calculator for Drop track attacks"""
    
    def get_track_name(self):
        return "Drop"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if drop attack hits
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
        atkTrack, atkLevel = self._get_actual_track_level(attack)
        
        # Special case for NPC drop attacks
        if atkTrack == DROP and attack[TOON_TRACK_COL] == NPCSOS:
            unlured_suits = 0
            for target in attack_targets:
                if not self._suit_is_lured(target.getDoId()):
                    unlured_suits = 1
            
            if unlured_suits == 0:
                attack[TOON_ACCBONUS_COL] = 1
                return (0, 0)
        
        # Regular drop accuracy calculation
        elif atkTrack == DROP:
            all_lured = True
            for target in attack_targets:
                if not self._suit_is_lured(target.getDoId()):
                    all_lured = False
                    break
            
            # Drop misses if all targets are lured
            if all_lured:
                attack[TOON_ACCBONUS_COL] = 1
                return (0, 0)
        
        # Calculate target defense
        tgt_def = 0
        num_lured = 0
        for target in attack_targets:
            this_suit_def = self._target_defense(target, atkTrack)
            if self.notify.getDebug():
                self.notify.debug(f'Examining suit def for drop attack: {this_suit_def}')
            tgt_def = min(this_suit_def, tgt_def)
            
            if self._suit_is_lured(target.getDoId()):
                num_lured += 1
        
        # Get track experience bonus
        track_exp = self._toon_track_exp(attack[TOON_ID_COL], atkTrack)
        
        # Check for same track bonus from other toons
        for other_atk in self.battle_calculator.toonAtkOrder:
            if other_atk != attack[TOON_ID_COL]:
                next_attack = self.battle.toonAttacks[other_atk]
                next_atk_track = self.battle_calculator._BattleCalculatorAI__getActualTrack(next_attack)
                if (atkTrack == next_atk_track and 
                    attack[TOON_TGT_COL] == next_attack[TOON_TGT_COL]):
                    curr_track_exp = self._toon_track_exp(next_attack[TOON_ID_COL], atkTrack)
                    if self.notify.getDebug():
                        self.notify.debug(f'Examining toon track exp bonus: {curr_track_exp}')
                    track_exp = max(curr_track_exp, track_exp)
        
        if self.notify.getDebug():
            self.notify.debug(f'Suit defense used for drop attack: {tgt_def}')
            self.notify.debug(f'Toon track exp bonus used for drop attack: {track_exp}')
        
        # Random roll
        if attack[TOON_TRACK_COL] == NPCSOS:
            rand_choice = 0
        else:
            rand_choice = random.randint(0, 99)
        
        # Base accuracy
        prop_acc = AvPropAccuracy[atkTrack][atkLevel]
        attack_acc = prop_acc + track_exp + tgt_def
        
        # Check for same track bonus from previous attacks
        curr_atk = self.battle_calculator.toonAtkOrder.index(attack_index)
        if curr_atk > 0:
            prev_atk_id = self.battle_calculator.toonAtkOrder[curr_atk - 1]
            prev_attack = self.battle.toonAttacks[prev_atk_id]
            prev_atk_track = self.battle_calculator._BattleCalculatorAI__getActualTrack(prev_attack)
            
            if (atkTrack == prev_atk_track and 
                attack[TOON_TGT_COL] == prev_attack[TOON_TGT_COL]):
                if prev_attack[TOON_ACCBONUS_COL] == 1:
                    if self.notify.getDebug():
                        self.notify.debug('DODGE: Drop attack track dodged')
                elif prev_attack[TOON_ACCBONUS_COL] == 0:
                    if self.notify.getDebug():
                        self.notify.debug('HIT: Drop attack track hit')
                
                attack[TOON_ACCBONUS_COL] = prev_attack[TOON_ACCBONUS_COL]
                return (not attack[TOON_ACCBONUS_COL], attack_acc)
        
        # Apply accuracy bonus
        acc = attack_acc + self._calc_toon_acc_bonus(attack_index)
        
        # Drop always misses lured targets (already handled above for all lured)
        if num_lured == len(attack_targets):
            if self.notify.getDebug():
                self.notify.debug('All targets are lured, drop attack misses')
            attack[TOON_ACCBONUS_COL] = 1
            return (0, 0)
        
        if acc > MaxToonAcc:
            acc = MaxToonAcc
        
        if rand_choice < acc:
            if self.notify.getDebug():
                self.notify.debug(f'HIT: Drop attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if self.notify.getDebug():
                self.notify.debug(f'MISS: Drop attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 1
        
        return (not attack[TOON_ACCBONUS_COL], attack_acc)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate drop damage and effects
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel, atkHp = self._get_actual_track_level_hp(attack)
        
        # Check if attack hit
        hit_success, atk_acc = self.calculate_hit(attack_index, attack_targets)
        if not hit_success:
            return
        
        valid_target_available = False
        
        for target_idx, target in enumerate(attack_targets):
            target_id = target.getDoId()
            
            if self._combatant_dead(target_id, toon=False):
                continue
            
            # Check for lured target special handling
            if self._suit_is_lured(target_id):
                if self.notify.getDebug():
                    self.notify.debug('not setting validTargetAvail, since drop on a lured suit')
                    self.notify.debug('setting damage to 0, since drop on a lured suit')
                
                # Flag as lured but don't count as valid target
                tgt_pos = self.battle.activeSuits.index(target)
                attack[TOON_KBBONUS_COL][tgt_pos] = self.battle_calculator.KBBONUS_LURED_FLAG
                
                # Set damage to 0 for lured targets
                targets = self._get_suit_targets(attack)
                if target in targets:
                    target_index = targets.index(target)
                    attack[TOON_HP_COL][target_index] = 0
                continue
            
            valid_target_available = True
            
            # Calculate damage
            toon = self.battle.getToon(attack[TOON_ID_COL])
            if attack[TOON_TRACK_COL] == NPCSOS:
                attack_damage = atkHp
            else:
                organic_bonus = self._toon_check_gag_bonus(attack[TOON_ID_COL], atkTrack, atkLevel)
                prop_bonus = self._check_prop_bonus(atkTrack)
                attack_damage = getAvPropDamage(atkTrack, atkLevel, toon.experience.getExp(atkTrack),
                                              organic_bonus, prop_bonus,
                                              self.battle_calculator.propAndOrganicBonusStack)
            
            if self.notify.getDebug():
                self.notify.debug(f'Drop does {attack_damage} damage to suit')
            
            # Set damage in attack
            targets = self._get_suit_targets(attack)
            if target in targets:
                target_index = targets.index(target)
                attack[TOON_HP_COL][target_index] = attack_damage
        
        # Clear attack if no valid targets
        if not valid_target_available and self._prev_atk_track(attack[TOON_ID_COL]) != atkTrack:
            self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _get_suit_targets(self, attack):
        """Helper to get suit targets"""
        return self.battle.activeSuits
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)