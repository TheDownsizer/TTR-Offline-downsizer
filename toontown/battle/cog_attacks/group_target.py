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
        Calculate which attack type the cog should use - prefer group attacks
        """
        the_suit = self._get_suit(attack_index)
        attacks = SuitAttributes[the_suit.dna.name]['attacks']
        
        # Filter for group attacks first
        group_attacks = []
        single_attacks = []
        
        for i, attack_data in enumerate(attacks):
            attack_name = attack_data[0]
            if attack_name in SuitAttacks:
                attack_info = SuitAttacks[attack_name]
                if attack_info[1] == ATK_TGT_GROUP:
                    group_attacks.append(i)
                else:
                    single_attacks.append(i)
        
        # Prefer group attacks when available
        if group_attacks:
            if self.notify.getDebug():
                self.notify.debug(f'Group calculator: selecting from {len(group_attacks)} group attacks')
            # Use weighted selection among group attacks
            attack_type = self._pick_weighted_attack(attacks, group_attacks, the_suit.getLevel())
        else:
            if self.notify.getDebug():
                self.notify.debug('Group calculator: no group attacks available, using any attack')
            # Fall back to any attack if no group attacks
            attack_type = pickSuitAttack(attacks, the_suit.getLevel())
        
        return attack_type
    
    def calculate_target(self, attack_index):
        """
        For group attacks, target selection is not used as it affects all toons
        Returns -1 to indicate group targeting
        """
        if self.notify.getDebug():
            self.notify.debug('Group attack calculator: returning -1 for group targeting')
        
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
        if self.notify.getDebug():
            self.notify.debug('Group attack calculator: calculating damage for all active toons')
        
        target_list = self.create_target_list(attack_index)
        attack = self._get_attack_data(attack_index)
        
        # Check if attack hits (same roll for all targets in group attack)
        attack_hits = self.calculate_hit(attack_index)

        attack[SUIT_TGT_COL] = -1
        
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
    
    def _pick_weighted_attack(self, attacks, attack_indices, suit_level):
        """
        Pick an attack from specified indices using weighted selection
        """
        if not attack_indices:
            return None
        
        # Create weighted list based on attack probabilities
        total_weight = 0
        for idx in attack_indices:
            total_weight += attacks[idx][3][suit_level]
        
        if total_weight == 0:
            # If no weights, pick randomly
            return random.choice(attack_indices)
        
        # Weighted selection
        randNum = random.randint(0, total_weight - 1)
        current_weight = 0
        
        for idx in attack_indices:
            current_weight += attacks[idx][3][suit_level]
            if randNum < current_weight:
                return idx
        
        # Fallback
        return attack_indices[0]