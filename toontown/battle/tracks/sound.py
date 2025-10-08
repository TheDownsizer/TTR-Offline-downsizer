"""Sound track calculator."""

from .base import TrackCalculatorBase
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.cog_attacks import supervisor_rules
from toontown.battle.BattleBase import *

class SoundTrackCalculator(TrackCalculatorBase):
    """Calculator for Sound gag track."""
    
    def calculate_attack(self, toon_id, attack):
        """Calculate sound gag attack."""
        self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level):
        """Calculate sound gag attack damage."""
        valid_target_avail = 0
        toon = self._get_toon(toon_id)
        
        got_bonus = 0

        for curr_target in range(len(target_list)):
            target_id = target_list[curr_target].getDoId()
            
            # Check for lured suit sound flag
            if self._suit_is_lured(target_id):
                self.notify.debug('Sound on lured suit, ' + 'indicating with KBBONUS_COL flag')
                # Make sure we don't go out of bounds
                if target_list[curr_target] in self.battle.activeSuits:
                    tgt_pos = self.battle.activeSuits.index(target_list[curr_target])
                    if tgt_pos < len(attack[TOON_KBBONUS_COL]):
                        attack[TOON_KBBONUS_COL][tgt_pos] = self.battle_calculator.KBBONUS_LURED_FLAG
            
            # Calculate sound damage
            organic_bonus = self._check_gag_bonus(toon, SOUND, atk_level)
            prop_bonus = self._check_prop_bonus(SOUND)
            attack_damage = self._get_av_prop_damage(SOUND, atk_level, toon.experience.getExp(SOUND), organic_bonus, prop_bonus, self.battle_calculator.propAndOrganicBonusStack)
            
            if not self._combatant_dead(target_id, toon=0):
                valid_target_avail = 1
            
            result = attack_damage
            if self.notify.getDebug():
                self.notify.debug('toon does ' + str(result) + ' damage to suit')
            
            # Apply damage
            targets = self._get_toon_targets(attack)
            if target_list[curr_target] in targets:
                target_index = targets.index(target_list[curr_target])
                # Make sure we don't go out of bounds
                if target_index < len(self.battle.activeSuits):
                    currSuitTarget = self.battle.activeSuits[target_index]
                    if currSuitTarget.dna.name == 'ofc':
                        clerkRules = supervisor_rules.OfficeClerk()
                        if currSuitTarget.getActualLevel() == 32:
                            self.battle.battleCalc.clerkSoundedResponse([toon.doId, int(attack_damage * clerkRules.SHHH_SOUND_PERCENTS[0])])
                        else:
                            self.battle.battleCalc.clerkSoundedResponse([toon.doId, int(attack_damage * clerkRules.SHHH_SOUND_PERCENTS[1])])
                attack[TOON_HP_COL][target_index] = result
                
                # Handle lure experience
                if result > 0:
                    lure_infos = self._get_lured_exp_info(target_id)
                    for curr_info in lure_infos:
                        if curr_info[3]:
                            self.notify.debug('Giving lure EXP to toon ' + str(curr_info[0]))
                            self._add_attack_exp(attack, track=LURE, level=curr_info[1], attacker_id=curr_info[0])
                        self._clear_lurer(curr_info[0], lure_id=curr_info[2])
            
            if not got_bonus:
                got_bonus = 1
        
        # Clear attack if no valid targets
        if not valid_target_avail and self._prev_atk_track(toon_id) != SOUND:
            self._clear_attack(toon_id)
    
    def create_target_list(self, attack_index, attack):
        """Create target list for sound attack."""
        # Use the base implementation for sound attacks
        return super().create_target_list(attack_index, attack)
    
    def is_unlure_attack(self, attack_index, attack):
        """Sound attacks unlure lured suits."""
        return True