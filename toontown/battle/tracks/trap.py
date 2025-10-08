"""Trap track calculator."""

from .base import TrackCalculatorBase
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.BattleBase import *

class TrapTrackCalculator(TrackCalculatorBase):
    """Calculator for Trap gag track."""
    
    def calculate_attack(self, toon_id, attack):
        """Calculate trap gag attack."""
        self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level, atk_hp):
        """Calculate trap gag attack damage."""
        for curr_target in range(len(target_list)):
            target_id = target_list[curr_target].getDoId()
            
            npc_damage = 0
            if attack[TOON_TRACK_COL] == NPCSOS:
                npc_damage = atk_hp
            if self.battle_calculator.CLEAR_MULTIPLE_TRAPS:
                if self.battle_calculator.getSuitTrapType(target_id) != NO_TRAP:
                    self._clear_attack(toon_id)
                    return
            if atk_level == UBER_GAG_LEVEL_INDEX:
                self.battle_calculator._BattleCalculatorAI__addSuitGroupTrap(target_id, atk_level, toon_id, target_list, npc_damage)
                if self._suit_is_lured(target_id):
                    self.notify.debug('Train Trap on lured suit %d, indicating with KBBONUS_COL flag' % target_id)
                    # Make sure we don't go out of bounds
                    if target_list[curr_target] in self.battle.activeSuits:
                        tgt_pos = self.battle.activeSuits.index(target_list[curr_target])
                        if tgt_pos < len(attack[TOON_KBBONUS_COL]):
                            attack[TOON_KBBONUS_COL][tgt_pos] = self.battle_calculator.KBBONUS_LURED_FLAG
            else:
                self.battle_calculator._BattleCalculatorAI__addSuitTrap(target_id, atk_level, toon_id, npc_damage)