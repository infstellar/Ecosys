"""
Ecosystem Simulation Engine
Manages the entire ecosystem simulation process and time stepping
"""

import time
import threading
from typing import Callable, Optional, Dict, Any
from ..models.ecosystem import EcosystemState, EcosystemConfig


class SimulationEngine:
    """Ecosystem Simulation Engine"""
    
    def __init__(self, config: EcosystemConfig):
        self.config = config
        self.ecosystem = EcosystemState(config)
        
        # Simulation parameters
        self.is_running = False
        self.is_paused = False
        self.simulation_speed = 1.0  # Simulation speed multiplier
        self.target_fps = 30  # Target frame rate
        
        # Callback functions
        self.update_callback: Optional[Callable] = None
        self.extinction_callback: Optional[Callable] = None
        
        # Thread control
        self.simulation_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
    
    def set_update_callback(self, callback: Callable):
        """Set update callback function"""
        self.update_callback = callback
    
    def set_extinction_callback(self, callback: Callable):
        """Set extinction callback function"""
        self.extinction_callback = callback
    
    def start(self):
        """Start simulation"""
        if self.is_running:
            return
        
        self.is_running = True
        self.is_paused = False
        self.stop_event.clear()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def pause(self):
        """Pause simulation"""
        self.is_paused = True
    
    def resume(self):
        """Resume simulation"""
        self.is_paused = False
    
    def stop(self):
        """Stop simulation"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.is_paused = False
        self.stop_event.set()
        
        if self.simulation_thread and self.simulation_thread.is_alive():
            self.simulation_thread.join()
    
    def reset(self, new_config: Optional[EcosystemConfig] = None):
        """Reset simulation"""
        was_running = self.is_running
        
        # Stop current simulation
        self.stop()
        
        # Reset ecosystem
        if new_config:
            self.config = new_config
        self.ecosystem = EcosystemState(self.config)
        
        # If it was running before, restart
        if was_running:
            self.start()
    
    def step(self):
        """Execute single simulation step"""
        if self.is_running:
            return  # If running, don't execute single step
        
        self._update_ecosystem()
    
    def set_speed(self, speed: float):
        """Set simulation speed"""
        self.simulation_speed = max(0.1, min(5.0, speed))
    
    def get_data(self) -> Dict[str, Any]:
        """Get simulation data"""
        return {
            'ecosystem_state': self.ecosystem.get_species_data(),
            'species_counts': self.ecosystem.get_species_counts(),
            'statistics': {
                'time_step': self.ecosystem.time_step,
                'births': self.ecosystem.births,
                'deaths': self.ecosystem.deaths,
                'population_history': self.ecosystem.population_history
            },
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'simulation_speed': self.simulation_speed
        }
    
    def update_config(self, new_config: EcosystemConfig):
        """Update configuration"""
        self.config = new_config
        # Note: This doesn't reset the ecosystem, just updates the config
    
    def _simulation_loop(self):
        """Simulation main loop"""
        last_time = time.time()
        
        while self.is_running and not self.stop_event.is_set():
            if not self.is_paused:
                current_time = time.time()
                
                # Update ecosystem
                self._update_ecosystem()
                
                # Call update callback
                if self.update_callback:
                    self.update_callback(self.get_data())
                
                # Check extinction
                extinct_species = self.ecosystem.check_extinction()
                if extinct_species and self.extinction_callback:
                    self.extinction_callback(extinct_species)
                
                last_time = current_time
            
            # Control frame rate
            sleep_time = (1.0 / self.target_fps) / self.simulation_speed
            time.sleep(sleep_time)
    
    def _update_ecosystem(self):
        """Update ecosystem state"""
        
        # Get ecosystem state
        ecosystem_state = self.ecosystem.get_ecosystem_state()
        
        # Update all species
        self.ecosystem.update_species(ecosystem_state)
        
        # Handle reproduction
        self.ecosystem.handle_reproduction()
        
        # Clean up dead individuals
        self.ecosystem.cleanup_dead()
        
        # Update statistics
        self.ecosystem.update_statistics()
        
        # Increment time step
        self.ecosystem.time_step += 1


class SimulationController:
    """Simulation Controller - Provides simplified interface"""
    
    def __init__(self, config: EcosystemConfig):
        self.engine = SimulationEngine(config)
        self.callbacks = {
            'update': [],
            'extinction': []
        }
    
    def start(self):
        """Start simulation"""
        self.engine.start()
    
    def pause(self):
        """Pause simulation"""
        self.engine.pause()
    
    def resume(self):
        """Resume simulation"""
        self.engine.resume()
    
    def stop(self):
        """Stop simulation"""
        self.engine.stop()
    
    def reset(self, config: Optional[EcosystemConfig] = None):
        """Reset simulation"""
        self.engine.reset(config)
    
    def step(self):
        """Execute single step"""
        self.engine.step()
    
    def set_speed(self, speed: float):
        """Set speed"""
        self.engine.set_speed(speed)
    
    def get_data(self) -> Dict[str, Any]:
        """Get data"""
        return self.engine.get_data()
    
    def update_config(self, config: EcosystemConfig):
        """Update configuration"""
        self.engine.update_config(config)
    
    def set_callbacks(self, update_callback=None, extinction_callback=None):
        """Set callback functions"""
        if update_callback:
            self.engine.set_update_callback(update_callback)
        if extinction_callback:
            self.engine.set_extinction_callback(extinction_callback)
    
    def is_running(self) -> bool:
        """Check if running"""
        return self.engine.is_running
    
    def is_paused(self) -> bool:
        """Check if paused"""
        return self.engine.is_paused