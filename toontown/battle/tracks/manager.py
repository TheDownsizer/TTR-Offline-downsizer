"""Manager for all gag track calculators."""

from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.BattleBase import *
from .base import TrackCalculatorBase
from .throw import ThrowTrackCalculator
from .squirt import SquirtTrackCalculator
from .sound import SoundTrackCalculator
from .lure import LureTrackCalculator
from .trap import TrapTrackCalculator
from .drop import DropTrackCalculator
from .heal import HealTrackCalculator
from .fire import FireTrackCalculator

class TrackCalculatorManager:
    """Manager that handles all gag track calculators."""
    
    def __init__(self, battle_calculator):
        self.battle_calculator = battle_calculator
        self.track_calculators = {}
        
        # Initialize all track calculators
        self._initialize_track_calculators()
    
    def _initialize_track_calculators(self):
        """Initialize all track calculators."""
        self.track_calculators[THROW] = ThrowTrackCalculator(self.battle_calculator)
        self.track_calculators[SQUIRT] = SquirtTrackCalculator(self.battle_calculator)
        self.track_calculators[SOUND] = SoundTrackCalculator(self.battle_calculator)
        self.track_calculators[LURE] = LureTrackCalculator(self.battle_calculator)
        self.track_calculators[TRAP] = TrapTrackCalculator(self.battle_calculator)
        self.track_calculators[DROP] = DropTrackCalculator(self.battle_calculator)
        self.track_calculators[HEAL] = HealTrackCalculator(self.battle_calculator)
        self.track_calculators[FIRE] = FireTrackCalculator(self.battle_calculator)
    
    def calculate_attack(self, track, toon_id, attack):
        """Calculate an attack for the specified track."""
        if track in self.track_calculators:
            return self.track_calculators[track].calculate_attack(toon_id, attack)
        else:
            # Fallback to default behavior
            self.battle_calculator._BattleCalculatorAI__calcToonAtkHp(toon_id)
            attack_idx = self.battle_calculator.toonAtkOrder.index(toon_id)
            self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=0)
            self.battle_calculator._BattleCalculatorAI__handleBonus(attack_idx, hp=1)
            return self.battle_calculator._BattleCalculatorAI__attackHasHit(attack, suit=0)
    
    def calculate_damage(self, track, toon_id, attack, target_list, atk_level, atk_hp=0, atk_acc=0):
        """Calculate damage for the specified track."""
        if track in self.track_calculators:
            if track == LURE:
                return self.track_calculators[track].calculate_damage(toon_id, attack, target_list, atk_level, atk_acc)
            elif track == TRAP:
                return self.track_calculators[track].calculate_damage(toon_id, attack, target_list, atk_level, atk_hp)
            else:
                return self.track_calculators[track].calculate_damage(toon_id, attack, target_list, atk_level)
        else:
            # For unsupported tracks, we don't calculate damage
            pass
    
    def create_toon_target_list(self, attack_index):
        """Create target list for toon attack using appropriate track calculator."""
        attack = self.battle_calculator.battle.toonAttacks[attack_index]
        atk_track, atk_level = self.battle_calculator._BattleCalculatorAI__getActualTrackLevel(attack)
        
        # Use track-specific target list creation when available
        if atk_track in self.track_calculators:
            # Check if the track calculator has a create_target_list method
            calculator = self.track_calculators[atk_track]
            if hasattr(calculator, 'create_target_list'):
                return calculator.create_target_list(attack_index, attack)
        
        # Fallback to original logic
        target_list = []
        if atk_track == NPCSOS:
            return target_list
        if not attackAffectsGroup(atk_track, atk_level, attack[TOON_TRACK_COL]):
            if atk_track == HEAL:
                target = attack[TOON_TGT_COL]
            else:
                target = self.battle_calculator.battle.findSuit(attack[TOON_TGT_COL])
            if target is not None:
                target_list.append(target)
        elif atk_track == HEAL or atk_track == PETSOS:
            if attack[TOON_TRACK_COL] == NPCSOS or atk_track == PETSOS:
                target_list = self.battle_calculator.battle.activeToons
            else:
                for curr_toon in self.battle_calculator.battle.activeToons:
                    if attack[TOON_ID_COL] != curr_toon:
                        target_list.append(curr_toon)
        else:
            target_list = self.battle_calculator.battle.activeSuits
        return target_list
    
    def is_unlure_attack(self, attack_index):
        """Check if attack is an unlure attack using appropriate track calculator."""
        attack = self.battle_calculator.battle.toonAttacks[attack_index]
        track = self.battle_calculator._BattleCalculatorAI__getActualTrack(attack)
        
        # Use track-specific unlure check when available
        if track in self.track_calculators:
            calculator = self.track_calculators[track]
            if hasattr(calculator, 'is_unlure_attack'):
                return calculator.is_unlure_attack(attack_index, attack)
        
        # Fallback to original logic
        if track == THROW or track == SQUIRT or track == SOUND:
            return True
        return False