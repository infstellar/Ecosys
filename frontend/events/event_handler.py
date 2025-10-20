"""
Event Handler for the Ecosystem Simulator
Manages user input and system events
"""

import pygame
from typing import Callable, Dict, List, Any, Optional
from enum import Enum


class EventType(Enum):
    """Custom event types for the simulator"""
    SIMULATION_START = "simulation_start"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_RESET = "simulation_reset"
    SPEED_CHANGE = "speed_change"
    CONFIG_CHANGE = "config_change"
    SPECIES_CLICK = "species_click"
    WORLD_CLICK = "world_click"


class EventHandler:
    """Main event handler for the ecosystem simulator"""
    
    def __init__(self):
        self.event_callbacks: Dict[EventType, List[Callable]] = {}
        self.pygame_callbacks: Dict[int, List[Callable]] = {}
        self.mouse_handlers: List[Callable] = []
        self.keyboard_handlers: List[Callable] = []
        
        # Initialize callback lists
        for event_type in EventType:
            self.event_callbacks[event_type] = []
    
    def register_callback(self, event_type: EventType, callback: Callable):
        """Register a callback for a custom event type"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def register_pygame_callback(self, pygame_event_type: int, callback: Callable):
        """Register a callback for a pygame event type"""
        if pygame_event_type not in self.pygame_callbacks:
            self.pygame_callbacks[pygame_event_type] = []
        self.pygame_callbacks[pygame_event_type].append(callback)
    
    def register_mouse_handler(self, handler: Callable):
        """Register a mouse event handler"""
        self.mouse_handlers.append(handler)
    
    def register_keyboard_handler(self, handler: Callable):
        """Register a keyboard event handler"""
        self.keyboard_handlers.append(handler)
    
    def emit_event(self, event_type: EventType, data: Any = None):
        """Emit a custom event"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    if data is not None:
                        callback(data)
                    else:
                        callback()
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    def handle_pygame_events(self, events: List[pygame.event.Event]) -> bool:
        """
        Handle pygame events
        Returns True if quit event was received
        """
        should_quit = False
        
        for event in events:
            # Handle quit event
            if event.type == pygame.QUIT:
                should_quit = True
                continue
            
            # Handle registered pygame callbacks
            if event.type in self.pygame_callbacks:
                for callback in self.pygame_callbacks[event.type]:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"Error in pygame callback: {e}")
            
            # Handle mouse events
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION]:
                for handler in self.mouse_handlers:
                    try:
                        if handler(event):
                            break  # Event was consumed
                    except Exception as e:
                        print(f"Error in mouse handler: {e}")
            
            # Handle keyboard events
            if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                for handler in self.keyboard_handlers:
                    try:
                        if handler(event):
                            break  # Event was consumed
                    except Exception as e:
                        print(f"Error in keyboard handler: {e}")
        
        return should_quit
    
    def clear_callbacks(self):
        """Clear all registered callbacks"""
        for event_type in EventType:
            self.event_callbacks[event_type] = []
        self.pygame_callbacks = {}
        self.mouse_handlers = []
        self.keyboard_handlers = []


class SimulationEventHandler:
    """Specialized event handler for simulation control"""
    
    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler
        self.simulation_running = False
        self.simulation_speed = 1.0
        self.config = {}
        
        # Register keyboard shortcuts
        self.event_handler.register_keyboard_handler(self._handle_keyboard_shortcuts)
    
    def _handle_keyboard_shortcuts(self, event: pygame.event.Event) -> bool:
        """Handle keyboard shortcuts for simulation control"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Space bar toggles simulation
                if self.simulation_running:
                    self.event_handler.emit_event(EventType.SIMULATION_PAUSE)
                else:
                    self.event_handler.emit_event(EventType.SIMULATION_START)
                return True
            
            elif event.key == pygame.K_r:
                # R key resets simulation
                self.event_handler.emit_event(EventType.SIMULATION_RESET)
                return True
            
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Plus key increases speed
                new_speed = min(5.0, self.simulation_speed + 0.5)
                self.event_handler.emit_event(EventType.SPEED_CHANGE, new_speed)
                return True
            
            elif event.key == pygame.K_MINUS:
                # Minus key decreases speed
                new_speed = max(0.1, self.simulation_speed - 0.5)
                self.event_handler.emit_event(EventType.SPEED_CHANGE, new_speed)
                return True
        
        return False
    
    def set_simulation_state(self, running: bool):
        """Update simulation running state"""
        self.simulation_running = running
    
    def set_simulation_speed(self, speed: float):
        """Update simulation speed"""
        self.simulation_speed = speed
    
    def update_config(self, config: Dict[str, Any]):
        """Update configuration"""
        self.config = config.copy()


class MouseEventHandler:
    """Specialized handler for mouse interactions with the simulation world"""
    
    def __init__(self, event_handler: EventHandler, world_rect: pygame.Rect):
        self.event_handler = event_handler
        self.world_rect = world_rect
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Register mouse handler
        self.event_handler.register_mouse_handler(self._handle_mouse_events)
    
    def _handle_mouse_events(self, event: pygame.event.Event) -> bool:
        """Handle mouse events in the simulation world"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.world_rect.collidepoint(event.pos):
                if event.button == 1:  # Left click
                    # Convert screen coordinates to world coordinates
                    world_x = event.pos[0] - self.world_rect.x
                    world_y = event.pos[1] - self.world_rect.y
                    
                    self.event_handler.emit_event(EventType.WORLD_CLICK, {
                        'x': world_x,
                        'y': world_y,
                        'screen_pos': event.pos
                    })
                    return True
                
                elif event.button == 3:  # Right click
                    # Start dragging for camera movement (if implemented)
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:  # Right click release
                self.dragging = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Handle camera dragging (if implemented)
                dx = event.pos[0] - self.last_mouse_pos[0]
                dy = event.pos[1] - self.last_mouse_pos[1]
                self.last_mouse_pos = event.pos
                # Emit camera move event if needed
                return True
        
        return False
    
    def update_world_rect(self, world_rect: pygame.Rect):
        """Update the world rectangle for mouse coordinate conversion"""
        self.world_rect = world_rect


class UIEventHandler:
    """Specialized handler for UI component events"""
    
    def __init__(self, event_handler: EventHandler):
        self.event_handler = event_handler
        self.ui_components = []
        
        # Register mouse handler for UI
        self.event_handler.register_mouse_handler(self._handle_ui_mouse_events)
    
    def register_ui_component(self, component):
        """Register a UI component for event handling"""
        self.ui_components.append(component)
    
    def _handle_ui_mouse_events(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for UI components"""
        for component in self.ui_components:
            if hasattr(component, 'handle_event'):
                if component.handle_event(event):
                    return True  # Event was consumed by UI
        return False
    
    def clear_components(self):
        """Clear all registered UI components"""
        self.ui_components = []


class EventManager:
    """Main event manager that coordinates all event handlers"""
    
    def __init__(self, world_rect: pygame.Rect):
        self.main_handler = EventHandler()
        self.simulation_handler = SimulationEventHandler(self.main_handler)
        self.mouse_handler = MouseEventHandler(self.main_handler, world_rect)
        self.ui_handler = UIEventHandler(self.main_handler)
        
        # Setup event forwarding
        self._setup_event_forwarding()
    
    def _setup_event_forwarding(self):
        """Setup event forwarding between handlers"""
        # Forward simulation events
        self.main_handler.register_callback(EventType.SIMULATION_START, 
                                          lambda: self.simulation_handler.set_simulation_state(True))
        self.main_handler.register_callback(EventType.SIMULATION_PAUSE, 
                                          lambda: self.simulation_handler.set_simulation_state(False))
        self.main_handler.register_callback(EventType.SPEED_CHANGE, 
                                          self.simulation_handler.set_simulation_speed)
    
    def register_simulation_callback(self, event_type: EventType, callback: Callable):
        """Register a callback for simulation events"""
        self.main_handler.register_callback(event_type, callback)
    
    def register_ui_component(self, component):
        """Register a UI component"""
        self.ui_handler.register_ui_component(component)
    
    def emit_event(self, event_type: EventType, data: Any = None):
        """Emit an event"""
        self.main_handler.emit_event(event_type, data)
    
    def handle_events(self) -> bool:
        """Handle all pygame events, returns True if should quit"""
        events = pygame.event.get()
        return self.main_handler.handle_pygame_events(events)
    
    def update_world_rect(self, world_rect: pygame.Rect):
        """Update world rectangle for mouse handling"""
        self.mouse_handler.update_world_rect(world_rect)
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        return {
            'running': self.simulation_handler.simulation_running,
            'speed': self.simulation_handler.simulation_speed,
            'config': self.simulation_handler.config
        }