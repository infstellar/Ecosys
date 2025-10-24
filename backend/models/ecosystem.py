"""
Ecosystem Data Model
Manages the entire ecosystem state and data
"""

import random
import numpy as np
from typing import List, Dict, Any, Tuple
from .species import Grass, Cow, Tiger, Position


class EcosystemConfig:
    """Ecosystem Configuration"""
    def __init__(self, world_width=800, world_height=600, 
                 initial_grass=100, initial_cows=10, initial_tigers=1):
        self.world_width = world_width
        self.world_height = world_height
        self.initial_grass = initial_grass
        self.initial_cows = initial_cows
        self.initial_tigers = initial_tigers


class EcosystemState:
    """Ecosystem State Management"""
    
    def __init__(self, config: EcosystemConfig):
        self.config = config
        self.time_step = 0
        
        # Species lists
        self.grass_list: List[Grass] = []
        self.cow_list: List[Cow] = []
        self.tiger_list: List[Tiger] = []
        
        # Statistics
        self.births = {'grass': 0, 'cow': 0, 'tiger': 0}
        self.deaths = {'grass': 0, 'cow': 0, 'tiger': 0}
        self.population_history = []
        
        # Initialize populations
        self._initialize_populations()
    
    def _initialize_populations(self):
        """Initialize populations"""
        # Initialize grass
        for _ in range(self.config.initial_grass):
            position = Position(
                random.randint(0, self.config.world_width),
                random.randint(0, self.config.world_height)
            )
            grass = Grass(position)
            self.grass_list.append(grass)
        
        # Initialize cows
        for _ in range(self.config.initial_cows):
            position = Position(
                random.randint(0, self.config.world_width),
                random.randint(0, self.config.world_height)
            )
            cow = Cow(position)
            self.cow_list.append(cow)
        
        # Initialize tigers
        for _ in range(self.config.initial_tigers):
            position = Position(
                random.randint(0, self.config.world_width),
                random.randint(0, self.config.world_height)
            )
            tiger = Tiger(position)
            self.tiger_list.append(tiger)
    
    def get_ecosystem_state(self) -> Dict[str, Any]:
        """Get ecosystem state dictionary for species updates"""
        # Precompute grass positions for numpy optimization
        alive_grass_positions = []
        alive_grass_objects = []
        for grass in self.grass_list:
            if grass.alive:
                alive_grass_positions.append([grass.position.x, grass.position.y])
                alive_grass_objects.append(grass)
        
        grass_positions_array = np.array(alive_grass_positions) if alive_grass_positions else np.empty((0, 2))
        
        return {
            'world_width': self.config.world_width,
            'world_height': self.config.world_height,
            'grass_list': self.grass_list,
            'cow_list': self.cow_list,
            'tiger_list': self.tiger_list,
            'time_step': self.time_step,
            # Precomputed numpy arrays for performance
            'grass_positions_array': grass_positions_array,
            'alive_grass_objects': alive_grass_objects
        }
    
    def update_species(self, ecosystem_state: Dict[str, Any]):
        """Update species lists"""
        # Update all species
        for grass in self.grass_list[:]:
            grass.update(ecosystem_state)
        for cow in self.cow_list[:]:
            cow.update(ecosystem_state)
        for tiger in self.tiger_list[:]:
            tiger.update(ecosystem_state)
    
    def handle_reproduction(self):
        """Handle reproduction"""
        new_grass = []
        new_cows = []
        new_tigers = []
        
        # Grass reproduction
        ecosystem_state = self.get_ecosystem_state()
        for grass in self.grass_list[:]:  # Use slice to avoid modifying list during iteration
            if grass.can_reproduce():
                new_grass_individual = grass.reproduce(ecosystem_state)
                if new_grass_individual:
                    new_grass.append(new_grass_individual)
        
        # Cow reproduction
        for cow in self.cow_list[:]:
            if cow.can_reproduce():
                new_cow = cow.reproduce(ecosystem_state)
                if new_cow:
                    new_cows.append(new_cow)
        
        # Tiger reproduction
        for tiger in self.tiger_list[:]:
            if tiger.can_reproduce():
                new_tiger = tiger.reproduce(ecosystem_state)
                if new_tiger:
                    new_tigers.append(new_tiger)
        
        # Add new individuals
        self.grass_list.extend(new_grass)
        self.cow_list.extend(new_cows)
        self.tiger_list.extend(new_tigers)
        
        # Record birth counts and log reproduction events
        self.births['grass'] += len(new_grass)
        self.births['cow'] += len(new_cows)
        self.births['tiger'] += len(new_tigers)
        
        # Log reproduction events
        if len(new_grass) > 0:
            print(f"🌱 {len(new_grass)} new grass individuals born")
        if len(new_cows) > 0:
            print(f"🐄 {len(new_cows)} new cows born")
        if len(new_tigers) > 0:
            print(f"🐅 {len(new_tigers)} new tigers born")
    
    def update_statistics(self):
        """Update statistics"""
        counts = self.get_species_counts()
        self.population_history.append(counts.copy())
        
        # Keep history data within reasonable range
        if len(self.population_history) > 100:
            self.population_history = self.population_history[-100:]
    
    def cleanup_dead(self):
        """Remove dead individuals and update death statistics"""
        # Count deaths before cleanup and log death reasons
        dead_grass = []
        dead_cows = []
        dead_tigers = []
        
        # Collect dead individuals and their death reasons
        for g in self.grass_list:
            if not g.alive:
                dead_grass.append(g)
        
        for c in self.cow_list:
            if not c.alive:
                dead_cows.append(c)
        
        for t in self.tiger_list:
            if not t.alive:
                dead_tigers.append(t)
        
        # Debug: Print cleanup status every 100 time steps
        if self.time_step % 100 == 0:
            print(f"⏰ Time step {self.time_step}: Alive - Grass: {len(self.grass_list) - len(dead_grass)}, Cows: {len(self.cow_list) - len(dead_cows)}, Tigers: {len(self.tiger_list) - len(dead_tigers)}")
        
        # Log death reasons to console (exclude grass)
        if dead_cows:
            for cow in dead_cows:
                print(f"🐄 Cow died: {cow.death_reason} (Age: {cow.age}, Energy: {cow.energy})")
        
        if dead_tigers:
            for tiger in dead_tigers:
                print(f"🐅 Tiger died: {tiger.death_reason} (Age: {tiger.age}, Energy: {tiger.energy})")
        
        # Update death statistics
        self.deaths['grass'] += len(dead_grass)
        self.deaths['cow'] += len(dead_cows)
        self.deaths['tiger'] += len(dead_tigers)
        
        # Remove dead individuals
        self.grass_list = [g for g in self.grass_list if g.alive]
        self.cow_list = [c for c in self.cow_list if c.alive]
        self.tiger_list = [t for t in self.tiger_list if t.alive]
    
    def get_species_counts(self) -> Dict[str, int]:
        """Get current species counts"""
        return {
            'grass': len(self.grass_list),
            'cow': len(self.cow_list),
            'tiger': len(self.tiger_list),
            'total': len(self.grass_list) + len(self.cow_list) + len(self.tiger_list)
        }
    
    def get_species_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get species data for frontend rendering"""
        grass_data = []
        for grass in self.grass_list:
            if grass.alive:
                grass_data.append({
                    'x': grass.position.x,
                    'y': grass.position.y,
                    'energy': grass.energy,
                    'age': grass.age,
                    'max_energy': grass.max_energy
                })
        
        cow_data = []
        for cow in self.cow_list:
            if cow.alive:
                cow_data.append({
                    'x': cow.position.x,
                    'y': cow.position.y,
                    'energy': cow.energy,
                    'age': cow.age,
                    'max_energy': cow.max_energy
                })
        
        tiger_data = []
        for tiger in self.tiger_list:
            if tiger.alive:
                tiger_data.append({
                    'x': tiger.position.x,
                    'y': tiger.position.y,
                    'energy': tiger.energy,
                    'age': tiger.age,
                    'max_energy': tiger.max_energy
                })
        
        return {
            'grass': grass_data,
            'cow': cow_data,
            'tiger': tiger_data
        }
    
    def reset(self, config: EcosystemConfig = None):
        """Reset ecosystem"""
        if config:
            self.config = config
        
        self.time_step = 0
        self.grass_list.clear()
        self.cow_list.clear()
        self.tiger_list.clear()
        
        # Reset statistics
        self.births = {'grass': 0, 'cow': 0, 'tiger': 0}
        self.deaths = {'grass': 0, 'cow': 0, 'tiger': 0}
        self.population_history.clear()
        
        # Reinitialize populations
        self._initialize_populations()
    
    def check_extinction(self) -> List[str]:
        """Check if any species are extinct"""
        extinct_species = []
        
        if len(self.grass_list) == 0:
            extinct_species.append('grass')
        if len(self.cow_list) == 0:
            extinct_species.append('cow')
        if len(self.tiger_list) == 0:
            extinct_species.append('tiger')
        
        return extinct_species