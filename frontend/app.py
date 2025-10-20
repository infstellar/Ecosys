"""
Main Application for the Ecosystem Simulator
Integrates all frontend components and implements the main loop
"""

import pygame
import sys
import threading
import time
from typing import Dict, Any, Optional

from frontend.renderer.display import DisplayManager
from frontend.ui.control_panel import ControlPanel, ConfigManager
from frontend.events.event_handler import EventManager, EventType
from backend.interface.api import EcosystemAPI, Command, CommandType, APIHelper
from backend.models.ecosystem import EcosystemConfig


class EcosystemApp:
    """Main application class for the ecosystem simulator"""
    
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.running = False
        self.fps = 60
        
        # Calculate layout
        self.simulation_width = 600
        self.simulation_height = 600
        self.control_panel_width = width - self.simulation_width - 20
        
        # Initialize state
        self.is_running = False
        self.simulation_data = None
        
        # Initialize components
        self.display_manager = DisplayManager(width, height)
        self.config_manager = ConfigManager()
        self.control_panel = ControlPanel(
            self.simulation_width + 20, 10, 
            self.control_panel_width, height - 20
        )
        
        # Create world rect for event handling
        self.world_rect = pygame.Rect(10, 10, self.simulation_width, self.simulation_height)
        
        # Initialize event manager with world rect
        self.event_manager = EventManager(self.world_rect)
        self.api = EcosystemAPI()
        
        # Initialize pygame clock
        self.clock = pygame.time.Clock()
        self.last_update_time = 0
        self.update_interval = 1.0 / 30  # 30 FPS for simulation updates
        
        # Setup event callbacks
        self._setup_event_callbacks()
        
        # Register UI components with event manager
        self.event_manager.register_ui_component(self.control_panel)
        
        # Initialize simulation with default config
        self._initialize_simulation()
    
    def _setup_event_callbacks(self):
        """Setup event callbacks for simulation control"""
        # Control panel callbacks
        self.control_panel.set_callback('start_pause', self._toggle_simulation)
        self.control_panel.set_callback('reset', self._reset_simulation)
        self.control_panel.set_callback('speed_change', self._change_speed)
        self.control_panel.set_callback('grass_count_change', 
                                      lambda count: self._update_config('initial_grass', count))
        self.control_panel.set_callback('cow_count_change', 
                                      lambda count: self._update_config('initial_cows', count))
        self.control_panel.set_callback('tiger_count_change', 
                                      lambda count: self._update_config('initial_tigers', count))
        self.control_panel.set_callback('world_size_change', self._change_world_size)
        
        # Event manager callbacks
        self.event_manager.register_simulation_callback(EventType.SIMULATION_START, self._start_simulation)
        self.event_manager.register_simulation_callback(EventType.SIMULATION_PAUSE, self._pause_simulation)
        self.event_manager.register_simulation_callback(EventType.SIMULATION_RESET, self._reset_simulation)
        self.event_manager.register_simulation_callback(EventType.SPEED_CHANGE, self._change_speed)
        self.event_manager.register_simulation_callback(EventType.WORLD_CLICK, self._handle_world_click)
    
    def _initialize_simulation(self):
        """Initialize the simulation with default configuration"""
        config = self.config_manager.get_config()
        ecosystem_config = EcosystemConfig(
            world_width=config['world_width'],
            world_height=config['world_height'],
            initial_grass_count=config['initial_grass'],
            initial_cow_count=config['initial_cows'],
            initial_tiger_count=config['initial_tigers']
        )
        
        # Initialize backend
        command = Command(CommandType.RESET_SIMULATION, {'config': ecosystem_config})
        response = self.api.execute_command(command)
        
        if response.success:
            self.simulation_data = response.data
            print("Simulation initialized successfully")
        else:
            print(f"Failed to initialize simulation: {response.error}")
    
    def _toggle_simulation(self):
        """Toggle simulation start/pause"""
        if self.api.simulation_engine.is_running:
            self._pause_simulation()
        else:
            self._start_simulation()
    
    def _start_simulation(self):
        """Start the simulation"""
        command = Command(CommandType.START_SIMULATION, {})
        response = self.api.execute_command(command)
        
        if response.success:
            self.is_running = True
            print("Simulation started")
        else:
            print(f"Failed to start simulation: {response.error}")
    
    def _pause_simulation(self):
        """Pause the simulation"""
        command = Command(CommandType.PAUSE_SIMULATION, {})
        response = self.api.execute_command(command)
        
        if response.success:
            self.is_running = False
            print("Simulation paused")
        else:
            print(f"Failed to pause simulation: {response.error}")
    
    def _reset_simulation(self):
        """Reset the simulation"""
        config = self.config_manager.get_config()
        ecosystem_config = EcosystemConfig(
            world_width=config['world_width'],
            world_height=config['world_height'],
            initial_grass_count=config['initial_grass'],
            initial_cow_count=config['initial_cows'],
            initial_tiger_count=config['initial_tigers']
        )
        
        command = Command(CommandType.RESET_SIMULATION, {'config': ecosystem_config})
        response = self.api.execute_command(command)
        
        if response.success:
            self.simulation_data = response.data
            self.is_running = False
            print("Simulation reset")
        else:
            print(f"Failed to reset simulation: {response.error}")
    
    def _change_speed(self, speed: float):
        """Change simulation speed"""
        command = Command(CommandType.SET_SPEED, {'speed': speed})
        response = self.api.execute_command(command)
        
        if response.success:
            print(f"Speed changed to {speed}")
        else:
            print(f"Failed to change speed: {response.error}")
    
    def _update_config(self, key: str, value: Any):
        """Update configuration"""
        self.config_manager.update_config(key, value)
        print(f"Config updated: {key} = {value}")
    
    def _change_world_size(self, size: int):
        """Change world size"""
        self.config_manager.update_config('world_width', size)
        self.config_manager.update_config('world_height', size)
        
        # Update simulation area
        self.simulation_width = size
        self.simulation_height = size
        
        # Recreate world rect
        self.world_rect = pygame.Rect(10, 10, self.simulation_width, self.simulation_height)
    
    def _handle_world_click(self, click_data: Dict[str, Any]):
        """Handle clicks in the simulation world"""
        x, y = click_data['position']
        print(f"World clicked at ({x}, {y})")
    
    def _update_simulation_data(self):
        """Update simulation data from backend"""
        if self.is_running:
            current_time = time.time()
            if current_time - self.last_update_time >= self.update_interval:
                command = Command(CommandType.GET_DATA, {})
                response = self.api.execute_command(command)
                
                if response.success:
                    self.simulation_data = response.data
                    
                    # Update control panel
                    self.control_panel.update_info(self.simulation_data)
                    
                    # Update chart
                    species_data = self.simulation_data.get('species_data', {})
                    species_counts = {
                        'grass': len(species_data.get('grass', [])),
                        'cow': len(species_data.get('cow', [])),
                        'tiger': len(species_data.get('tiger', []))
                    }
                    time_step = self.simulation_data.get('time_step', 0)
                    self.control_panel.update_chart(time_step, species_counts)
                    
                    self.last_update_time = current_time
    
    def _handle_events(self):
        """Handle all events"""
        should_quit = self.event_manager.handle_events()
        if should_quit:
            self.running = False
    
    def _update(self):
        """Update application state"""
        self._update_simulation_data()
    
    def _render(self):
        """Render the application"""
        # Clear screen
        self.display_manager.clear_screen()
        
        # Render simulation area
        if self.simulation_data:
            species_data = self.simulation_data.get('species_data', {})
            self.display_manager.draw_simulation_area(species_data)
        
        # Render control panel
        if self.simulation_data:
            self.display_manager.draw_control_panel(self.simulation_data)
        
        # Update display
        self.display_manager.update_display()
    
    def run(self):
        """Main application loop"""
        self.running = True
        print("Starting Ecosystem Simulator...")
        print("Controls:")
        print("  Space: Start/Pause simulation")
        print("  R: Reset simulation")
        print("  +/-: Increase/Decrease speed")
        print("  Mouse: Click on controls or simulation area")
        
        while self.running:
            # Handle events
            self._handle_events()
            
            # Update
            self._update()
            
            # Render
            self._render()
            
            # Control frame rate
            self.clock.tick(self.fps)
        
        # Cleanup
        self._cleanup()
    
    def _cleanup(self):
        """Cleanup resources"""
        # Stop simulation
        if self.api.simulation_engine.is_running:
            self.api.execute_command(Command(CommandType.PAUSE_SIMULATION, {}))
        
        pygame.quit()
        print("Ecosystem Simulator closed")


def main():
    """Main entry point"""
    try:
        app = EcosystemApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()