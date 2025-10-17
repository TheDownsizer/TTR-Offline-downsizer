"""Heal track calculator."""

from .base import TrackCalculatorBase
from toontown.battle.BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *

class HealTrackCalculator(TrackCalculatorBase):
    """Calculator for Heal gag track."""
    
    def calculate_attack(self, toon_id, attack):
        """Calculate heal gag attack."""
        self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level):
        """Calculate heal gag attack damage."""
        valid_target_avail = 1  # Heal always has valid targets
        toon = self._get_toon(toon_id)
        
        for curr_target in range(len(target_list)):
            target_id = target_list[curr_target]  # For heal, this is toon ID directly
            
            # Calculate heal amount
            organic_bonus = self._check_gag_bonus(toon, HEAL, atk_level)
            prop_bonus = self._check_prop_bonus(HEAL)
            heal_amount = self._get_av_prop_damage(HEAL, atk_level, toon.experience.getExp(HEAL), organic_bonus, prop_bonus, self.battle_calculator.propAndOrganicBonusStack)
            
            # Reduce heal if attack missed
            result = heal_amount
            if not self._attack_has_hit(attack, suit=0):
                result = result * 0.2
            if self.notify.getDebug():
                self.notify.debug('toon does ' + str(result) + ' healing to toon(s)')
            
            # Split heal among targets
            result = result / len(target_list)
            if self.notify.getDebug():
                self.notify.debug('Splitting heal among ' + str(len(target_list)) + ' targets')
            
            # Apply heal
            targets = self._get_toon_targets(attack)
            if target_list[curr_target] in targets:
                target_index = targets.index(target_list[curr_target])
                attack[TOON_HP_COL][target_index] = result