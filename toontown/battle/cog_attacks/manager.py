"""
Cog Attack Calculator Manager

Manages and coordinates all cog attack calculators for battle calculations.
"""

from .single_target import SingleTargetAttackCalculator
from .group_target import GroupTargetAttackCalculator
from .special import SpecialAttackCalculator
from . import CogAttackCalculatorError
from ..BattleBase import *
from ..SuitBattleGlobals import *

class CogAttackCalculatorManager:
    """
    Manages all cog attack calculators and routes attacks to appropriate handlers
    """
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.notify = battle_calculator.notify
        
        # Initialize all attack calculators
        self.single_target_calculator = SingleTargetAttackCalculator(battle_calculator)
        self.group_target_calculator = GroupTargetAttackCalculator(battle_calculator)
        self.special_calculator = SpecialAttackCalculator(battle_calculator)
    
    def can_suit_attack(self, suit_id):
        """
        Check if a suit can attack (not dead, lured, or just revived)
        """
        return self.battle_calculator._BattleCalculatorAI__suitCanAttack(suit_id)
    
    def calculate_suit_attack_type(self, attack_index):
        """
        Calculate which attack type a suit should use
        """
        attack = self.battle.suitAttacks[attack_index]
        calculator = self._get_calculator_for_attack(attack_index)
        return calculator.calculate_attack_type(attack_index)
    
    def calculate_suit_target(self, attack_index):
        """
        Calculate which target(s) a suit should attack
        """
        attack = self.battle.suitAttacks[attack_index]
        calculator = self._get_calculator_for_attack(attack_index)
        return calculator.calculate_target(attack_index)
    
    def suit_attack_hits(self, attack_index):
        """
        Calculate if a suit attack hits its target(s)
        """
        attack = self.battle.suitAttacks[attack_index]
        calculator = self._get_calculator_for_attack(attack_index)
        return calculator.calculate_hit(attack_index)
    
    def suit_attack_affects_group(self, attack):
        """
        Check if a suit attack affects group or single target
        """
        # Determine attack type from attack data
        attack_type = attack[SUIT_ATK_COL]
        if attack_type == NO_ATTACK:
            return False
        
        suit_id = attack[SUIT_ID_COL]
        the_suit = self.battle.findSuit(suit_id)
        if the_suit is None:
            return False
        
        attack_info = getSuitAttack(the_suit.dna.name, the_suit.getLevel(), attack_type)
        return attack_info['group'] != ATK_TGT_SINGLE
    
    def create_suit_target_list(self, attack_index):
        """
        Create list of targets for suit attack
        """
        attack = self.battle.suitAttacks[attack_index]
        calculator = self._get_calculator_for_attack(attack_index)
        return calculator.create_target_list(attack_index)
    
    def calculate_suit_attack_damage(self, attack_index):
        """
        Calculate damage for suit attack
        """
        attack = self.battle.suitAttacks[attack_index]
        calculator = self._get_calculator_for_attack(attack_index)
        calculator.calculate_damage(attack_index)
    
    def apply_suit_attack_damages(self, attack_index):
        """
        Apply calculated damage to toons
        """
        attack = self.battle.suitAttacks[attack_index]
        if self.battle_calculator.APPLY_HEALTH_ADJUSTMENTS:
            for t in self.battle.activeToons:
                position = self.battle.activeToons.index(t)
                if attack[SUIT_HP_COL][position] <= 0:
                    continue
                
                toon_hp = self.battle_calculator._BattleCalculatorAI__getToonHp(t)
                damage = attack[SUIT_HP_COL][position]
                
                if toon_hp - damage <= 0:
                    if self.notify.getDebug():
                        self.notify.debug(f'Toon {t} has died, removing')
                    self.battle_calculator.toonLeftBattle(t)
                    attack[TOON_DIED_COL] = attack[TOON_DIED_COL] | 1 << position
                
                if self.notify.getDebug():
                    self.notify.debug(f'Toon {t} takes {damage} damage')
                
                self.battle_calculator.toonHPAdjusts[t] -= damage
                if self.notify.getDebug():
                    new_hp = self.battle_calculator._BattleCalculatorAI__getToonHp(t)
                    self.notify.debug(f'Toon {t} now has {new_hp} health')
    
    def update_suit_attack_stats(self, attack_index):
        """
        Update attack statistics for suit attacks
        """
        attack = self.battle.suitAttacks[attack_index]
        
        if attack[SUIT_ATK_COL] != NO_ATTACK:
            if self.suit_attack_affects_group(attack):
                # Group attack - update stats for all toons
                for curr_tgt in self.battle.activeToons:
                    self.battle_calculator._BattleCalculatorAI__updateSuitAtkStat(curr_tgt)
            else:
                # Single attack - update stats for targeted toon
                target_index = attack[SUIT_TGT_COL]
                if target_index >= 0 and target_index < len(self.battle.activeToons):
                    tgt_id = self.battle.activeToons[target_index]
                    self.battle_calculator._BattleCalculatorAI__updateSuitAtkStat(tgt_id)
    
    def _get_calculator_for_attack(self, attack_index):
        """
        Get the appropriate calculator for an attack based on the suit's attack selection
        """
        attack = self.battle.suitAttacks[attack_index]
        
        # Get suit and determine what attack it will perform
        suit_id = attack[SUIT_ID_COL]
        the_suit = self.battle.findSuit(suit_id)
        if the_suit is None:
            return self.single_target_calculator
        
        # Determine attack type using same logic as calculators
        attacks = SuitAttributes[the_suit.dna.name]['attacks']
        attack_type_index = pickSuitAttack(attacks, the_suit.getLevel())
        
        if attack_type_index is None or attack_type_index >= len(attacks):
            return self.single_target_calculator
        
        # Get the attack info
        attack_name = attacks[attack_type_index][0]
        if attack_name in SuitAttacks:
            attack_info = SuitAttacks[attack_name]
            if attack_info[1] == ATK_TGT_GROUP:
                if self.notify.getDebug():
                    self.notify.debug(f'Routing to group calculator for attack: {attack_name}')
                return self.group_target_calculator
        
        # Default to single target calculator
        if self.notify.getDebug():
            self.notify.debug(f'Routing to single target calculator for attack: {attack_name if attack_name in SuitAttacks else "unknown"}')
        return self.single_target_calculator
    
    def _is_special_attack(self, attack_index):
        """
        Determine if an attack requires special handling
        Future: Add logic to identify special attacks that need unique mechanics
        """
        # For now, all attacks use standard logic
        # Future: Check attack type and route special attacks appropriately
        return False
    
    def calculate_full_suit_attacks(self):
        """
        Calculate all suit attacks for the current round
        """
        for i in range(len(self.battle.suitAttacks)):
            if i < len(self.battle.activeSuits):
                suit_id = self.battle.activeSuits[i].doId
                self.battle.suitAttacks[i][SUIT_ID_COL] = suit_id
                
                # Check if suit can attack (not dead, not lured, not just revived)
                if not self.can_suit_attack(suit_id):
                    if self.notify.getDebug():
                        self.notify.debug(f"Suit {suit_id} can't attack (dead, lured, or just revived)")
                    continue
                
                # Skip pending/joining suits
                if (self.battle.pendingSuits.count(self.battle.activeSuits[i]) > 0 or 
                    self.battle.joiningSuits.count(self.battle.activeSuits[i]) > 0):
                    continue
                
                attack = self.battle.suitAttacks[i]
                attack[SUIT_ID_COL] = self.battle.activeSuits[i].doId
                attack[SUIT_ATK_COL] = self.calculate_suit_attack_type(i)
                attack[SUIT_TGT_COL] = self.calculate_suit_target(i)
                
                self.calculate_suit_attack_damage(i)
                self.update_suit_attack_stats(i)
                
                # Check if all targets are dead
                targets = self.create_suit_target_list(i)
                all_targets_dead = True
                for curr_tgt in targets:
                    if self.battle_calculator._BattleCalculatorAI__getToonHp(curr_tgt) > 0:
                        all_targets_dead = False
                        break
                
                if all_targets_dead:
                    self.battle.suitAttacks[i] = getDefaultSuitAttack()
                    if self.notify.getDebug():
                        self.notify.debug('clearing suit attack, targets dead')
                        self.notify.debug('suit attack is now ' + repr(self.battle.suitAttacks[i]))
                        self.notify.debug('all attacks: ' + repr(self.battle.suitAttacks))
                    attack = self.battle.suitAttacks[i]
                
                # Apply damage if attack hit
                if self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=1):
                    self.apply_suit_attack_damages(i)
                
                if self.notify.getDebug():
                    self.notify.debug(f'Suit attack: {self.battle.suitAttacks[i]}')
    
    def get_all_calculators(self):
        """
        Get all attack calculators for debugging/inspection
        """
        return {
            'single_target': self.single_target_calculator,
            'group_target': self.group_target_calculator,
            'special': self.special_calculator
        }