"""
Movie Sequence Manager

Manages and coordinates all movie sequence builders for battle animations.
"""

from .toon_attack_builders import (
    FireSequenceBuilder, SOSSequenceBuilder, NPCSOSSequenceBuilder,
    PetSOSSequenceBuilder, HealSequenceBuilder, TrapSequenceBuilder,
    LureSequenceBuilder, SoundSequenceBuilder, ThrowSequenceBuilder,
    SquirtSequenceBuilder, DropSequenceBuilder
)
from .suit_attack_builders import (
    SuitAttackSequenceBuilder, CustomSuitAttackBuilder,
    GroupSuitAttackBuilder, SingleSuitAttackBuilder
)
from . import BaseSequenceBuilder, SequenceBuilderError, SequenceConfig
from direct.interval.IntervalGlobal import *
from panda3d.core import *
import config
import random
from .. import MovieUtil

class MovieSequenceManager:
    """
    Manages all movie sequence builders and coordinates sequence generation
    """
    
    def __init__(self, movie):
        self.movie = movie
        self.battle = movie.battle
        self.notify = movie.notify
        
        # Initialize all sequence builders
        self.toon_builders = [
            FireSequenceBuilder(movie),
            SOSSequenceBuilder(movie),
            NPCSOSSequenceBuilder(movie),
            PetSOSSequenceBuilder(movie),
            HealSequenceBuilder(movie),
            TrapSequenceBuilder(movie),
            LureSequenceBuilder(movie),
            SoundSequenceBuilder(movie),
            ThrowSequenceBuilder(movie),
            SquirtSequenceBuilder(movie),
            DropSequenceBuilder(movie)
        ]
        
        self.suit_builders = [
            SuitAttackSequenceBuilder(movie),
            # GroupSuitAttackBuilder(movie),  # Can enable for specialized handling
            # SingleSuitAttackBuilder(movie)   # Can enable for specialized handling
        ]
        
        # Custom builders registry for extensions
        self.custom_builders = []
        
        # Sort builders by priority
        self._sort_builders()
    
    def _sort_builders(self):
        """Sort builders by their priority"""
        self.toon_builders.sort(key=lambda b: b.get_priority())
        self.suit_builders.sort(key=lambda b: b.get_priority())
        self.custom_builders.sort(key=lambda b: b.get_priority())
    
    def register_custom_builder(self, builder):
        """Register a custom sequence builder"""
        if not isinstance(builder, BaseSequenceBuilder):
            raise SequenceBuilderError("Builder must inherit from BaseSequenceBuilder")
        
        self.custom_builders.append(builder)
        self._sort_builders()
    
    def unregister_custom_builder(self, builder):
        """Unregister a custom sequence builder"""
        if builder in self.custom_builders:
            self.custom_builders.remove(builder)
    
    def build_toon_attack_sequences(self, toon_attack_dicts):
        """
        Build all toon attack sequences
        Returns: (main_track, camera_track) or (None, None)
        """
        if not config.ConfigVariableBool(SequenceConfig.WANT_TOON_ATTACKS, 1).getValue():
            return (None, None)
        
        if not toon_attack_dicts:
            return (None, None)
        
        # Initialize shot direction randomly
        if random.random() > 0.5:
            MovieUtil.shotDirection = 'left'
        else:
            MovieUtil.shotDirection = 'right'
        
        # Reset suit trap freshness
        for suit in self.battle.activeSuits:
            suit.battleTrapIsFresh = 0
        
        main_track = Sequence(name='toon-attacks')
        camera_track = Sequence(name='toon-attacks-cam')
        
        # Process builders in priority order
        all_builders = self.toon_builders + self.custom_builders
        all_builders.sort(key=lambda b: b.get_priority())
        
        for builder in all_builders:
            try:
                # Filter attacks that this builder can handle
                handled_attacks = []
                for attack in toon_attack_dicts:
                    if builder.can_handle_attack(attack):
                        handled_attacks.append(attack)
                
                if handled_attacks:
                    ival, cam_ival = builder.build_sequence(handled_attacks)
                    if ival:
                        main_track.append(ival)
                        camera_track.append(cam_ival)
                        
                        if self.notify.getDebug():
                            self.notify.debug(f'Added {builder.get_sequence_name()} sequence')
            
            except Exception as e:
                self.notify.warning(f'Error in {builder.get_sequence_name()} builder: {e}')
                # Continue with other builders
                continue
        
        if len(main_track) == 0:
            return (None, None)
        
        return (main_track, camera_track)
    
    def build_suit_attack_sequences(self, suit_attack_dicts):
        """
        Build all suit attack sequences
        Returns: (main_track, camera_track) or (None, None)
        """
        if not config.ConfigVariableBool(SequenceConfig.WANT_SUIT_ATTACKS, 1).getValue():
            return (None, None)
        
        if not suit_attack_dicts:
            return (None, None)
        
        main_track = Sequence(name='suit-attacks')
        camera_track = Sequence(name='suit-attacks-cam')
        
        # Process builders in priority order
        all_builders = self.suit_builders + self.custom_builders
        all_builders.sort(key=lambda b: b.get_priority())
        
        for builder in all_builders:
            try:
                # Filter attacks that this builder can handle
                handled_attacks = []
                for attack in suit_attack_dicts:
                    if builder.can_handle_attack(attack):
                        handled_attacks.append(attack)
                
                if handled_attacks:
                    ival, cam_ival = builder.build_sequence(handled_attacks)
                    if ival:
                        main_track.append(ival)
                        camera_track.append(cam_ival)
                        
                        if self.notify.getDebug():
                            self.notify.debug(f'Added {builder.get_sequence_name()} sequence')
                        
                        # For suit attacks, we typically only want one builder to handle them
                        # Remove handled attacks to prevent duplicate processing
                        for attack in handled_attacks:
                            if attack in suit_attack_dicts:
                                suit_attack_dicts.remove(attack)
            
            except Exception as e:
                self.notify.warning(f'Error in {builder.get_sequence_name()} builder: {e}')
                # Continue with other builders
                continue
        
        if len(main_track) == 0:
            return (None, None)
        
        return (main_track, camera_track)
    
    def build_complete_movie_sequence(self, toon_attack_dicts, suit_attack_dicts, callback):
        """
        Build the complete movie sequence with toon attacks, suit attacks, and callback
        Returns: main_track
        """
        main_track = Sequence(name=f'movie-track-{self.battle.doId}')
        camera_track = Sequence(name=f'movie-track-cam-{self.battle.doId}')
        
        # Build toon attack sequences
        toon_ival, toon_cam = self.build_toon_attack_sequences(toon_attack_dicts)
        if toon_ival:
            main_track.append(toon_ival)
            camera_track.append(toon_cam)
        
        # Build suit attack sequences
        suit_ival, suit_cam = self.build_suit_attack_sequences(suit_attack_dicts)
        if suit_ival:
            main_track.append(suit_ival)
            camera_track.append(suit_cam)
        
        # Add callback at the end
        main_track.append(Func(callback))
        
        # Combine with camera track if local toon is active
        if self.battle.localToonPendingOrActive():
            combined_track = Parallel(
                main_track, 
                camera_track,
                name=f'movie-track-with-cam-{self.battle.doId}'
            )
            return combined_track
        
        return main_track
    
    def get_builder_by_name(self, name):
        """Get a specific builder by name"""
        all_builders = self.toon_builders + self.suit_builders + self.custom_builders
        for builder in all_builders:
            if builder.get_sequence_name() == name:
                return builder
        return None
    
    def get_all_builders(self):
        """Get all registered builders"""
        return {
            'toon_builders': self.toon_builders,
            'suit_builders': self.suit_builders,
            'custom_builders': self.custom_builders
        }
    
    def enable_builder(self, builder_name, enabled=True):
        """Enable or disable a specific builder"""
        builder = self.get_builder_by_name(builder_name)
        if builder:
            builder.enabled = enabled
    
    def is_builder_enabled(self, builder_name):
        """Check if a builder is enabled"""
        builder = self.get_builder_by_name(builder_name)
        return builder.enabled if builder and hasattr(builder, 'enabled') else True
    
    def clear_custom_builders(self):
        """Remove all custom builders"""
        self.custom_builders.clear()
    
    def get_sequence_info(self):
        """Get information about available sequence types"""
        info = {
            'toon_sequences': [b.get_sequence_name() for b in self.toon_builders],
            'suit_sequences': [b.get_sequence_name() for b in self.suit_builders],
            'custom_sequences': [b.get_sequence_name() for b in self.custom_builders]
        }
        return info