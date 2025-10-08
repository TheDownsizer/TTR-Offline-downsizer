#!/usr/bin/env python
"""Test script to verify that lured suits cannot unlure until their rounds are exhausted."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from toontown.battle.BattleCalculatorAI import BattleCalculatorAI
from toontown.battle.BattleBase import getToonAttack, LURE, LURE_TRACK, TOON_TRACK_COL, TOON_LVL_COL, TOON_TGT_COL, TOON_HP_COL

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

class MockDNA:
    """Mock DNA class for testing."""
    def __init__(self, name='f'):
        self.name = name

class MockBattle:
    """Mock battle class for testing."""
    def __init__(self):
        self.activeSuits = [MockSuit(1)]
        self.activeToons = [1]
        self.luredSuits = []
        
    def getToon(self, toonId):
        return None
        
    def findSuit(self, suitId):
        for suit in self.activeSuits:
            if suit.doId == suitId:
                return suit
        return None

def test_lure_rounds_exhaustion():
    """Test that lured suits cannot unlure until their rounds are exhausted."""
    print("Testing lure rounds exhaustion...")
    
    # Create mock objects
    battle = MockBattle()
    battle_calculator = BattleCalculatorAI(battle)
    
    # Add a lured suit with 3 max rounds and 1 current round
    suit_id = 1
    battle_calculator.currentlyLuredSuits[suit_id] = [1, 3, 0, {}]  # [current_rounds, max_rounds, wake_chance, lurer_info]
    
    # Test that __luredWakeupTime returns False (suit should not wake up randomly)
    wakeup_time = battle_calculator._BattleCalculatorAI__luredWakeupTime(suit_id)
    if not wakeup_time:
        print("SUCCESS: Suit correctly prevented from random wakeup")
    else:
        print("ERROR: Suit was allowed to wake up randomly")
        return False
    
    # Test that __luredMaxRoundsReached returns False when rounds are not exhausted
    max_rounds_reached = battle_calculator._BattleCalculatorAI__luredMaxRoundsReached(suit_id)
    if not max_rounds_reached:
        print("SUCCESS: Suit correctly identified as not having exhausted rounds")
    else:
        print("ERROR: Suit incorrectly identified as having exhausted rounds")
        return False
    
    # Increment rounds to max
    battle_calculator._BattleCalculatorAI__incLuredCurrRound(suit_id)
    battle_calculator._BattleCalculatorAI__incLuredCurrRound(suit_id)
    
    # Now test that __luredMaxRoundsReached returns True when rounds are exhausted
    max_rounds_reached = battle_calculator._BattleCalculatorAI__luredMaxRoundsReached(suit_id)
    if max_rounds_reached:
        print("SUCCESS: Suit correctly identified as having exhausted rounds")
    else:
        print("ERROR: Suit not correctly identified as having exhausted rounds")
        return False
    
    print("All lure rounds tests passed!")
    return True

def test_suit_is_lured():
    """Test that suit is correctly identified as lured."""
    print("Testing suit is lured...")
    
    # Create mock objects
    battle = MockBattle()
    battle_calculator = BattleCalculatorAI(battle)
    
    # Add a lured suit
    suit_id = 1
    battle_calculator.currentlyLuredSuits[suit_id] = [0, 3, 0, {}]
    
    # Test that suit is correctly identified as lured
    is_lured = battle_calculator._BattleCalculatorAI__suitIsLured(suit_id)
    if is_lured:
        print("SUCCESS: Suit correctly identified as lured")
        return True
    else:
        print("ERROR: Suit not correctly identified as lured")
        return False

if __name__ == "__main__":
    print("Running lure rounds tests...")
    
    tests = [
        test_lure_rounds_exhaustion,
        test_suit_is_lured
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
        print("All tests passed! Lure rounds implementation is working correctly.")
    else:
        print("Some tests failed. Please review the implementation.")