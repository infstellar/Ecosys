"""
Species Data Model
Defines the base species class and specific species implementations in the ecosystem
"""

import random
import math
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class Position:
    """Position coordinates"""
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate distance to another position"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


class Species:
    """Species base class"""
    def __init__(self, position: Position, energy: int = 100, max_age: int = 100, reproduction_energy_cost: int = 50):
        self.position = position
        self.energy = reproduction_energy_cost
        self.max_energy = energy*4
        self.age = 0
        self.max_age = max_age
        self.alive = True
        self.reproduction_cooldown = 0
        self.death_reason = None  # Record the reason for death
        self.species_name = self.__class__.__name__  # Store species name for logging
        self.reproduction_energy_cost = reproduction_energy_cost
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update species state"""
        if not self.alive:
            return
        
        # Reduce reproduction cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return self.alive and self.energy >= self.reproduction_energy_cost*2 and self.reproduction_cooldown <= 0
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Species']:
        """Reproduce to create new individual"""
        return None
    
    def move_randomly(self, world_width: int, world_height: int, speed: float = 1.0) -> None:
        """Random movement"""
        if not self.alive:
            return
        
        # Random direction
        angle = random.uniform(0, 2 * math.pi)
        dx = math.cos(angle) * speed
        dy = math.sin(angle) * speed
        
        # Update position with boundary constraints
        self.position.x = max(0, min(world_width, self.position.x + dx))
        self.position.y = max(0, min(world_height, self.position.y + dy))
    
    def age_one_step(self) -> None:
        """Age increases by one step"""
        self.age += 1
        if self.age >= self.max_age:
            self.die_from_old_age()
    
    def die(self, reason: str = "Unknown") -> None:
        """Death with reason"""
        if self.alive:  # Only record death reason once
            self.alive = False
            self.death_reason = reason
            
    
    def die_from_old_age(self) -> None:
        """Death from old age"""
        self.die("Old age")
    
    def die_from_starvation(self) -> None:
        """Death from starvation"""
        self.die("Starvation")
    
    def die_from_predation(self, predator_name: str) -> None:
        """Death from being eaten by predator"""
        self.die(f"Predation by {predator_name}")


class Animal(Species):
    """Animal base class - inherits from Species and adds intelligent movement"""
    
    def __init__(self, position: Position, energy: int = 100, max_age: int = 100, reproduction_energy_cost: int = 50,
                 movement_speed: float = 1.0, energy_consumption: int = 1, hunting_range: float = 5.0,
                 hunting_success_rate: float = 0.5, detection_range: float = 500.0, 
                 food_types: List[str] = None, hunting_cooldown_duration: int = 0):
        super().__init__(position, energy, max_age, reproduction_energy_cost)
        self.movement_speed = movement_speed
        self.energy_consumption = energy_consumption
        self.hunting_range = hunting_range
        self.hunting_success_rate = hunting_success_rate
        self.detection_range = detection_range
        self.food_types = food_types if food_types is not None else []
        self.hunting_cooldown = 0  # Cooldown after hunting/eating
        self.hunting_cooldown_duration = hunting_cooldown_duration
    
    def find_nearest_food(self, ecosystem_state: Dict[str, Any]) -> Optional[Position]:
        """Find the nearest food source"""
        nearest_food = None
        min_distance = float('inf')
        
        for food_type in self.food_types:
            food_list = ecosystem_state.get(f'{food_type}_list', [])
            for food in food_list:
                if food.alive:
                    distance = self.position.distance_to(food.position)
                    if distance <= self.detection_range and distance < min_distance:
                        min_distance = distance
                        nearest_food = food.position
        
        return nearest_food
    
    def move_towards_target(self, target_position: Position, world_width: int, world_height: int) -> None:
        """Move towards a target position"""
        if not self.alive:
            return
        
        # Calculate direction to target
        dx = target_position.x - self.position.x
        dy = target_position.y - self.position.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction and apply speed
            dx = (dx / distance) * self.movement_speed
            dy = (dy / distance) * self.movement_speed
            
            # Update position with boundary constraints
            self.position.x = max(0, min(world_width, self.position.x + dx))
            self.position.y = max(0, min(world_height, self.position.y + dy))
    
    def intelligent_move(self, ecosystem_state: Dict[str, Any]) -> None:
        """Intelligent movement - move towards food if available, otherwise move randomly"""
        if not self.alive:
            return
        
        # Check if in hunting cooldown (stay still)
        if self.hunting_cooldown > 0:
            self.hunting_cooldown -= 1
            return  # Don't move during cooldown
        
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        # Try to find food
        nearest_food = self.find_nearest_food(ecosystem_state)
        
        if nearest_food:
            # Move towards food
            self.move_towards_target(nearest_food, world_width, world_height)
        else:
            # No food found, move randomly
            self.move_randomly(world_width, world_height, self.movement_speed)
    
    def start_hunting_cooldown(self) -> None:
        """Start hunting cooldown - animal will stay still for a period"""
        self.hunting_cooldown = self.hunting_cooldown_duration


class Grass(Species):
    """Grass class - Producer"""
    
    def __init__(self, position: Position):
        super().__init__(position, energy=40, max_age=2000, reproduction_energy_cost=40)
        self.base_growth_rate = 0.9  # Slightly increased base growth rate
        self.reproduction_chance = 0.4  # Reduced reproduction chance to balance density
        self.competition_radius = 30.0  # Increased competition radius for more realistic effect
        self.max_competition_effect = 0.9  # Reduced max competition effect for better balance
    
    def calculate_nearby_grass_density_optimized(self, ecosystem_state: Dict[str, Any]) -> float:
        """Calculate the density of grass in the nearby area using precomputed numpy arrays"""
        grass_positions_array = ecosystem_state.get('grass_positions_array', np.empty((0, 2)))
        alive_grass_objects = ecosystem_state.get('alive_grass_objects', [])
        
        if grass_positions_array.size == 0:
            return 0.0
        
        # Find the index of self in alive_grass_objects to exclude it
        self_index = -1
        for i, grass in enumerate(alive_grass_objects):
            if grass is self:
                self_index = i
                break
        
        # Create a mask to exclude self from calculations
        if self_index >= 0:
            mask = np.ones(len(grass_positions_array), dtype=bool)
            mask[self_index] = False
            filtered_positions = grass_positions_array[mask]
        else:
            filtered_positions = grass_positions_array
        
        if filtered_positions.size == 0:
            return 0.0
        
        # Vectorized distance calculation
        self_position = np.array([self.position.x, self.position.y])
        distances = np.linalg.norm(filtered_positions - self_position, axis=1)
        
        # Count grass within competition radius
        nearby_grass_count = np.sum(distances <= self.competition_radius)
        
        # Return normalized density (0-1 scale)
        max_possible_grass = math.pi * (self.competition_radius ** 2) / 400
        density = min(1.0, nearby_grass_count / max_possible_grass)
        
        return density

    def calculate_nearby_grass_density(self, ecosystem_state: Dict[str, Any]) -> float:
        """Calculate the density of grass in the nearby area using numpy optimization"""
        # Use optimized version if precomputed arrays are available
        if 'grass_positions_array' in ecosystem_state:
            return self.calculate_nearby_grass_density_optimized(ecosystem_state)
        
        # Fallback to original implementation
        grass_list = ecosystem_state.get('grass_list', [])
        
        if not grass_list:
            return 0.0
        
        # Extract positions of all alive grass (excluding self)
        alive_grass_positions = []
        for grass in grass_list:
            if grass != self and grass.alive:
                alive_grass_positions.append([grass.position.x, grass.position.y])
        
        if not alive_grass_positions:
            return 0.0
        
        # Convert to numpy array for vectorized computation
        grass_positions = np.array(alive_grass_positions)
        self_position = np.array([self.position.x, self.position.y])
        
        # Vectorized distance calculation
        distances = np.linalg.norm(grass_positions - self_position, axis=1)
        
        # Count grass within competition radius
        nearby_grass_count = np.sum(distances <= self.competition_radius)
        
        # Return normalized density (0-1 scale)
        # Higher values mean more competition
        max_possible_grass = math.pi * (self.competition_radius ** 2) / 100  # Assume 1 grass per 200 units area
        density = min(1.0, nearby_grass_count / max_possible_grass)
        
        return density
    
    def get_competition_adjusted_growth_rate(self, ecosystem_state: Dict[str, Any]) -> float:
        """Calculate growth rate adjusted for local competition"""
        density = self.calculate_nearby_grass_density(ecosystem_state)
        
        # Growth rate decreases with higher density
        # Formula: growth_rate = base_rate * (1 - density * max_competition_effect)
        competition_factor = 1.0 - (density**0.3 * self.max_competition_effect)
        if density == 0:
            competition_factor = 2.0
        adjusted_growth_rate = self.base_growth_rate * competition_factor
        
        # Ensure growth rate doesn't go below 10% of base rate
        min_growth_rate = self.base_growth_rate * 0.01
        return max(min_growth_rate, adjusted_growth_rate)

    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update grass state"""
        # Call parent update first to handle reproduction cooldown
        super().update(ecosystem_state)
        
        if not self.alive:
            return
        
        # Calculate competition-adjusted growth rate
        adjusted_growth_rate = self.get_competition_adjusted_growth_rate(ecosystem_state)
        
        # Growth gains energy based on competition
        self.energy = min(self.max_energy, self.energy + adjusted_growth_rate)
        
        # Age increases
        self.age_one_step()
        
        # Death check from old age - handled by age_one_step() now
        if self.age >= self.max_age:
            self.die()
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                random.random() < self.reproduction_chance)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Grass']:
        """Reproduce to create new grass"""
        super().reproduce(ecosystem_state)
        
        if not self.can_reproduce():
            return None
        
        # Generate new grass at nearby random position
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        new_x = max(0, min(world_width, self.position.x + random.uniform(-200, 200)))
        new_y = max(0, min(world_height, self.position.y + random.uniform(-200, 200)))
        
        if new_x <= 0 or new_x >= world_width or new_y <= 0 or new_y >= world_height:
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 10

        
        new_position = Position(new_x, new_y)
        return Grass(new_position)


class Cow(Animal):
    """Cow class - Primary consumer"""
    
    def __init__(self, position: Position):
        super().__init__(position, 
                        energy=400, 
                        max_age=4000, 
                        reproduction_energy_cost=400,
                        movement_speed=3.0,
                        energy_consumption=2,
                        hunting_range=5.0,  # eating_range equivalent
                        hunting_success_rate=1.0,  # Cows always succeed in eating grass
                        detection_range=800.0,
                        food_types=['grass'],
                        hunting_cooldown_duration=0,
                        )
        # Keep eating_range for backward compatibility if needed elsewhere
        self.eating_range = self.hunting_range
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update cow state"""
        # Call parent update first to handle reproduction cooldown
        super().update(ecosystem_state)
        
        if not self.alive:
            return
        
        # Intelligent movement - move towards grass if available
        self.intelligent_move(ecosystem_state)
        
        # Consume energy
        self.energy -= self.energy_consumption
        
        # Find and eat grass
        self._eat_grass(ecosystem_state.get('grass_list', []))
        
        # Age increases
        self.age_one_step()
        
        # Death check
        if self.energy <= 0:
            self.die_from_starvation()
    
    def _eat_grass(self, grass_list: List['Grass']) -> None:
        """Eat grass"""
        for grass in grass_list:
            # Double check: grass must be alive and within eating range
            if grass.alive and self.position.distance_to(grass.position) <= self.eating_range:
                # Eat grass, gain energy
                self.energy = min(self.max_energy, self.energy + grass.energy)
                grass.die_from_predation("Cow")
                break  # Only eat one grass at a time
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                self.age > 20)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Cow']:
        """Reproduce to create new cow"""
        super().reproduce(ecosystem_state)
        
        if not self.can_reproduce():
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 200
        
        # Generate new cow at nearby random position
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        new_x = max(0, min(world_width, self.position.x + random.uniform(-10, 10)))
        new_y = max(0, min(world_height, self.position.y + random.uniform(-10, 10)))
        
        new_position = Position(new_x, new_y)
        return Cow(new_position)


class Tiger(Animal):
    """Tiger class - Secondary consumer"""
    
    def __init__(self, position: Position):
        super().__init__(position, 
                        energy=4000, 
                        max_age=8000, 
                        reproduction_energy_cost=4000,
                        movement_speed=4.0,
                        energy_consumption=20,
                        hunting_range=6.0,
                        hunting_success_rate=0.2,
                        detection_range=1000.0,
                        food_types=['cow'],
                        hunting_cooldown_duration=4)
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update tiger state"""
        # Call parent update first to handle reproduction cooldown
        super().update(ecosystem_state)
        
        if self.energy <= self.reproduction_energy_cost/3:
            # self.movement_speed = 3.8 + 0.1+0.3*(1 - self.age/self.max_age)
            self.hunting_success_rate = 0.2+0.6*(1 - self.age/self.max_age)
        else:
            # self.movement_speed = 4.0
            self.hunting_success_rate = 0.2
        
        if not self.alive:
            return
        
        # Intelligent movement - move towards cows if available
        self.intelligent_move(ecosystem_state)
        
        # Consume energy
        self.energy -= self.energy_consumption
        
        # Find and hunt cows
        self._hunt_cows(ecosystem_state.get('cow_list', []))
        
        # Age increases
        self.age_one_step()
        
        # Death check
        if self.energy <= 0:
            self.die_from_starvation()
    
    def _hunt_cows(self, cow_list: List['Cow']) -> None:
        """Hunt cows"""
        for cow in cow_list:
            if cow.alive and self.position.distance_to(cow.position) <= self.hunting_range:
                # Attempt to hunt
                if random.random() < self.hunting_success_rate:
                    # Successful hunt, gain energy
                    self.energy = min(self.max_energy, self.energy + cow.energy)
                    cow.die_from_predation("Tiger")
                    # Start hunting cooldown - tiger will stay still for a period
                    self.start_hunting_cooldown()
                    break  # Only hunt one cow at a time
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                self.age > 30)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Tiger']:
        """Reproduce to create new tiger"""
        super().reproduce(ecosystem_state)
        
        if not self.can_reproduce():
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 800
        
        # Generate new tiger at nearby random position
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        new_x = max(0, min(world_width, self.position.x + random.uniform(-40, 40)))
        new_y = max(0, min(world_height, self.position.y + random.uniform(-40, 40)))
        
        new_position = Position(new_x, new_y)
        return Tiger(new_position)