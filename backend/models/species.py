"""
Species Data Model
Defines the base species class and specific species implementations in the ecosystem
"""

import random
import math
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
    def __init__(self, position: Position, energy: int = 100, max_age: int = 100):
        self.position = position
        self.energy = energy
        self.max_energy = energy
        self.age = 0
        self.max_age = max_age
        self.alive = True
        self.reproduction_cooldown = 0
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update species state"""
        if not self.alive:
            return
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return self.alive and self.energy > self.max_energy * 0.7 and self.reproduction_cooldown <= 0
    
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
            self.alive = False
    
    def die(self) -> None:
        """Death"""
        self.alive = False


class Animal(Species):
    """Animal base class - inherits from Species and adds intelligent movement"""
    
    def __init__(self, position: Position, energy: int = 100, max_age: int = 100):
        super().__init__(position, energy, max_age)
        self.movement_speed = 1.0
        self.detection_range = 500.0  # Range to detect food
        self.food_types = []  # List of food types this animal eats
        self.hunting_cooldown = 0  # Cooldown after hunting/eating
        self.hunting_cooldown_duration = 0  # Duration to stay still after hunting
    
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
        super().__init__(position, energy=50, max_age=200)
        self.growth_rate = 2
        self.reproduction_energy_cost = 20
        self.reproduction_chance = 0.3
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update grass state"""
        if not self.alive:
            return
        
        # Growth gains energy
        self.energy = min(self.max_energy, self.energy + self.growth_rate)
        
        # Age increases
        self.age_one_step()
        
        # Death check from old age
        if self.age >= self.max_age:
            self.die()
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                self.energy >= self.reproduction_energy_cost and
                random.random() < self.reproduction_chance)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Grass']:
        """Reproduce to create new grass"""
        if not self.can_reproduce():
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 10
        
        # Generate new grass at nearby random position
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        new_x = max(0, min(world_width, self.position.x + random.uniform(-50, 50)))
        new_y = max(0, min(world_height, self.position.y + random.uniform(-50, 50)))
        
        new_position = Position(new_x, new_y)
        return Grass(new_position)


class Cow(Animal):
    """Cow class - Primary consumer"""
    
    def __init__(self, position: Position):
        super().__init__(position, energy=100, max_age=150)
        self.movement_speed = 2.0
        self.energy_consumption = 1
        self.reproduction_energy_cost = 40
        self.eating_range = 5.0
        self.detection_range = 800.0  # Cows can detect grass from farther away
        self.food_types = ['grass']  # Cows eat grass
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update cow state"""
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
        if self.energy <= 0 or self.age >= self.max_age:
            self.die()
    
    def _eat_grass(self, grass_list: List['Grass']) -> None:
        """Eat grass"""
        for grass in grass_list:
            # Double check: grass must be alive and within eating range
            if grass.alive and self.position.distance_to(grass.position) <= self.eating_range:
                # Eat grass, gain energy
                self.energy = min(self.max_energy, self.energy + grass.energy)
                grass.die()
                break  # Only eat one grass at a time
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                self.energy >= self.reproduction_energy_cost and
                self.age > 20)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Cow']:
        """Reproduce to create new cow"""
        if not self.can_reproduce():
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 20
        
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
        super().__init__(position, energy=150, max_age=120)
        self.movement_speed = 4.0
        self.energy_consumption = 2
        self.reproduction_energy_cost = 60
        self.hunting_range = 5.0
        self.hunting_success_rate = 0.6
        self.detection_range = 1000.0  # Tigers can detect cows from farther away
        self.food_types = ['cow']  # Tigers eat cows
        self.hunting_cooldown_duration = 15  # Stay still for 30 steps after hunting
    
    def update(self, ecosystem_state: Dict[str, Any]) -> None:
        """Update tiger state"""
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
        if self.energy <= 0 or self.age >= self.max_age:
            self.die()
    
    def _hunt_cows(self, cow_list: List['Cow']) -> None:
        """Hunt cows"""
        for cow in cow_list:
            if cow.alive and self.position.distance_to(cow.position) <= self.hunting_range:
                # Attempt to hunt
                if random.random() < self.hunting_success_rate:
                    # Successful hunt, gain energy
                    self.energy = min(self.max_energy, self.energy + cow.energy)
                    cow.die()
                    # Start hunting cooldown - tiger will stay still for a period
                    self.start_hunting_cooldown()
                    break  # Only hunt one cow at a time
    
    def can_reproduce(self) -> bool:
        """Check if can reproduce"""
        return (super().can_reproduce() and 
                self.energy >= self.reproduction_energy_cost and
                self.age > 30)
    
    def reproduce(self, ecosystem_state: Dict[str, Any]) -> Optional['Tiger']:
        """Reproduce to create new tiger"""
        if not self.can_reproduce():
            return None
        
        # Consume energy
        self.energy -= self.reproduction_energy_cost
        self.reproduction_cooldown = 30
        
        # Generate new tiger at nearby random position
        world_width = ecosystem_state.get('world_width', 800)
        world_height = ecosystem_state.get('world_height', 600)
        
        new_x = max(0, min(world_width, self.position.x + random.uniform(-40, 40)))
        new_y = max(0, min(world_height, self.position.y + random.uniform(-40, 40)))
        
        new_position = Position(new_x, new_y)
        return Tiger(new_position)