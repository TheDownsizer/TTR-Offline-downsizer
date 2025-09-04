"""
Squirt Track Calculator

Handles all squirt gag calculations including accuracy, damage, and knockback effects.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class SquirtTrackCalculator(BaseTrackCalculator):
    """Calculator for Squirt track attacks"""
    
    def get_track_name(self):
        return "Squirt"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if squirt attack hits
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
        
        # Calculate target defense
        tgt_def = 0
        num_lured = 0
        for target in attack_targets:
            this_suit_def = self._target_defense(target, atkTrack)
            if self.notify.getDebug():
                self.notify.debug(f'Examining suit def for squirt attack: {this_suit_def}')
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
            self.notify.debug(f'Suit defense used for squirt attack: {tgt_def}')
            self.notify.debug(f'Toon track exp bonus used for squirt attack: {track_exp}')
        
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
                        self.notify.debug('DODGE: Squirt attack track dodged')
                elif prev_attack[TOON_ACCBONUS_COL] == 0:
                    if self.notify.getDebug():
                        self.notify.debug('HIT: Squirt attack track hit')
                
                attack[TOON_ACCBONUS_COL] = prev_attack[TOON_ACCBONUS_COL]
                return (not attack[TOON_ACCBONUS_COL], attack_acc)
        
        # Apply accuracy bonus
        acc = attack_acc + self._calc_toon_acc_bonus(attack_index)
        
        # Squirt gets bonus against lured targets
        if num_lured == len(attack_targets):
            if self.notify.getDebug():
                self.notify.debug('All targets are lured, squirt attack hits')
            attack[TOON_ACCBONUS_COL] = 0
            return (1, 100)
        else:
            # Partial lure bonus
            lured_ratio = float(num_lured) / float(len(attack_targets))
            acc_adjust = 100 * lured_ratio
            if acc_adjust > 0 and self.notify.getDebug():
                self.notify.debug(f'{num_lured} out of {len(attack_targets)} targets are lured, '
                                f'so adding {acc_adjust} to attack accuracy')
            acc += acc_adjust
        
        if acc > MaxToonAcc:
            acc = MaxToonAcc
        
        if rand_choice < acc:
            if self.notify.getDebug():
                self.notify.debug(f'HIT: Squirt attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if self.notify.getDebug():
                self.notify.debug(f'MISS: Squirt attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 1
        
        return (not attack[TOON_ACCBONUS_COL], attack_acc)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate squirt damage and knockback effects
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
                self.notify.debug(f'Squirt does {attack_damage} damage to suit')
            
            # Set damage in attack
            targets = self._get_suit_targets(attack)
            if target in targets:
                target_index = targets.index(target)
                attack[TOON_HP_COL][target_index] = attack_damage
                
                # Handle lure breaking and experience
                if attack_damage > 0:
                    lure_infos = self._get_lured_exp_info(target_id)
                    for curr_info in lure_infos:
                        if curr_info[3]:  # Check if credit should be given
                            if self.notify.getDebug():
                                self.notify.debug(f'Giving lure EXP to toon {curr_info[0]}')
                            self._add_attack_exp(attack, track=LURE, level=curr_info[1],
                                               attacker_id=curr_info[0])
                        self._clear_lurer(curr_info[0], lure_id=curr_info[2])
        
        # Clear attack if no valid targets
        if not valid_target_available and self._prev_atk_track(attack[TOON_ID_COL]) != atkTrack:
            self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def is_knockback_attack(self):
        """
        Squirt attacks are knockback attacks
        """
        return True
    
    def is_unlure_attack(self):
        """
        Squirt attacks unlure targets
        """
        return True
    
    def _get_lured_exp_info(self, suit_id):
        """Helper to get lured experience info"""
        return self.battle_calculator._BattleCalculatorAI__getLuredExpInfo(suit_id)
    
    def _clear_lurer(self, lurer_id, lure_id=-1):
        """Helper to clear lurer"""
        return self.battle_calculator._BattleCalculatorAI__clearLurer(lurer_id, lure_id)
    
    def _get_suit_targets(self, attack):
        """Helper to get suit targets"""
        return self.battle.activeSuits
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)