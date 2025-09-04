"""
Group Target Cog Attack Calculator

Handles all group-target cog attacks that affect all active toons.
"""

from . import BaseCogAttackCalculator
from ..BattleBase import *
from ..SuitBattleGlobals import *
import random

class GroupTargetAttackCalculator(BaseCogAttackCalculator):
    """Calculator for group-target cog attacks"""
    
    def get_attack_name(self):
        return "GroupTarget"
    
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
        For group attacks, target selection is not used as it affects all toons
        Returns -1 to indicate group targeting
        """
        # Group attacks don't need specific targeting since they hit all toons
        # We return -1 as a convention for group attacks
        return -1
    
    def calculate_hit(self, attack_index):
        """
        Calculate if the group attack hits
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
        
        # For group attacks, use attack accuracy directly
        accuracy = attack_acc
        rand_choice = random.randint(0, 99)
        
        if self.notify.getDebug():
            self.notify.debug(f'Group suit attack rolled {rand_choice} to hit with accuracy {accuracy}')
        
        return 1 if rand_choice < accuracy else 0
    
    def affects_group(self, attack):
        """
        Group target attacks always affect groups
        """
        return True
    
    def create_target_list(self, attack_index):
        """
        Create target list for group attack - includes all active toons
        """
        attack = self._get_attack_data(attack_index)
        target_list = []
        
        if attack[SUIT_ATK_COL] == NO_ATTACK:
            if self.notify.getDebug():
                self.notify.debug('No attack, no targets')
            return target_list
        
        # Group attack - add all active toons
        for curr_toon in self.battle.activeToons:
            target_list.append(curr_toon)
            if self.notify.getDebug():
                self.notify.debug(f'Group suit attack will target toon {curr_toon}')
        
        return target_list
    
    def calculate_damage(self, attack_index):
        """
        Calculate damage for group attack - affects all toons
        """
        target_list = self.create_target_list(attack_index)
        attack = self._get_attack_data(attack_index)
        
        # Check if attack hits (same roll for all targets in group attack)
        attack_hits = self.calculate_hit(attack_index)
        
        # Calculate damage for each target
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
                result = attack_info['hp']
                
                if self.notify.getDebug():
                    self.notify.debug(f'Group attack hits toon {target_toon_id} for {result} damage')
            
            # Set damage in attack data for this target
            target_index = self.battle.activeToons.index(target_toon_id)
            attack[SUIT_HP_COL][target_index] = result
    
    def update_attack_stats(self, attack_index):
        """
        Update attack statistics for all targeted toons in group attack
        """
        target_list = self.create_target_list(attack_index)
        
        # Update stats for all toons hit by group attack
        for curr_tgt in target_list:
            self.battle_calculator._BattleCalculatorAI__updateSuitAtkStat(curr_tgt)