#!/usr/bin/env python3
"""
Ecosystem Simulation - Main Entry Point
A comprehensive ecosystem simulation featuring grass, cows, and tigers
"""

import sys
import os
import pygame
import time
from typing import Dict, Any

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.engine.simulation import SimulationEngine
from backend.models.ecosystem import EcosystemConfig
from frontend.renderer.display import DisplayRenderer


class EcosystemApp:
    """Main application class for the ecosystem simulation"""
    
    def __init__(self):
        """Initialize the ecosystem application"""
        # Initialize Pygame
        pygame.init()
        
        # Configuration
        self.config = EcosystemConfig(
            world_width=800,
            world_height=600,
            initial_grass=150,
            initial_cows=20,
            initial_tigers=1
        )
        
        # Initialize components
        self.simulation_engine = SimulationEngine(self.config)
        self.display_renderer = DisplayRenderer(
            self.config.world_width, 
            self.config.world_height
        )
        
        # Application state
        self.running = True
        self.paused = False
        self.simulation_speed = 1.0
        self.last_update_time = time.time()
        
        print("Ecosystem Simulation Initialized Successfully!")
        print("Controls:")
        print("  SPACE - Pause/Resume simulation")
        print("  R - Reset simulation")
        print("  UP/DOWN - Adjust simulation speed")
        print("  ESC/Close Window - Exit")
        print()
    
    def run(self) -> None:
        """Main application loop"""
        print("Starting ecosystem simulation...")
        
        while self.running:
            current_time = time.time()
            
            # Handle events
            self._handle_events()
            
            # Update simulation
            if not self.paused:
                dt = (current_time - self.last_update_time) * self.simulation_speed
                if dt >= 1.0 / 60.0:  # 60 FPS update rate
                    self.simulation_engine.step()
                    self.last_update_time = current_time
            
            # Render
            self._render()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
        
        self._cleanup()
    
    def _handle_events(self) -> None:
        """Handle user input events"""
        events = self.display_renderer.handle_events()
        
        if events['quit']:
            self.running = False
        
        if events['pause']:
            self.paused = not self.paused
            status = "Paused" if self.paused else "Resumed"
            print(f"Simulation {status}")
        
        if events['reset']:
            self._reset_simulation()
        
        if events['speed_up']:
            self.simulation_speed = min(5.0, self.simulation_speed + 0.5)
            print(f"Simulation speed: {self.simulation_speed}x")
        
        if events['speed_down']:
            self.simulation_speed = max(0.1, self.simulation_speed - 0.5)
            print(f"Simulation speed: {self.simulation_speed}x")
    
    def _render(self) -> None:
        """Render the current state"""
        # Get simulation data
        data = self.simulation_engine.get_data()
        ecosystem_state = data['ecosystem_state']
        species_counts = data['species_counts']
        
        # Prepare simulation statistics
        simulation_stats = {
            'time': data['statistics']['time_step'],
            'grass_count': species_counts['grass'],
            'cow_count': species_counts['cow'],
            'tiger_count': species_counts['tiger'],
            'speed': data['simulation_speed']
        }
        
        # Prepare ecosystem state with species data
        ecosystem_display_data = {
            'species_data': ecosystem_state
        }
        
        # Render the display
        self.display_renderer.render(ecosystem_display_data, simulation_stats)
    
    def _reset_simulation(self) -> None:
        """Reset the simulation to initial state"""
        print("Resetting simulation...")
        self.simulation_engine = SimulationEngine(self.config)
        self.paused = False
        self.simulation_speed = 1.0
        print("Simulation reset complete!")
    
    def _cleanup(self) -> None:
        """Clean up resources"""
        print("Shutting down ecosystem simulation...")
        self.display_renderer.cleanup()


def main():
    """Main function"""
    try:
        app = EcosystemApp()
        app.run()
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()