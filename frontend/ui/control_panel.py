"""
Control Panel UI
Provides user interface controls for the ecosystem simulation
"""

import pygame
from typing import Dict, Any, Callable, Optional


class Button:
    """Button UI component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False
        
        # Colors
        self.colors = {
            'normal': (70, 130, 180),
            'hover': (100, 149, 237),
            'pressed': (50, 110, 160),
            'text': (255, 255, 255),
            'border': (128, 128, 128)
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle button events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                self.is_pressed = False
                return True
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the button"""
        # Choose color based on state
        if self.is_pressed:
            color = self.colors['pressed']
        elif self.is_hovered:
            color = self.colors['hover']
        else:
            color = self.colors['normal']
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.colors['border'], self.rect, 2)
        
        # Draw text
        text_surface = font.render(self.text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class Slider:
    """Slider UI component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float, label: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        
        # Colors
        self.colors = {
            'track': (128, 128, 128),
            'handle': (70, 130, 180),
            'handle_hover': (100, 149, 237),
            'text': (0, 0, 0)
        }
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle slider events"""
        handle_rect = self._get_handle_rect()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update value based on mouse position
            relative_x = event.pos[0] - self.rect.x
            ratio = max(0, min(1, relative_x / self.rect.width))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)
            return True
        
        return False
    
    def _get_handle_rect(self) -> pygame.Rect:
        """Get the handle rectangle"""
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * self.rect.width) - 5
        return pygame.Rect(handle_x, self.rect.y, 10, self.rect.height)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the slider"""
        # Draw track
        track_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height // 2 - 2, 
                                self.rect.width, 4)
        pygame.draw.rect(screen, self.colors['track'], track_rect)
        
        # Draw handle
        handle_rect = self._get_handle_rect()
        color = self.colors['handle_hover'] if self.dragging else self.colors['handle']
        pygame.draw.rect(screen, color, handle_rect)
        
        # Draw label and value
        label_text = f"{self.label}: {self.value:.1f}"
        text_surface = font.render(label_text, True, self.colors['text'])
        screen.blit(text_surface, (self.rect.x, self.rect.y - 20))


class ConfigManager:
    """Configuration manager for simulation parameters"""
    
    def __init__(self):
        self.config = {
            'world_width': 800,
            'world_height': 600,
            'initial_grass': 100,
            'initial_cows': 20,
            'initial_tigers': 5,
            'simulation_speed': 1.0
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, key: str, value: Any) -> None:
        """Update configuration parameter"""
        if key in self.config:
            self.config[key] = value
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = {
            'world_width': 800,
            'world_height': 600,
            'initial_grass': 100,
            'initial_cows': 20,
            'initial_tigers': 5,
            'simulation_speed': 1.0
        }


class ControlPanel:
    """Main control panel for the simulation"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.config_manager = ConfigManager()
        
        # UI components
        self.buttons = {}
        self.sliders = {}
        
        # Initialize UI components
        self._init_components()
        
        # Colors
        self.colors = {
            'background': (220, 220, 220),
            'border': (128, 128, 128),
            'text': (0, 0, 0)
        }
        
        # Font
        try:
            self.font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('arial', 20)
            self.title_font = pygame.font.SysFont('arial', 24)
    
    def _init_components(self) -> None:
        """Initialize UI components"""
        button_width = 100
        button_height = 30
        button_spacing = 10
        
        # Control buttons
        y_offset = 50
        self.buttons['start'] = Button(
            self.rect.x + 10, self.rect.y + y_offset,
            button_width, button_height, "Start"
        )
        
        self.buttons['pause'] = Button(
            self.rect.x + 120, self.rect.y + y_offset,
            button_width, button_height, "Pause"
        )
        
        y_offset += button_height + button_spacing
        self.buttons['reset'] = Button(
            self.rect.x + 10, self.rect.y + y_offset,
            button_width, button_height, "Reset"
        )
        
        self.buttons['step'] = Button(
            self.rect.x + 120, self.rect.y + y_offset,
            button_width, button_height, "Step"
        )
        
        # Configuration sliders
        y_offset += 60
        slider_width = 200
        slider_height = 20
        
        self.sliders['speed'] = Slider(
            self.rect.x + 10, self.rect.y + y_offset,
            slider_width, slider_height, 0.1, 5.0, 1.0, "Speed"
        )
        
        y_offset += 50
        self.sliders['grass'] = Slider(
            self.rect.x + 10, self.rect.y + y_offset,
            slider_width, slider_height, 10, 500, 100, "Initial Grass"
        )
        
        y_offset += 50
        self.sliders['cows'] = Slider(
            self.rect.x + 10, self.rect.y + y_offset,
            slider_width, slider_height, 1, 100, 20, "Initial Cows"
        )
        
        y_offset += 50
        self.sliders['tigers'] = Slider(
            self.rect.x + 10, self.rect.y + y_offset,
            slider_width, slider_height, 1, 50, 5, "Initial Tigers"
        )
    
    def handle_event(self, event: pygame.event.Event) -> Dict[str, Any]:
        """Handle control panel events"""
        events = {}
        
        # Handle button events
        for name, button in self.buttons.items():
            if button.handle_event(event):
                events[name] = True
        
        # Handle slider events
        for name, slider in self.sliders.items():
            if slider.handle_event(event):
                # Update configuration
                if name == 'speed':
                    self.config_manager.update_config('simulation_speed', slider.value)
                elif name == 'grass':
                    self.config_manager.update_config('initial_grass', int(slider.value))
                elif name == 'cows':
                    self.config_manager.update_config('initial_cows', int(slider.value))
                elif name == 'tigers':
                    self.config_manager.update_config('initial_tigers', int(slider.value))
                
                events['config_changed'] = True
        
        return events
    
    def draw(self, screen: pygame.Surface, simulation_stats: Dict[str, Any]) -> None:
        """Draw the control panel"""
        # Draw background
        pygame.draw.rect(screen, self.colors['background'], self.rect)
        pygame.draw.rect(screen, self.colors['border'], self.rect, 2)
        
        # Draw title
        title_text = self.title_font.render("Control Panel", True, self.colors['text'])
        screen.blit(title_text, (self.rect.x + 10, self.rect.y + 10))
        
        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen, self.font)
        
        # Draw sliders
        for slider in self.sliders.values():
            slider.draw(screen, self.font)
        
        # Draw simulation statistics
        self._draw_statistics(screen, simulation_stats)
    
    def _draw_statistics(self, screen: pygame.Surface, stats: Dict[str, Any]) -> None:
        """Draw simulation statistics"""
        y_offset = self.rect.y + 350
        
        # Statistics title
        stats_title = self.font.render("Statistics:", True, self.colors['text'])
        screen.blit(stats_title, (self.rect.x + 10, y_offset))
        y_offset += 25
        
        # Population counts
        stats_text = [
            f"Time: {stats.get('time', 0)}",
            f"Grass: {stats.get('grass_count', 0)}",
            f"Cows: {stats.get('cow_count', 0)}",
            f"Tigers: {stats.get('tiger_count', 0)}",
            f"Total: {stats.get('total_count', 0)}"
        ]
        
        for text in stats_text:
            text_surface = self.font.render(text, True, self.colors['text'])
            screen.blit(text_surface, (self.rect.x + 10, y_offset))
            y_offset += 20
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config_manager.get_config()
    
    def set_button_callback(self, button_name: str, callback: Callable) -> None:
        """Set callback for a button"""
        if button_name in self.buttons:
            self.buttons[button_name].callback = callback