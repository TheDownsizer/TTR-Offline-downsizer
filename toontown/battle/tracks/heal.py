"""
Heal Track Calculator

Handles all heal (Toon-Up) gag calculations including accuracy and healing amounts.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
import random

class HealTrackCalculator(BaseTrackCalculator):
    """Calculator for Heal/Toon-Up track attacks"""
    
    def get_track_name(self):
        return "Heal"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if heal attack hits
        Heal attacks always hit, but accuracy affects healing effectiveness
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
        
        # Heal attacks always hit
        attack[TOON_ACCBONUS_COL] = 0
        return (1, 100)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate healing amount for heal attacks
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel, atkHp = self._get_actual_track_level_hp(attack)
        
        valid_target_available = False
        
        for target_idx, target_id in enumerate(attack_targets):
            if self._combatant_dead(target_id, toon=True):
                continue
                
            valid_target_available = True
            
            # Calculate healing amount
            toon = self.battle.getToon(attack[TOON_ID_COL])
            if attack[TOON_TRACK_COL] == NPCSOS:
                healing_amount = atkHp
            else:
                organic_bonus = self._toon_check_gag_bonus(attack[TOON_ID_COL], HEAL, atkLevel)
                prop_bonus = self._check_prop_bonus(HEAL)
                healing_amount = getAvPropDamage(HEAL, atkLevel, toon.experience.getExp(HEAL), 
                                               organic_bonus, prop_bonus, 
                                               self.battle_calculator.propAndOrganicBonusStack)
            
            # Apply accuracy modifier to healing
            if not self._attack_has_hit(attack):
                healing_amount = healing_amount * 0.2
            
            if self.notify.getDebug():
                self.notify.debug(f'Heal does {healing_amount} healing to toon(s)')
            
            # Split healing among targets
            healing_per_target = healing_amount / len(attack_targets)
            
            # Find target index in battle
            targets = self._get_toon_targets(attack)
            if target_id in targets:
                target_index = targets.index(target_id)
                attack[TOON_HP_COL][target_index] = healing_per_target
                
                if self.notify.getDebug():
                    self.notify.debug(f'Splitting heal among {len(attack_targets)} targets')
        
        # Clear attack if no valid targets
        if not valid_target_available:
            prev_track = self._prev_atk_track(attack[TOON_ID_COL])
            if prev_track != HEAL:
                self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _attack_has_hit(self, attack):
        """Helper to check if attack has hit"""
        return not attack[TOON_ACCBONUS_COL] and self._get_actual_track_level(attack)[0] != NO_ATTACK
    
    def _get_toon_targets(self, attack):
        """Helper to get toon targets"""
        return self.battle.activeToons
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)