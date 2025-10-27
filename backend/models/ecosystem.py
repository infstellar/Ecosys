"""
Ecosystem Data Model
Manages the entire ecosystem state and data
"""

import random
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from .species import Grass, Cow, Tiger, Position, Species


# Pydantic Models for Type Safety and C++ Migration
class SpeciesType(str, Enum):
    GRASS = "grass"
    COW = "cow"
    TIGER = "tiger"


class PositionData(BaseModel):
    x: float
    y: float


class BaseIndividualData(BaseModel):
    id: int
    position: PositionData
    energy: float
    age: int
    alive: bool
    max_energy: Optional[float] = None


class SpeciesPopulationData(BaseModel):
    species_data: Dict[str, List[BaseIndividualData]] = Field(default_factory=dict)


class SpeciesStatistics(BaseModel):
    statistics: Dict[SpeciesType, int] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        # 初始化所有物种的统计为0
        for species_type in SpeciesType:
            if species_type not in self.statistics:
                self.statistics[species_type] = 0
    
    def increment(self, species_type: SpeciesType, count: int = 1):
        """增加指定物种的计数"""
        if species_type not in self.statistics:
            self.statistics[species_type] = 0
        self.statistics[species_type] += count
    
    def set_count(self, species_type: SpeciesType, count: int):
        """设置指定物种的计数"""
        self.statistics[species_type] = count
    
    def get_count(self, species_type: SpeciesType) -> int:
        """获取指定物种的计数"""
        return self.statistics.get(species_type, 0)
    
    def reset(self):
        """重置所有统计"""
        for species_type in SpeciesType:
            self.statistics[species_type] = 0
    
    # 为了向后兼容，保留属性访问方式
    @property
    def grass(self) -> int:
        return self.get_count(SpeciesType.GRASS)
    
    @grass.setter
    def grass(self, value: int):
        self.set_count(SpeciesType.GRASS, value)
    
    @property
    def cow(self) -> int:
        return self.get_count(SpeciesType.COW)
    
    @cow.setter
    def cow(self, value: int):
        self.set_count(SpeciesType.COW, value)
    
    @property
    def tiger(self) -> int:
        return self.get_count(SpeciesType.TIGER)
    
    @tiger.setter
    def tiger(self, value: int):
        self.set_count(SpeciesType.TIGER, value)


class EcosystemStateData(BaseModel):
    world_width: int
    world_height: int
    grass_list: List[Species]
    cow_list: List[Species]
    tiger_list: List[Species]
    time_step: int
    grass_positions_array: Optional[np.ndarray] = None
    alive_grass_objects: List[Species] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True  # Allow numpy arrays and custom types


class SpeciesRegistry:
    """物种注册表管理类"""
    
    def __init__(self, config: 'EcosystemConfig'):
        self._registry = {}
        self._register_species('grass', Grass, config.initial_grass)
        self._register_species('cow', Cow, config.initial_cows)
        self._register_species('tiger', Tiger, config.initial_tigers)
    
    def _register_species(self, name: str, species_class: type, initial_count: int):
        """注册一个物种"""
        self._registry[name] = {
            'class': species_class,
            'list': [],
            'initial_count': initial_count
        }
    
    def get_species_list(self, species_name: str) -> List[Species]:
        """获取指定物种的列表"""
        return self._registry[species_name]['list']
    
    def get_species_class(self, species_name: str) -> type:
        """获取指定物种的类"""
        return self._registry[species_name]['class']
    
    def get_initial_count(self, species_name: str) -> int:
        """获取指定物种的初始数量"""
        return self._registry[species_name]['initial_count']
    
    def get_all_species_names(self) -> List[str]:
        """获取所有物种名称"""
        return list(self._registry.keys())
    
    def add_individual(self, species_name: str, individual: Species):
        """添加个体到指定物种"""
        self._registry[species_name]['list'].append(individual)
    
    def extend_individuals(self, species_name: str, individuals: List[Species]):
        """批量添加个体到指定物种"""
        self._registry[species_name]['list'].extend(individuals)
    
    def clear_species(self, species_name: str):
        """清空指定物种"""
        self._registry[species_name]['list'].clear()
    
    def clear_all(self):
        """清空所有物种"""
        for info in self._registry.values():
            info['list'].clear()
    
    def get_species_count(self, species_name: str) -> int:
        """获取指定物种的数量"""
        return len(self._registry[species_name]['list'])
    
    def get_total_count(self) -> int:
        """获取所有物种的总数量"""
        return sum(len(info['list']) for info in self._registry.values())
    
    def filter_alive(self, species_name: str):
        """过滤掉死亡的个体"""
        self._registry[species_name]['list'] = [
            individual for individual in self._registry[species_name]['list'] 
            if individual.alive
        ]
    
    def filter_all_alive(self):
        """过滤掉所有物种中死亡的个体"""
        for species_name in self.get_all_species_names():
            self.filter_alive(species_name)


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
        
        # 使用SpeciesRegistry统一管理物种
        self.species_registry = SpeciesRegistry(config)
        
        # Statistics using Pydantic models
        self.births = SpeciesStatistics()
        self.deaths = SpeciesStatistics()
        self.population_history = []
        
        # Initialize populations
        self._initialize_populations()
    
    def _initialize_populations(self):
        """Initialize populations using unified logic"""
        for species_name in self.species_registry.get_all_species_names():
            species_class = self.species_registry.get_species_class(species_name)
            initial_count = self.species_registry.get_initial_count(species_name)
            
            for _ in range(initial_count):
                position = Position(
                    random.randint(0, self.config.world_width),
                    random.randint(0, self.config.world_height)
                )
                individual = species_class(position)
                self.species_registry.add_individual(species_name, individual)
    
    def get_ecosystem_state(self) -> EcosystemStateData:
        """Get ecosystem state using Pydantic model for species updates"""
        # Precompute grass positions for numpy optimization
        grass_list = self.species_registry.get_species_list('grass')
        alive_grass_positions = []
        alive_grass_objects = []
        for grass in grass_list:
            if grass.alive:
                alive_grass_positions.append([grass.position.x, grass.position.y])
                alive_grass_objects.append(grass)
        
        grass_positions_array = np.array(alive_grass_positions) if alive_grass_positions else np.empty((0, 2))
        
        return EcosystemStateData(
            world_width=self.config.world_width,
            world_height=self.config.world_height,
            grass_list=self.species_registry.get_species_list('grass'),
            cow_list=self.species_registry.get_species_list('cow'),
            tiger_list=self.species_registry.get_species_list('tiger'),
            time_step=self.time_step,
            grass_positions_array=grass_positions_array,
            alive_grass_objects=alive_grass_objects
        )
    
    def update_species(self, ecosystem_state: EcosystemStateData):
        """Update species lists using unified logic"""
        for species_name in self.species_registry.get_all_species_names():
            species_list = self.species_registry.get_species_list(species_name)
            
            # Update each individual in the species
            for individual in species_list[:]:
                individual.update(ecosystem_state)
    
    def handle_reproduction(self):
        """Handle reproduction for all species using unified logic"""
        ecosystem_state = self.get_ecosystem_state()
        
        for species_name in self.species_registry.get_all_species_names():
            species_list = self.species_registry.get_species_list(species_name)
            new_individuals = []
            
            for individual in species_list[:]:
                if individual.can_reproduce():
                    offspring = individual.reproduce(ecosystem_state)
                    if offspring:
                        new_individuals.append(offspring)
            
            # Add new individuals to the species list
            self.species_registry.extend_individuals(species_name, new_individuals)
            
            # Record birth counts using enum-driven approach
            species_type = SpeciesType(species_name)
            self.births.increment(species_type, len(new_individuals))
            
            # Log reproduction events
            if len(new_individuals) > 0:
                species_emoji = {'grass': '🌱', 'cow': '🐄', 'tiger': '🐅'}
                print(f"{species_emoji.get(species_name, '🔸')} {len(new_individuals)} new {species_name} individuals born")
    
    def update_statistics(self):
        """Update statistics"""
        counts = self.get_species_counts()
        self.population_history.append(counts.model_dump())
        
        # Keep history data within reasonable range
        if len(self.population_history) > 100:
            self.population_history = self.population_history[-100:]
    
    def cleanup_dead(self):
        """Remove dead individuals from all species using unified logic"""
        for species_name in self.species_registry.get_all_species_names():
            species_list = self.species_registry.get_species_list(species_name)
            
            # Count deaths before filtering
            dead_count = sum(1 for individual in species_list if not individual.alive)
            
            # Record death counts using enum-driven approach
            species_type = SpeciesType(species_name)
            self.deaths.increment(species_type, dead_count)
            
            # Filter out dead individuals
            self.species_registry.filter_alive(species_name)
            
            # Log deaths if any occurred
            if dead_count > 0:
                species_emoji = {'grass': '🌱', 'cow': '🐄', 'tiger': '🐅'}
                print(f"💀 {dead_count} {species_name} individuals died")
    
    def get_species_counts(self) -> SpeciesStatistics:
        """Get current population counts for all species using Pydantic model"""
        stats = SpeciesStatistics()
        for species_name in self.species_registry.get_all_species_names():
            species_type = SpeciesType(species_name)
            count = self.species_registry.get_species_count(species_name)
            stats.set_count(species_type, count)
        return stats
    
    def get_species_data(self) -> SpeciesPopulationData:
        """Get detailed data for all species using unified Pydantic models"""
        species_data = SpeciesPopulationData()
        
        # Process all species using unified logic
        for species_name in self.species_registry.get_all_species_names():
            species_data.species_data[species_name] = []
            
            for individual in self.species_registry.get_species_list(species_name):
                if individual.alive:
                    individual_data = BaseIndividualData(
                        id=id(individual),
                        position=PositionData(x=individual.position.x, y=individual.position.y),
                        energy=individual.energy,
                        age=individual.age,
                        alive=individual.alive,
                        max_energy=individual.max_energy
                    )
                    species_data.species_data[species_name].append(individual_data)
        
        return species_data
    
    def reset(self, config: EcosystemConfig = None):
        """Reset ecosystem to initial state using unified logic"""
        if config:
            self.config = config
        
        self.time_step = 0
        
        # Clear all species and reinitialize
        self.species_registry.clear_all()
        
        # Reset statistics using Pydantic models
        self.births = SpeciesStatistics()
        self.deaths = SpeciesStatistics()
        self.population_history = []
        
        # Reinitialize populations
        self._initialize_populations()
    
    def check_extinction(self) -> List[str]:
        """Check for extinct species using unified logic"""
        extinct_species = []
        
        for species_name in self.species_registry.get_all_species_names():
            if self.species_registry.get_species_count(species_name) == 0:
                extinct_species.append(species_name)
        
        return extinct_species