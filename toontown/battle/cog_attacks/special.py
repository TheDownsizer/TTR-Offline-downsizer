"""
Special Cog Attack Calculator

Handles special cog attacks that have unique mechanics or effects beyond
standard single/group targeting, such as status effects, special conditions,
or complex targeting rules.
"""

from . import BaseCogAttackCalculator
from ..BattleBase import *
from ..SuitBattleGlobals import *
import random

class SpecialAttackCalculator(BaseCogAttackCalculator):
    """Calculator for special effect cog attacks"""
    
    def get_attack_name(self):
        return "Special"
    
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
        Calculate targeting for special attacks
        May use custom logic depending on attack type
        """
        attack = self._get_attack_data(attack_index)
        suit_id = attack[SUIT_ID_COL]
        
        # For now, use standard targeting logic
        # Future: Add special targeting rules for specific attacks
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
                    self.notify.debug(f'Special attack targeting toon {toon_id}')
                return self.battle.activeToons.index(toon_id)
        
        return self._pick_random_toon(suit_id)
    
    def calculate_hit(self, attack_index):
        """
        Calculate if the special attack hits
        May include special accuracy rules
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
        
        # Special attacks may have modified accuracy
        accuracy = self._calculate_special_accuracy(attack_info, the_suit)
        rand_choice = random.randint(0, 99)
        
        if self.notify.getDebug():
            self.notify.debug(f'Special suit attack rolled {rand_choice} to hit with accuracy {accuracy}')
        
        return 1 if rand_choice < accuracy else 0
    
    def _calculate_special_accuracy(self, attack_info, suit):
        """
        Calculate special accuracy modifiers for certain attacks
        """
        # For now, use base accuracy
        # Future: Add special accuracy rules for specific attacks
        return attack_info['acc']
    
    def affects_group(self, attack):
        """
        Check if special attack affects group based on attack info
        """
        attack_type = attack[SUIT_ATK_COL]
        the_suit = self.battle.findSuit(attack[SUIT_ID_COL])
        attack_info = getSuitAttack(the_suit.dna.name, the_suit.getLevel(), attack_type)
        return attack_info['group'] != ATK_TGT_SINGLE
    
    def create_target_list(self, attack_index):
        """
        Create target list for special attack
        """
        attack = self._get_attack_data(attack_index)
        target_list = []
        
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            if self.notify.getDebug():
                self.notify.debug('No attack, no targets')
            return target_list
        
        # Determine targeting based on attack type
        if self.affects_group(attack):
            # Group attack - add all active toons
            for curr_toon in self.battle.activeToons:
                target_list.append(curr_toon)
                if self.notify.getDebug():
                    self.notify.debug(f'Special group attack will target toon {curr_toon}')
        else:
            # Single target attack
            target_index = attack[SUIT_TGT_COL]
            if target_index >= 0 and target_index < len(self.battle.activeToons):
                target_toon = self.battle.activeToons[target_index]
                target_list.append(target_toon)
                
                if self.notify.getDebug():
                    self.notify.debug(f'Special single attack will target toon {target_toon}')
        
        return target_list
    
    def calculate_damage(self, attack_index):
        """
        Calculate damage and apply special effects
        """
        target_list = self.create_target_list(attack_index)
        attack = self._get_attack_data(attack_index)
        
        # Check if attack hits
        attack_hits = self.calculate_hit(attack_index)
        
        # Apply damage to targets
        for target_toon_id in target_list:
            toon = self.battle.getToon(target_toon_id)
            result = 0
            
            # Check various damage immunity conditions
            if toon and toon.immortalMode:
                result = 1
            elif self.battle_calculator.TOONS_TAKE_NO_DAMAGE:
                result = 0
            elif attack_hits:
                # Attack hits - calculate actual damage
                attack_type = attack[SUIT_ATK_COL]
                the_suit = self.battle.findSuit(attack[SUIT_ID_COL])
                attack_info = getSuitAttack(the_suit.dna.name, the_suit.getLevel(), attack_type)
                
                # Apply special damage calculation
                result = self._calculate_special_damage(attack_info, the_suit, toon, target_toon_id)
                
                if self.notify.getDebug():
                    self.notify.debug(f'Special attack hits toon {target_toon_id} for {result} damage')
            
            # Set damage in attack data
            target_index = self.battle.activeToons.index(target_toon_id)
            attack[SUIT_HP_COL][target_index] = result
    
    def _calculate_special_damage(self, attack_info, suit, toon, toon_id):
        """
        Calculate special damage effects for certain attacks
        """
        # Base damage
        base_damage = attack_info['hp']
        
        # Future: Add special damage modifications based on attack type
        # For example:
        # - Status effect attacks
        # - Percentage-based damage
        # - Conditional damage modifiers
        
        return base_damage
    
    def apply_special_effects(self, attack_index):
        """
        Apply any special effects beyond damage
        """
        # Future: Implement special effects like:
        # - Status ailments
        # - Stat modifications
        # - Unique mechanics per attack type
        pass