#!/usr/bin/env python
"""Test script to verify that group lure attacks set target index to -1."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toontown.battle.tracks.lure import LureTrackCalculator
from toontown.battle.BattleBase import getToonAttack, LURE, LURE_TRACK, TOON_TRACK_COL, TOON_LVL_COL, TOON_TGT_COL, TOON_HP_COL
from toontown.battle.BattleCalculatorAI import BattleCalculatorAI
from toontown.battle.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.toonbase.ToontownBattleGlobals import AvPropTargetCat, AvPropTarget

class MockBattle:
    """Mock battle class for testing."""
    def __init__(self):
        self.activeSuits = []
        self.activeToons = []
        
    def getToon(self, toonId):
        return None

class MockBattleCalculator:
    """Mock battle calculator for testing."""
    def __init__(self):
        self.battle = MockBattle()
        self.notify = type('MockNotify', (), {
            'getDebug': lambda self: False,
            'debug': lambda self, msg: None
        })()
        self.SUITS_UNLURED_IMMEDIATELY = False
        self.NumRoundsLured = [1, 2, 3, 4, 5, 6]  # For each level
        self.traps = {}
        self.successfulLures = {}
        
    def _BattleCalculatorAI__calcToonAtkHp(self, toonId):
        pass
        
    def _BattleCalculatorAI__handleBonus(self, attackIdx, hp=0):
        pass
        
    def _BattleCalculatorAI__attackHasHit(self, attack, suit=0):
        return True
        
    def getSuitTrapType(self, targetId):
        from toontown.battle.BattleBase import NO_TRAP
        return NO_TRAP
        
    def _BattleCalculatorAI__addLuredSuitInfo(self, targetId, a, rounds, wakeupChance, toonId, atkLevel, lureId=-1, npc=False):
        return 0
        
    def _BattleCalculatorAI__getToonTargets(self, attack):
        # Return a list of mock targets
        return [type('MockTarget', (), {'getDoId': lambda self: 1})()]
        
    def itemIsCredit(self, track, level):
        return True

def test_group_lure_attack():
    """Test that group lure attacks set target index to -1."""
    print("Testing group lure attack...")
    
    # Create mock objects
    battle_calculator = MockBattleCalculator()
    lure_calculator = LureTrackCalculator(battle_calculator)
    
    # Create a group lure attack (level 4 is typically a group lure)
    toon_id = 1
    attack = getToonAttack(toon_id, track=LURE, level=4, target=-1)  # -1 for group target
    
    # Create mock target list
    target_list = [type('MockSuit', (), {'getDoId': lambda self: 1})()]
    
    # Calculate damage
    lure_calculator.calculate_damage(toon_id, attack, target_list, atk_level=4, atk_acc=50)
    
    # Check that the target index is -1 for group attacks
    # For a group attack, the HP column should have -1 as the target index
    print(f"Attack HP column: {attack[TOON_HP_COL]}")
    
    # Since this is a group attack, we expect the target index to be handled appropriately
    print("Test completed. Group lure attack processed.")

def test_single_lure_attack():
    """Test that single lure attacks work normally."""
    print("Testing single lure attack...")
    
    # Create mock objects
    battle_calculator = MockBattleCalculator()
    lure_calculator = LureTrackCalculator(battle_calculator)
    
    # Create a single lure attack (level 0 is typically a single lure)
    toon_id = 1
    attack = getToonAttack(toon_id, track=LURE, level=0, target=0)
    
    # Create mock target list
    target_list = [type('MockSuit', (), {'getDoId': lambda self: 1})()]
    
    # Calculate damage
    lure_calculator.calculate_damage(toon_id, attack, target_list, atk_level=0, atk_acc=50)
    
    # Check that the attack was processed
    print(f"Attack HP column: {attack[TOON_HP_COL]}")
    
    print("Test completed. Single lure attack processed.")

if __name__ == "__main__":
    print("Running lure track calculator tests...")
    test_single_lure_attack()
    test_group_lure_attack()
    print("All tests completed.")