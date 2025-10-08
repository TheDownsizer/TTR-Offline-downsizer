"""Lure track calculator."""

from .base import TrackCalculatorBase
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.BattleBase import *

class LureTrackCalculator(TrackCalculatorBase):
    """Calculator for Lure gag track."""
    
    def calculate_attack(self, toon_id, attack):
        """Calculate lure gag attack."""
        self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level, atk_acc):
        """Calculate lure gag attack damage."""
        valid_target_avail = 0
        lure_did_damage = 0
        curr_lure_id = -1
        
        # Check if this is a group attack
        is_group_attack = attackAffectsGroup(LURE, atk_level, attack[TOON_TRACK_COL])
        
        for curr_target in range(len(target_list)):
            target_id = target_list[curr_target].getDoId()
            target_lured = 0
            attack_level = -1
            attack_track = None
            attack_damage = 0
            
            if self.battle_calculator.getSuitTrapType(target_id) == NO_TRAP:
                if self.notify.getDebug():
                    self.notify.debug('Suit lured, but no trap exists')
                if self.battle_calculator.SUITS_UNLURED_IMMEDIATELY:
                    if not self._suit_is_lured(target_id, prev_round=1):
                        if not self._combatant_dead(target_id, toon=0):
                            valid_target_avail = 1
                        rounds = self.battle_calculator.NumRoundsLured[atk_level]
                        wakeup_chance = 100 - atk_acc * 2  # Fixed wakeup chance calculation
                        npc_lurer = attack[TOON_TRACK_COL] == NPCSOS
                        curr_lure_id = self.battle_calculator._BattleCalculatorAI__addLuredSuitInfo(target_id, -1, rounds, wakeup_chance, toon_id, atk_level, lureId=curr_lure_id, npc=npc_lurer)
                        if self.notify.getDebug():
                            self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(wakeup_chance) + '% chance to wake up each round')
                        target_lured = 1
            else:
                attack_track = TRAP
                if target_id in self.battle_calculator.traps:
                    trap_info = self.battle_calculator.traps[target_id]
                    attack_level = trap_info[0]
                else:
                    attack_level = NO_TRAP
                attack_damage = self.battle_calculator._BattleCalculatorAI__suitTrapDamage(target_id)
                trap_creator_id = self.battle_calculator._BattleCalculatorAI__trapCreator(target_id)
                if trap_creator_id > 0:
                    self.notify.debug('Giving trap EXP to toon ' + str(trap_creator_id))
                    self._add_attack_exp(attack, track=TRAP, level=attack_level, attacker_id=trap_creator_id)
                self.battle_calculator._BattleCalculatorAI__clearTrapCreator(trap_creator_id, target_id)
                lure_did_damage = 1
                if self.notify.getDebug():
                    self.notify.debug('Suit lured right onto a trap!')
                if not self._combatant_dead(target_id, toon=0):
                    valid_target_avail = 1
                target_lured = 1
            
            if not self.battle_calculator.SUITS_UNLURED_IMMEDIATELY:
                if not self._suit_is_lured(target_id, prev_round=1):
                    if not self._combatant_dead(target_id, toon=0):
                        valid_target_avail = 1
                    rounds = self.battle_calculator.NumRoundsLured[atk_level]
                    wakeup_chance = 100 - atk_acc * 2  # Fixed wakeup chance calculation
                    npc_lurer = attack[TOON_TRACK_COL] == NPCSOS
                    curr_lure_id = self.battle_calculator._BattleCalculatorAI__addLuredSuitInfo(target_id, -1, rounds, wakeup_chance, toon_id, atk_level, lureId=curr_lure_id, npc=npc_lurer)
                    if self.notify.getDebug():
                        self.notify.debug('Suit lured for ' + str(rounds) + ' rounds max with ' + str(wakeup_chance) + '% chance to wake up each round')
                    target_lured = 1
                if attack_level != -1:
                    self.battle_calculator._BattleCalculatorAI__addLuredSuitsDelayed(toon_id, target_id)
            
            if target_lured and (target_id not in self.battle_calculator.successfulLures or target_id in self.battle_calculator.successfulLures and self.battle_calculator.successfulLures[target_id][1] < atk_level):
                self.notify.debug('Adding target ' + str(target_id) + ' to successfulLures list')
                self.battle_calculator.successfulLures[target_id] = [toon_id, atk_level, atk_acc, -1]
                
            # Apply lure result
            if attack_level == -1:
                result = LURE_SUCCEEDED
            else:
                result = attack_damage
                
            if result != 0:
                targets = self._get_toon_targets(attack)
                if target_list[curr_target] in targets:
                    # For group attacks, set target index to -1
                    if is_group_attack:
                        target_index = -1
                    else:
                        target_index = targets.index(target_list[curr_target])
                    if target_id in self.battle_calculator.successfulLures:
                        self.notify.debug('Updating lure damage to ' + str(result))
                        self.battle_calculator.successfulLures[target_id][3] = result
                    else:
                        # Make sure we don't go out of bounds for group attacks
                        if is_group_attack:
                            # For group attacks, we still need to set the damage in the correct position
                            # Find the position of this target in the active suits list
                            if target_list[curr_target] in self.battle.activeSuits:
                                target_pos = self.battle.activeSuits.index(target_list[curr_target])
                                if target_pos < len(attack[TOON_HP_COL]):
                                    attack[TOON_HP_COL][target_pos] = result
                        else:
                            attack[TOON_HP_COL][target_index] = result
        
        # Handle lure experience
        if lure_did_damage:
            if self.battle_calculator.itemIsCredit(LURE, atk_level):
                self.notify.debug('Giving lure EXP to toon ' + str(toon_id))
                self._add_attack_exp(attack)
        
        # Clear attack if no valid targets
        if not valid_target_avail and self._prev_atk_track(toon_id) != LURE:
            self._clear_attack(toon_id)
    
    def create_target_list(self, attack_index, attack):
        """Create target list for lure attack."""
        # Use the base implementation for lure attacks
        return super().create_target_list(attack_index, attack)
    
    def is_unlure_attack(self, attack_index, attack):
        """Lure attacks don't unlure suits, they lure them."""
        return False