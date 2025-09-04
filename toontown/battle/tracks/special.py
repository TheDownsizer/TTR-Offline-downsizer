"""
Special Track Calculator

Handles special attack types like FIRE, PETSOS, and NPCSOS.
"""

from . import BaseTrackCalculator
from ..BattleBase import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.pets import PetTricks, DistributedPetProxyAI
from direct.showbase.PythonUtil import lerp
import random

class SpecialTrackCalculator(BaseTrackCalculator):
    """Calculator for special track attacks (FIRE, PETSOS, NPCSOS)"""
    
    def get_track_name(self):
        return "Special"
    
    def calculate_hit(self, attack_index, attack_targets):
        """
        Calculate if special attack hits
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel = self._get_actual_track_level(attack)
        
        if atkTrack == NPCSOS:
            return (1, 95)
        elif atkTrack == FIRE:
            return (1, 95)
        elif atkTrack == PETSOS:
            return self._calculate_pet_trick_success(attack)
        else:
            # Fallback for unknown special tracks
            return (0, 0)
    
    def calculate_damage(self, attack_index, attack_targets):
        """
        Calculate damage and effects for special attacks
        """
        attack = self._get_attack_data(attack_index)
        atkTrack, atkLevel, atkHp = self._get_actual_track_level_hp(attack)
        
        if atkTrack == FIRE:
            self._calculate_fire_damage(attack, attack_targets)
        elif atkTrack == PETSOS:
            self._calculate_pet_healing(attack, attack_targets)
        elif atkTrack == NPCSOS:
            # NPCSOS damage is handled by the specific track it represents
            pass
    
    def _calculate_fire_damage(self, attack, attack_targets):
        """
        Calculate fire attack damage (instant kill)
        """
        valid_target_available = False
        
        for target_idx, target in enumerate(attack_targets):
            target_id = target.getDoId()
            
            if self._combatant_dead(target_id, toon=False):
                continue
            
            valid_target_available = True
            
            # Fire attack handling
            toon = self.battle.getToon(attack[TOON_ID_COL])
            suit = self.battle.findSuit(target_id)
            
            if suit:
                cost_to_fire = 1
                ability_to_fire = toon.getPinkSlips()
                num_left = ability_to_fire - cost_to_fire
                if num_left < 0:
                    num_left = 0
                toon.b_setPinkSlips(num_left)
                
                if cost_to_fire > ability_to_fire:
                    # Log suspicious activity
                    import simbase
                    simbase.air.writeServerEvent('suspicious', 
                                                avId=attack[TOON_ID_COL], 
                                                issue=f'Toon attempting to fire a {cost_to_fire} cost cog with {ability_to_fire} pinkslips')
                    print('Not enough PinkSlips to fire cog - print a warning here')
                    attack_damage = 0
                else:
                    # Instant kill - reset skele revives and deal full HP damage
                    suit.skeleRevives = 0
                    attack_damage = suit.getHP()
            else:
                attack_damage = 0
            
            # Set damage in attack
            targets = self._get_suit_targets(attack)
            if target in targets:
                target_index = targets.index(target)
                attack[TOON_HP_COL][target_index] = attack_damage
                
                if self.notify.getDebug():
                    self.notify.debug(f'Fire does {attack_damage} damage to suit (instant kill)')
        
        # Clear attack if no valid targets
        if not valid_target_available and self._prev_atk_track(attack[TOON_ID_COL]) != FIRE:
            self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _calculate_pet_healing(self, attack, attack_targets):
        """
        Calculate pet trick healing
        """
        valid_target_available = False
        
        # Get pet trick info
        pet_proxy_id = attack[TOON_TGT_COL]
        trick_id = attack[TOON_LVL_COL]
        
        # Calculate healing based on pet aptitude
        heal_range = PetTricks.TrickHeals[trick_id]
        hp = 0
        
        import simbase
        if pet_proxy_id in simbase.air.doId2do:
            pet_proxy = simbase.air.doId2do[pet_proxy_id]
            if trick_id < len(pet_proxy.trickAptitudes):
                aptitude = pet_proxy.trickAptitudes[trick_id]
                hp = int(lerp(heal_range[0], heal_range[1], aptitude))
        else:
            if self.notify.getDebug():
                self.notify.debug(f'pet proxy: {pet_proxy_id} not in doId2do!')
        
        # Apply healing to all toon targets
        for target_idx, target_id in enumerate(attack_targets):
            if self._combatant_dead(target_id, toon=True):
                continue
            
            valid_target_available = True
            
            # Set healing in attack
            targets = self._get_toon_targets(attack)
            if target_id in targets:
                target_index = targets.index(target_id)
                attack[TOON_HP_COL][target_index] = hp
                
                if self.notify.getDebug():
                    self.notify.debug(f'Pet trick heals {hp} to toon')
        
        # Clear attack if no valid targets
        if not valid_target_available and self._prev_atk_track(attack[TOON_ID_COL]) != PETSOS:
            self.battle_calculator._BattleCalculatorAI__clearAttack(attack[TOON_ID_COL])
    
    def _calculate_pet_trick_success(self, attack):
        """
        Calculate if pet trick succeeds
        """
        pet_proxy_id = attack[TOON_TGT_COL]
        
        import simbase
        if pet_proxy_id not in simbase.air.doId2do:
            if self.notify.getDebug():
                self.notify.debug(f'pet proxy {pet_proxy_id} not in doId2do!')
            attack[TOON_ACCBONUS_COL] = 1
            return (0, 0)
        
        pet_proxy = simbase.air.doId2do[pet_proxy_id]
        trick_id = attack[TOON_LVL_COL]
        
        # Use pet proxy's attemptBattleTrick method
        attack[TOON_ACCBONUS_COL] = pet_proxy.attemptBattleTrick(trick_id)
        
        if attack[TOON_ACCBONUS_COL] == 1:
            return (0, 0)
        else:
            return (1, 100)
    
    def _get_suit_targets(self, attack):
        """Helper to get suit targets"""
        return self.battle.activeSuits
    
    def _get_toon_targets(self, attack):
        """Helper to get toon targets"""
        return self.battle.activeToons
    
    def _prev_atk_track(self, attacker_id):
        """Helper to get previous attack track"""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon=1)