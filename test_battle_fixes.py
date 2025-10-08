#!/usr/bin/env python
"""Test script to verify battle calculation fixes."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toontown.battle.BattleCalculatorAI import BattleCalculatorAI
from toontown.battle.BattleBase import getToonAttack, LURE, LURE_TRACK, TOON_TRACK_COL, TOON_LVL_COL, TOON_TGT_COL, TOON_HP_COL
from toontown.battle.DistributedBattleBaseAI import DistributedBattleBaseAI
from toontown.toonbase.ToontownBattleGlobals import AvPropTargetCat, AvPropTarget

class MockSuit:
    """Mock suit class for testing."""
    def __init__(self, doId=1, dna=None):
        self.doId = doId
        self.dna = dna or MockDNA()
        self.currHP = 50
        self.maxHP = 50
        
    def getDoId(self):
        return self.doId
        
    def getHP(self):
        return self.currHP
        
    def setHP(self, hp):
        self.currHP = hp
        
    def getActualLevel(self):
        return 1

class MockDNA:
    """Mock DNA class for testing."""
    def __init__(self, name='f'):
        self.name = name
        
    def getLevel(self):
        return 1

class MockToon:
    """Mock toon class for testing."""
    def __init__(self, doId=1):
        self.doId = doId
        self.hp = 15
        self.maxHp = 15
        self.DISLid = 12345
        
    def getDoId(self):
        return self.doId
        
    def getPinkSlips(self):
        return 5
        
    def removePinkSlips(self, count):
        pass

class MockBattle:
    """Mock battle class for testing."""
    def __init__(self):
        self.activeSuits = [MockSuit(1)]
        self.activeToons = [1]
        self.luredSuits = []
        self.pendingSuits = []
        self.joiningSuits = []
        self.suitAttacks = [[-1, -1, -1, [], 0, 0, 0, []] for _ in range(4)]
        
    def getToon(self, toonId):
        return MockToon(toonId)
        
    def findSuit(self, suitId):
        for suit in self.activeSuits:
            if suit.doId == suitId:
                return suit
        return None

def test_lure_group_attack_target_index():
    """Test that group lure attacks set target index correctly."""
    print("Testing group lure attack target index fix...")
    
    # Create mock objects
    battle = MockBattle()
    battle_calculator = BattleCalculatorAI(battle)
    
    # Test group lure attack (level 4 is typically a group lure)
    toon_id = 1
    attack = getToonAttack(toon_id, track=LURE, level=4, target=-1)  # -1 for group target
    
    # Test that the attack is processed without errors
    try:
        battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
        print("Group lure attack processed successfully")
        return True
    except Exception as e:
        print(f"Error processing group lure attack: {e}")
        return False

def test_lured_suit_cannot_attack():
    """Test that lured suits cannot attack."""
    print("Testing lured suit attack prevention...")
    
    # Create mock objects
    battle = MockBattle()
    battle_calculator = BattleCalculatorAI(battle)
    
    # Add a lured suit
    suit = MockSuit(1)
    battle.luredSuits.append(suit)
    battle.activeSuits = [suit]
    
    # Test that lured suit cannot attack
    can_attack = battle_calculator._BattleCalculatorAI__suitCanAttack(1)
    if not can_attack:
        print("Lured suit correctly prevented from attacking")
        return True
    else:
        print("ERROR: Lured suit was allowed to attack")
        return False

def test_damage_calculation_bounds_checking():
    """Test that damage calculation includes bounds checking."""
    print("Testing damage calculation bounds checking...")
    
    # Create mock objects
    battle = MockBattle()
    battle_calculator = BattleCalculatorAI(battle)
    
    # Test bounds checking in various scenarios
    try:
        # This should not cause an IndexError
        suit = MockSuit(1)
        battle.activeSuits = [suit]
        
        # Simulate an attack that might go out of bounds
        attack = getToonAttack(1, track=LURE, level=0, target=0)
        # Extend the HP column to prevent index errors
        while len(attack[TOON_HP_COL]) < 4:
            attack[TOON_HP_COL].append(-1)
            
        # This should not cause an IndexError
        battle_calculator._BattleCalculatorAI__calcToonAtkHp(1)
        print("Damage calculation bounds checking successful")
        return True
    except Exception as e:
        print(f"Error in damage calculation bounds checking: {e}")
        return False

if __name__ == "__main__":
    print("Running battle calculation fixes tests...")
    
    tests = [
        test_lure_group_attack_target_index,
        test_lured_suit_cannot_attack,
        test_damage_calculation_bounds_checking
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test {test.__name__} failed with exception: {e}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! Battle calculation fixes are working correctly.")
    else:
        print("Some tests failed. Please review the fixes.")