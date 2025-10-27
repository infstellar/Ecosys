"""
Display Renderer
Handles the rendering of the ecosystem simulation using Pygame
"""

import pygame
import sys
from typing import Dict, Any, List, Optional
from backend.models.species import Grass, Cow, Tiger


class DisplayRenderer:
    """Display renderer class"""
    
    def __init__(self, width: int = 800, height: int = 600):
        """Initialize display renderer"""
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Ecosystem Simulation")
        
        # Colors
        self.colors = {
            'background': (34, 139, 34),  # Forest green
            'grass': (0, 255, 0),         # Green
            'cow': (139, 69, 19),         # Brown
            'tiger': (255, 140, 0),       # Orange
            'text': (255, 255, 255),      # White
            'panel': (50, 50, 50),        # Dark gray
        }
        
        # Font
        try:
            self.font = pygame.font.Font(None, 24)
            self.small_font = pygame.font.Font(None, 18)
        except:
            self.font = pygame.font.SysFont('arial', 24)
            self.small_font = pygame.font.SysFont('arial', 18)
        
        self.clock = pygame.time.Clock()
        self.running = True
    
    def handle_events(self) -> Dict[str, Any]:
        """Handle pygame events"""
        events = {
            'quit': False,
            'pause': False,
            'reset': False,
            'speed_up': False,
            'speed_down': False
        }
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events['quit'] = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    events['pause'] = True
                elif event.key == pygame.K_r:
                    events['reset'] = True
                elif event.key == pygame.K_UP:
                    events['speed_up'] = True
                elif event.key == pygame.K_DOWN:
                    events['speed_down'] = True
        
        return events
    
    def render(self, ecosystem_state: Dict[str, Any], simulation_stats: Dict[str, Any]) -> None:
        """Render the ecosystem"""
        # Clear screen
        self.screen.fill(self.colors['background'])
        
        # Render species
        self._render_species(ecosystem_state)
        
        # Render UI
        self._render_ui(simulation_stats)
        
        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # 60 FPS
    
    def _render_species(self, ecosystem_state: Dict[str, Any]) -> None:
        """Render all species"""
        # Get species data from ecosystem state
        species_data = ecosystem_state.get('species_data', {})
        
        # Render grass
        grass_data = species_data.species_data.get('grass', [])
        for grass in grass_data:
            pygame.draw.circle(
                self.screen, 
                self.colors['grass'],
                (int(grass.position.x), int(grass.position.y)),
                3
            )
        
        # Render cows
        cow_data = species_data.species_data.get('cow', [])
        for cow in cow_data:
            pygame.draw.circle(
                self.screen,
                self.colors['cow'],
                (int(cow.position.x), int(cow.position.y)),
                8
            )
        
        # Render tigers
        tiger_data = species_data.species_data.get('tiger', [])
        for tiger in tiger_data:
            pygame.draw.circle(
                self.screen,
                self.colors['tiger'],
                (int(tiger.position.x), int(tiger.position.y)),
                12
            )
    
    def _render_ui(self, stats: Dict[str, Any]) -> None:
        """Render user interface"""
        # Background panel
        panel_rect = pygame.Rect(10, 10, 250, 150)
        pygame.draw.rect(self.screen, self.colors['panel'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['text'], panel_rect, 2)
        
        # Statistics text
        y_offset = 20
        texts = [
            f"Time: {stats.get('time', 0)}",
            f"Grass: {stats.get('grass_count', 0)}",
            f"Cows: {stats.get('cow_count', 0)}",
            f"Tigers: {stats.get('tiger_count', 0)}",
            f"Speed: {stats.get('speed', 1)}x"
        ]
        
        for text in texts:
            text_surface = self.font.render(text, True, self.colors['text'])
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 25
        
        # Control instructions
        control_texts = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Reset",
            "UP/DOWN - Speed"
        ]
        
        y_offset = self.height - 100
        for text in control_texts:
            text_surface = self.small_font.render(text, True, self.colors['text'])
            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 20
    
    def show_message(self, message: str, duration: int = 2000) -> None:
        """Display message on screen"""
        text_surface = self.font.render(message, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        
        # Background for message
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, self.colors['panel'], bg_rect)
        pygame.draw.rect(self.screen, self.colors['text'], bg_rect, 2)
        
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        
        pygame.time.wait(duration)
    
    def cleanup(self) -> None:
        """Clean up resources"""
        pygame.quit()
        sys.exit()