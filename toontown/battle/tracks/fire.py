"""Fire track calculator."""

from .base import TrackCalculatorBase
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.BattleBase import *

class FireTrackCalculator(TrackCalculatorBase):
    """Calculator for Fire gag track."""
    
    def calculate_attack(self, toon_id, attack):
        """Calculate fire gag attack."""
        self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
        self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level):
        """Calculate fire gag attack damage."""
        valid_target_avail = 0
        toon = self._get_toon(toon_id)
        
        for curr_target in range(len(target_list)):
            target_id = target_list[curr_target].getDoId()
            suit = self.battle.findSuit(target_id)
            
            if suit:
                cost_to_fire = 1
                ability_to_fire = toon.getPinkSlips()
                toon.removePinkSlips(cost_to_fire)
                if cost_to_fire > ability_to_fire:
                    comment_str = 'Toon attempting to fire a %s cost cog with %s pinkslips' % (cost_to_fire, ability_to_fire)
                    simbase.air.writeServerEvent('suspicious', toon_id, comment_str)
                    disl_id = toon.DISLid
                    simbase.air.banManager.ban(toon_id, disl_id, comment_str)
                    print('Not enough PinkSlips to fire cog - print a warning here')
                    attack_damage = 0
                else:
                    suit.skeleRevives = 0
                    attack_damage = suit.getHP()
            else:
                attack_damage = 0
            
            if not self._combatant_dead(target_id, toon=0):
                valid_target_avail = 1
            
            result = attack_damage
            if self.notify.getDebug():
                self.notify.debug('toon does ' + str(result) + ' damage to suit')
            
            # Apply damage
            targets = self._get_toon_targets(attack)
            if target_list[curr_target] in targets:
                target_index = targets.index(target_list[curr_target])
                attack[TOON_HP_COL][target_index] = result
                
                # Handle lure experience
                if result > 0:
                    lure_infos = self._get_lured_exp_info(target_id)
                    for curr_info in lure_infos:
                        if curr_info[3]:
                            self.notify.debug('Giving lure EXP to toon ' + str(curr_info[0]))
                            self._add_attack_exp(attack, track=LURE, level=curr_info[1], attacker_id=curr_info[0])
                        self._clear_lurer(curr_info[0], lure_id=curr_info[2])
        
        # Clear attack if no valid targets
        if not valid_target_avail and self._prev_atk_track(toon_id) != FIRE:
            self._clear_attack(toon_id)