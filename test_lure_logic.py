#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script to verify that lured suits can't attack until their lure rounds run out.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, r'c:\TTR-Offline-downsizer')

from toontown.battle.BattleCalculatorAI import BattleCalculatorAI
from toontown.battle.BattleBase import getDefaultSuitAttack
from direct.directnotify.DirectNotifyGlobal import directNotify

class MockBattle:
    """Mock battle object for testing"""
    def __init__(self):
        self.activeToons = [1001, 1002, 1003, 1004]
        self.activeSuits = []
        self.suitAttacks = []
        self.luredSuits = []
        self.pendingSuits = []
        self.joiningSuits = []
        
        # Initialize suit attacks
        for i in range(4):
            self.suitAttacks.append(getDefaultSuitAttack())
    
    def findSuit(self, suitId):
        """Mock findSuit method"""
        # Return a mock suit object
        class MockSuit:
            def __init__(self, suitId):
                self.doId = suitId
                self.dna = type('DNA', (), {'name': 'f'})()  # Mock DNA with name 'f'
                self.currHP = 100
                self.getHP = lambda: 100
                self.setHP = lambda hp: None
                self.getActualLevel = lambda: 1
                self.getLevel = lambda: 1
                self.isGenerated = lambda: True
                self.b_setHP = lambda hp: None
        
        return MockSuit(suitId)
    
    def getToon(self, toonId):
        """Mock getToon method"""
        class MockToon:
            def __init__(self, toonId):
                self.doId = toonId
                self.hp = 50
                self.maxHp = 50
                self.immortalMode = False
        
        return MockToon(toonId)

def test_lure_logic():
    """Test that lured suits can't attack until their rounds run out"""
    print("Testing lure logic...")
    
    # Create mock battle and calculator
    battle = MockBattle()
    calculator = BattleCalculatorAI(battle)
    
    # Test 1: Non-lured suit should be able to attack
    suit_id = 2001
    can_attack = calculator._BattleCalculatorAI__suitCanAttack(suit_id)
    print(f"Non-lured suit {suit_id} can attack: {bool(can_attack)}")
    assert can_attack == 1, f"Non-lured suit should be able to attack, got {can_attack}"
    
    # Test 2: Lured suit with rounds remaining should not be able to attack
    # Add a lured suit with 2 rounds remaining (current round = 0, max rounds = 3)
    calculator.currentlyLuredSuits[suit_id] = [0, 3, 50, {1001: [1, 1, 1]}]
    can_attack = calculator._BattleCalculatorAI__suitCanAttack(suit_id)
    print(f"Lured suit {suit_id} with rounds remaining can attack: {bool(can_attack)}")
    assert can_attack == 0, f"Lured suit with rounds remaining should not be able to attack, got {can_attack}"
    
    # Test 3: Lured suit with rounds exhausted should be able to attack
    # Update the suit to have completed all rounds
    calculator.currentlyLuredSuits[suit_id] = [3, 3, 50, {1001: [1, 1, 1]}]
    can_attack = calculator._BattleCalculatorAI__suitCanAttack(suit_id)
    print(f"Lured suit {suit_id} with rounds exhausted can attack: {bool(can_attack)}")
    # After rounds are exhausted, the suit should be removed from currentlyLuredSuits
    # So it should be able to attack
    assert suit_id not in calculator.currentlyLuredSuits, "Suit should be removed from lured suits after rounds exhausted"
    
    # Test 4: Dead suit should not be able to attack
    class MockDeadSuit:
        def __init__(self):
            self.doId = 3001
    
    dead_suit_id = 3001
    # Mock the combatantDead method to return True for this suit
    original_combatant_dead = calculator._BattleCalculatorAI__combatantDead
    calculator._BattleCalculatorAI__combatantDead = lambda avId, toon: 1 if avId == dead_suit_id else original_combatant_dead(avId, toon)
    
    can_attack = calculator._BattleCalculatorAI__suitCanAttack(dead_suit_id)
    print(f"Dead suit {dead_suit_id} can attack: {bool(can_attack)}")
    assert can_attack == 0, f"Dead suit should not be able to attack, got {can_attack}"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_lure_logic()