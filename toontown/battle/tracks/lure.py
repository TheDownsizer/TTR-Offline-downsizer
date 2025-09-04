"""
Lure Track Calculator

Handles all lure gag calculations including accuracy, duration, and trap interactions.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class LureTrackCalculator(BaseTrackCalculator):
    """Calculator for Lure track attacks"""
    
    def get_track_name(self):
        return "Lure"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if lure attack hits
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
        
        if attack[TOON_TRACK_COL] == NPCSOS:
            rand_choice = 0
        else:
            rand_choice = random.randint(0, 99)
        
        # Calculate base accuracy
        prop_acc = AvPropAccuracy[atkTrack][atkLevel]
        
        # Apply organic/prop bonuses for lure
        tree_bonus = self._toon_check_gag_bonus(attack[TOON_ID_COL], atkTrack, atkLevel)
        prop_bonus = self._check_prop_bonus(atkTrack)
        
        if self.battle_calculator.propAndOrganicBonusStack:
            prop_acc = 0
            if tree_bonus:
                if self.notify.getDebug():
                    self.notify.debug('using organic bonus lure accuracy')
                prop_acc += AvLureBonusAccuracy[atkLevel]
            if prop_bonus:
                if self.notify.getDebug():
                    self.notify.debug('using prop bonus lure accuracy')
                prop_acc += AvLureBonusAccuracy[atkLevel]
        elif tree_bonus or prop_bonus:
            if self.notify.getDebug():
                self.notify.debug('using organic OR prop bonus lure accuracy')
            prop_acc = AvLureBonusAccuracy[atkLevel]
        
        # Add experience and defense bonuses
        track_exp = self._toon_track_exp(attack[TOON_ID_COL], atkTrack)
        target_def = self._calculate_target_defense(attack_targets, atkTrack)
        
        attack_acc = prop_acc + track_exp + target_def
        
        # Check for same track bonus from previous attacks
        curr_atk = self.battle_calculator.toonAtkOrder.index(attack_index)
        if curr_atk > 0:
            prev_atk_id = self.battle_calculator.toonAtkOrder[curr_atk - 1]
            prev_attack = self.battle.toonAttacks[prev_atk_id]
            prev_atk_track = self.battle_calculator._BattleCalculatorAI__getActualTrack(prev_attack)
            
            # Check for lure chaining bonus
            lure = (atkTrack == LURE and 
                   (not attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL]) and 
                    attack[TOON_TGT_COL] in self.battle_calculator.successfulLures or
                    attackAffectsGroup(atkTrack, atkLevel, attack[TOON_TRACK_COL])))
            
            if (atkTrack == prev_atk_track and 
                (attack[TOON_TGT_COL] == prev_attack[TOON_TGT_COL] or lure)):
                attack[TOON_ACCBONUS_COL] = prev_attack[TOON_ACCBONUS_COL]
                return (not attack[TOON_ACCBONUS_COL], attack_acc)
        
        # Apply accuracy bonus
        acc = attack_acc + self._calc_toon_acc_bonus(attack_index)
        
        if acc > MaxToonAcc:
            acc = MaxToonAcc
        
        if rand_choice < acc:
            if self.notify.getDebug():
                self.notify.debug(f'HIT: Lure attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 0
        else:
            if self.notify.getDebug():
                self.notify.debug(f'MISS: Lure attack rolled {rand_choice} to hit with accuracy {acc}')
            attack[TOON_ACCBONUS_COL] = 1
        
        return (not attack[TOON_ACCBONUS_COL], attack_acc)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate lure effects and trap interactions
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel, atkHp = self._get_actual_track_level_hp(attack)
        
        # Check if attack hit
        hit_success, atk_acc = self.calculate_hit(attack_index, attack_targets)
        if not hit_success:
            return
        
        valid_target_available = False
        lure_did_damage = False
        curr_lure_id = -1
        
        for target_idx, target in enumerate(attack_targets):
            target_id = target.getDoId()
            attack_level = -1
            attack_track = None
            attack_damage = 0
            target_lured = False
            
            if self._combatant_dead(target_id, toon=False):
                continue
            
            # Check for trap interaction
            if self._get_suit_trap_type(target_id) == NO_TRAP:
                # No trap - normal lure
                if self.notify.getDebug():
                    self.notify.debug('Suit lured, but no trap exists')
                
                if self.battle_calculator.SUITS_UNLURED_IMMEDIATELY:
                    if not self._suit_is_lured(target_id, prev_round=True):
                        if not self._combatant_dead(target_id, toon=False):
                            valid_target_available = True
                        
                        rounds = self.battle_calculator.NumRoundsLured[atkLevel]
                        wakeup_chance = 100 - atk_acc * 2
                        npc_lurer = attack[TOON_TRACK_COL] == NPCSOS
                        
                        curr_lure_id = self._add_lured_suit_info(
                            target_id, -1, rounds, wakeup_chance, 
                            attack[TOON_ID_COL], atkLevel, 
                            lure_id=curr_lure_id, npc=npc_lurer)
                        
                        if self.notify.getDebug():
                            self.notify.debug(f'Suit lured for {rounds} rounds max with '
                                            f'{wakeup_chance}% chance to wake up each round')
                        target_lured = True
            else:
                # Trap exists - trigger it
                attack_track = TRAP
                trap_info = self.battle_calculator.traps.get(target_id)
                if trap_info:
                    attack_level = trap_info[0]
                else:
                    attack_level = NO_TRAP
                
                attack_damage = self._suit_trap_damage(target_id)
                trap_creator_id = self._trap_creator(target_id)
                
                if trap_creator_id > 0:
                    if self.notify.getDebug():
                        self.notify.debug(f'Giving trap EXP to toon {trap_creator_id}')
                    self._add_attack_exp(attack, track=TRAP, level=attack_level, 
                                       attacker_id=trap_creator_id)
                
                self._clear_trap_creator(trap_creator_id, target_id)
                lure_did_damage = True
                
                if self.notify.getDebug():
                    self.notify.debug(f'Suit lured right onto a trap! '
                                    f'({AvProps[attack_track][attack_level]},{attack_level})')
                
                if not self._combatant_dead(target_id, toon=False):
                    valid_target_available = True
                target_lured = True
            
            # Handle delayed lure for non-immediate unlure mode
            if not self.battle_calculator.SUITS_UNLURED_IMMEDIATELY:
                if not self._suit_is_lured(target_id, prev_round=True):
                    if not self._combatant_dead(target_id, toon=False):
                        valid_target_available = True
                    
                    rounds = self.battle_calculator.NumRoundsLured[atkLevel]
                    wakeup_chance = 100 - atk_acc * 2
                    npc_lurer = attack[TOON_TRACK_COL] == NPCSOS
                    
                    curr_lure_id = self._add_lured_suit_info(
                        target_id, -1, rounds, wakeup_chance,
                        attack[TOON_ID_COL], atkLevel,
                        lure_id=curr_lure_id, npc=npc_lurer)
                    
                    target_lured = True
                
                if attack_level != -1:
                    self._add_lured_suits_delayed(attack[TOON_ID_COL], target_id)
            
            # Track successful lures
            if (target_lured and 
                (target_id not in self.battle_calculator.successfulLures or
                 target_id in self.battle_calculator.successfulLures and 
                 self.battle_calculator.successfulLures[target_id][1] < atkLevel)):
                
                if self.notify.getDebug():
                    self.notify.debug(f'Adding target {target_id} to successfulLures list')
                
                self.battle_calculator.successfulLures[target_id] = [
                    attack[TOON_ID_COL], atkLevel, atk_acc, attack_damage]
            
            # Set damage in attack
            if attack_damage != 0:
                targets = self._get_suit_targets(attack)
                if target in targets:
                    target_index = targets.index(target)
                    if target_id in self.battle_calculator.successfulLures:
                        self.notify.debug(f'Updating lure damage to {attack_damage}')
                        self.battle_calculator.successfulLures[target_id][3] = attack_damage
                    else:
                        attack[TOON_HP_COL][target_index] = attack_damage
                        
                    # Give lure exp for trap activation
                    if attack_damage > 0:
                        lure_infos = self._get_lured_exp_info(target_id)
                        for curr_info in lure_infos:
                            if curr_info[3]:  # Check if credit should be given
                                if self.notify.getDebug():
                                    self.notify.debug(f'Giving lure EXP to toon {curr_info[0]}')
                                self._add_attack_exp(attack, track=LURE, level=curr_info[1],
                                                   attacker_id=curr_info[0])
                            self._clear_lurer(curr_info[0], lure_id=curr_info[2])
        
        # Give lure experience if trap was triggered
        if lure_did_damage:
            if self._item_is_credit(atkTrack, atkLevel):
                if self.notify.getDebug():
                    self.notify.debug(f'Giving lure EXP to toon {attack[TOON_ID_COL]}')
                self._add_attack_exp(attack)
        
        # Clear attack if no valid targets and previous track was different
        if not valid_target_available and self._prev_atk_track(attack[TOON_ID_COL]) != atkTrack:
            self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _calculate_target_defense(self, attack_targets, track):
        """Calculate combined target defense"""
        tgt_def = 0
        for target in attack_targets:
            this_suit_def = self._target_defense(target, track)
            if self.notify.getDebug():
                self.notify.debug(f'Examining suit def for lure attack: {this_suit_def}')
            tgt_def = min(this_suit_def, tgt_def)
        return tgt_def
    
    def _get_suit_trap_type(self, suit_id):
        """Helper to get suit trap type"""
        return self.battle_calculator.getSuitTrapType(suit_id)
    
    def _suit_trap_damage(self, suit_id):
        """Helper to get suit trap damage"""
        return self.battle_calculator._BattleCalculatorAI__suitTrapDamage(suit_id)
    
    def _trap_creator(self, suit_id):
        """Helper to get trap creator"""
        return self.battle_calculator._BattleCalculatorAI__trapCreator(suit_id)
    
    def _clear_trap_creator(self, creator_id, suit_id=None):
        """Helper to clear trap creator"""
        return self.battle_calculator._BattleCalculatorAI__clearTrapCreator(creator_id, suit_id)
    
    def _add_lured_suit_info(self, suit_id, curr_rounds, max_rounds, wake_chance, 
                           lurer, lure_level, lure_id=-1, npc=0):
        """Helper to add lured suit info"""
        return self.battle_calculator._BattleCalculatorAI__addLuredSuitInfo(
            suit_id, curr_rounds, max_rounds, wake_chance, lurer, lure_level, lure_id, npc)
    
    def _add_lured_suits_delayed(self, toon_id, target_id=-1, ignore_damage_check=False):
        """Helper to add lured suits to delayed list"""
        return self.battle_calculator._BattleCalculatorAI__addLuredSuitsDelayed(
            toon_id, target_id, ignore_damage_check)
    
    def _get_lured_exp_info(self, suit_id):
        """Helper to get lured experience info"""
        return self.battle_calculator._BattleCalculatorAI__getLuredExpInfo(suit_id)
    
    def _clear_lurer(self, lurer_id, lure_id=-1):
        """Helper to clear lurer"""
        return self.battle_calculator._BattleCalculatorAI__clearLurer(lurer_id, lure_id)
    
    def _item_is_credit(self, track, level):
        """Helper to check if item gives credit"""
        return self.battle_calculator.itemIsCredit(track, level)
    
    def _get_suit_targets(self, attack):
        """Helper to get suit targets"""
        return self.battle.activeSuits
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)