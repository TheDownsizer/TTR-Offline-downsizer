"""Base class for all gag track calculators."""

from toontown.toonbase.ToontownBattleGlobals import *
from toontown.suit import DistributedSuitBaseAI
from toontown.battle.BattleBase import *
import random

class TrackCalculatorBase:
    """Base class for all gag track calculators."""
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.battle = battle_calculator.battle
        self.notify = battle_calculator.notify
    
    def calculate_attack(self, toon_id, attack):
        """Calculate the attack for this track.
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement calculate_attack method")
    
    def calculate_damage(self, toon_id, attack, target_list, atk_level):
        """Calculate damage for this track.
        
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement calculate_damage method")
    
    def create_target_list(self, attack_index, attack):
        """Create target list for this track.
        
        This method can be overridden by subclasses.
        """
        # Default implementation - can be overridden by specific track calculators
        atk_track, atk_level = self.battle_calculator._BattleCalculatorAI__getActualTrackLevel(attack)
        target_list = []
        
        if atk_track == NPCSOS:
            return target_list
        if not attackAffectsGroup(atk_track, atk_level, attack[TOON_TRACK_COL]):
            if atk_track == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle.findSuit(attack[TOON_TGT_COL])
            if target is not None:
                target_list.append(target)
        elif atk_track == HEAL or atk_track == PETSOS:
            if attack[TOON_TRACK_COL] == NPCSOS or atk_track == PETSOS:
                target_list = self.battle.activeToons
            else:
                for curr_toon in self.battle.activeToons:
                    if attack[TOON_ID_COL] != curr_toon:
                        target_list.append(curr_toon)
        else:
            target_list = self.battle.activeSuits
        return target_list
    
    def is_unlure_attack(self, attack_index, attack):
        """Check if this attack unlures suits.
        
        This method can be overridden by subclasses.
        """
        # Default implementation - can be overridden by specific track calculators
        track = self.battle_calculator._BattleCalculatorAI__getActualTrack(attack)
        if track == THROW or track == SQUIRT or track == SOUND:
            return True
        return False
    
    # Helper methods that can be used by all track calculators
    def _get_toon(self, toon_id):
        """Get the toon object from the battle."""
        return self.battle.getToon(toon_id)
    
    def _check_gag_bonus(self, toon, track, level):
        """Check if the toon has a gag bonus for this track and level."""
        return toon.checkGagBonus(track, level)
    
    def _check_prop_bonus(self, track):
        """Check if there's a prop bonus for this track."""
        return self.battle_calculator._BattleCalculatorAI__checkPropBonus(track)
    
    def _get_av_prop_damage(self, track, level, exp, organic_bonus, prop_bonus, prop_and_organic_bonus_stack):
        """Get the damage for a gag."""
        return getAvPropDamage(track, level, exp, organic_bonus, prop_bonus, prop_and_organic_bonus_stack)
    
    def _combatant_dead(self, av_id, toon):
        """Check if a combatant is dead."""
        return self.battle_calculator._BattleCalculatorAI__combatantDead(av_id, toon)
    
    def _attack_has_hit(self, attack, suit=0):
        """Check if an attack has hit."""
        return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit)
    
    def _get_toon_targets(self, attack):
        """Get the targets for a toon attack."""
        return self.battle_calculator._BattleCalculatorAI__getToonTargets(attack)
    
    def _add_attack_exp(self, attack, track=-1, level=-1, attacker_id=-1):
        """Add experience for an attack."""
        self.battle_calculator._BattleCalculatorAI__addAttackExp(attack, track, level, attacker_id)
    
    def _get_lured_exp_info(self, target_id):
        """Get lure experience info for a target."""
        return self.battle_calculator._BattleCalculatorAI__getLuredExpInfo(target_id)
    
    def _clear_lurer(self, lurer_id, lure_id=-1):
        """Clear a lurer."""
        self.battle_calculator._BattleCalculatorAI__clearLurer(lurer_id, lure_id)
    
    def _suit_is_lured(self, suit_id, prev_round=0):
        """Check if a suit is lured."""
        return self.battle_calculator._BattleCalculatorAI__suitIsLured(suit_id, prev_round)
    
    def _accumulate_bounce_bonus(self, toon, attack_damage):
        """Accumulate bounce bonus for non-bounce attacks."""
        pass
    
    def _clear_attack(self, attack_idx, toon=1):
        """Clear an attack."""
        self.battle_calculator._BattleCalculatorAI__clearAttack(attack_idx, toon)
    
    def _prev_atk_track(self, attacker_id, toon=1):
        """Get the previous attack track."""
        return self.battle_calculator._BattleCalculatorAI__prevAtkTrack(attacker_id, toon)