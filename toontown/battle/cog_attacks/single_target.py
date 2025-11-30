"""
Single Target Cog Attack Calculator

Handles all single-target cog attacks that affect only one toon at a time.
"""

from . import BaseCogAttackCalculator
from ..BattleBase import *
from ..SuitBattleGlobals import *
import random

class SingleTargetAttackCalculator(BaseCogAttackCalculator):
    """Calculator for single-target cog attacks"""
    
    def get_attack_name(self):
        return "SingleTarget"
    
    def calculate_attack_type(self, attack_index):
        """
        Calculate which attack type the cog should use
        """
        the_suit = self._get_suit(attack_index)
        attacks = SuitAttributes[the_suit.dna.name]['attacks']
        attack_type = pickSuitAttack(attacks, the_suit.getLevel())
        return attack_type
    
    def calculate_target(self, attack_index):
        """
        Calculate which toon the cog should target for single-target attack
        """
        attack = self._get_attack_data(attack_index)
        suit_id = attack[SUIT_ID_COL]
        
        # Use targeting logic based on who attacked this suit
        if suit_id in self.battle_calculator.SuitAttackers and random.randint(0, 99) < 75:
            total_damage = 0
            for curr_toon in list(self.battle_calculator.SuitAttackers[suit_id].keys()):
                total_damage += self.battle_calculator.SuitAttackers[suit_id][curr_toon]
            
            if total_damage > 0:
                dmgs = []
                for curr_toon in list(self.battle_calculator.SuitAttackers[suit_id].keys()):
                    dmgs.append(self.battle_calculator.SuitAttackers[suit_id][curr_toon] / total_damage * 100)
                
                dmg_idx = pickFromFreqList(dmgs)
                if dmg_idx is None:
                    toon_id = self._pick_random_toon(suit_id)
                else:
                    toon_id = list(self.battle_calculator.SuitAttackers[suit_id].keys())[dmg_idx]
                
                if toon_id == -1 or toon_id not in self.battle.activeToons:
                    return -1
                    
                if self.notify.getDebug():
                    self.notify.debug(f'Suit attacking back at toon {toon_id}')
                return self.battle.activeToons.index(toon_id)
        
        # Fallback to random target
        targetToon = self._pick_random_toon(suit_id)
        return targetToon
    
    def calculate_hit(self, attack_index):
        """
        Calculate if the single-target attack hits
        """
        if self.battle_calculator.suitsAlwaysHit:
            return 1
        elif self.battle_calculator.suitsAlwaysMiss:
            if random.randint(1, 100) >= 75:
                return 1
            else:
                return 0
        
        the_suit = self._get_suit(attack_index)
        attack_type = self._get_attack_data(attack_index)[SUIT_ATK_COL]
        attack_info = getSuitAttack(the_suit.dna.name, the_suit.getLevel(), attack_type)
        attack_acc = attack_info['acc']
        
        # For single target attacks, use attack accuracy directly
        accuracy = attack_acc
        rand_choice = random.randint(0, 99)
        
        if self.notify.getDebug():
            self.notify.debug(f'Single-target suit attack rolled {rand_choice} to hit with accuracy {accuracy}')
        
        return 1 if rand_choice < accuracy else 0
    
    def affects_group(self, attack):
        """
        Single target attacks never affect groups
        """
        return False
    
    def create_target_list(self, attack_index):
        """
        Create target list for single-target attack
        """
        attack = self._get_attack_data(attack_index)
        target_list = []
        
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            if self.notify.getDebug():
                self.notify.debug('No attack, no targets')
            return target_list
        
        # Single target - only add the targeted toon
        target_index = attack[SUIT_TGT_COL]
        if target_index >= 0 and target_index < len(self.battle.activeToons):
            target_toon = self.battle.activeToons[target_index]
            target_list.append(target_toon)
            
            if self.notify.getDebug():
                self.notify.debug(f'Single-target suit attack will target toon {target_toon}')
        
        return target_list
    
    def calculate_damage(self, attack_index):
        """
        Calculate damage for single-target attack
        """
        target_list = self.create_target_list(attack_index)
        attack = self._get_attack_data(attack_index)
        
        for curr_target in range(len(target_list)):
            toon_id = target_list[curr_target]
            toon = self.battle.getToon(toon_id)
            result = 0
            
            # Check various damage immunity conditions
            if toon and toon.immortalMode:
                result = 1
            elif self.battle_calculator.TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif self.calculate_hit(attack_index):
                # Attack hits - calculate actual damage
                attack_type = attack[SUIT_ATK_COL]
                the_suit = self.battle.findSuit(attack[SUIT_ID_COL])
                attack_info = getSuitAttack(the_suit.dna.name, the_suit.getLevel(), attack_type)
                result = attack_info['hp']
                
                if self.notify.getDebug():
                    self.notify.debug(f'Single-target attack hits for {result} damage')
            
            # Set damage in attack data
            target_index = self.battle.activeToons.index(toon_id)
            attack[SUIT_HP_COL][target_index] = result