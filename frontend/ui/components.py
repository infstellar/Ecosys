"""
UI Components for the Ecosystem Simulator
Provides interactive components like buttons, sliders, and panels
"""

import pygame
from typing import Callable, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class ButtonStyle:
    """Button styling configuration"""
    bg_color: Tuple[int, int, int] = (70, 130, 180)
    hover_color: Tuple[int, int, int] = (100, 149, 237)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    border_color: Tuple[int, int, int] = (0, 0, 0)
    border_width: int = 2
    font_size: int = 16


class Button:
    """Interactive button component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Callable[[], None], 
                 style: Optional[ButtonStyle] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.style = style or ButtonStyle()
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.Font(None, self.style.font_size)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, returns True if event was consumed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.callback()
                self.is_pressed = False
                return True
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the button"""
        color = self.style.hover_color if self.is_hovered else self.style.bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.style.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


@dataclass
class SliderStyle:
    """Slider styling configuration"""
    track_color: Tuple[int, int, int] = (128, 128, 128)
    handle_color: Tuple[int, int, int] = (70, 130, 180)
    handle_hover_color: Tuple[int, int, int] = (100, 149, 237)
    text_color: Tuple[int, int, int] = (0, 0, 0)
    font_size: int = 14


class Slider:
    """Interactive slider component"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: float, max_value: float, initial_value: float,
                 label: str, callback: Optional[Callable[[float], None]] = None,
                 style: Optional[SliderStyle] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.label = label
        self.callback = callback
        self.style = style or SliderStyle()
        self.is_dragging = False
        self.is_hovered = False
        self.font = pygame.font.Font(None, self.style.font_size)
        
        # Handle dimensions
        self.handle_width = 20
        self.handle_height = height
        self.track_rect = pygame.Rect(x, y + height // 4, width, height // 2)
        
    def _value_to_pos(self, value: float) -> int:
        """Convert value to handle position"""
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        return int(self.track_rect.x + ratio * (self.track_rect.width - self.handle_width))
    
    def _pos_to_value(self, pos: int) -> float:
        """Convert handle position to value"""
        ratio = (pos - self.track_rect.x) / (self.track_rect.width - self.handle_width)
        ratio = max(0, min(1, ratio))
        return self.min_value + ratio * (self.max_value - self.min_value)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, returns True if event was consumed"""
        handle_x = self._value_to_pos(self.value)
        handle_rect = pygame.Rect(handle_x, self.track_rect.y, 
                                self.handle_width, self.handle_height)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos):
                self.is_dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging:
                self.is_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                new_value = self._pos_to_value(event.pos[0])
                if new_value != self.value:
                    self.value = new_value
                    if self.callback:
                        self.callback(self.value)
                return True
            else:
                self.is_hovered = handle_rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the slider"""
        # Draw track
        pygame.draw.rect(screen, self.style.track_color, self.track_rect)
        
        # Draw handle
        handle_x = self._value_to_pos(self.value)
        handle_rect = pygame.Rect(handle_x, self.track_rect.y, 
                                self.handle_width, self.handle_height)
        color = self.style.handle_hover_color if self.is_hovered else self.style.handle_color
        pygame.draw.rect(screen, color, handle_rect)
        
        # Draw label and value
        label_text = f"{self.label}: {self.value:.1f}"
        text_surface = self.font.render(label_text, True, self.style.text_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.rect.centerx
        text_rect.bottom = self.track_rect.top - 5
        screen.blit(text_surface, text_rect)


@dataclass
class PanelStyle:
    """Panel styling configuration"""
    bg_color: Tuple[int, int, int] = (240, 240, 240)
    border_color: Tuple[int, int, int] = (0, 0, 0)
    border_width: int = 2
    title_color: Tuple[int, int, int] = (0, 0, 0)
    title_font_size: int = 18


class Panel:
    """Container panel for UI components"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", style: Optional[PanelStyle] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.style = style or PanelStyle()
        self.components = []
        self.title_font = pygame.font.Font(None, self.style.title_font_size)
        
    def add_component(self, component):
        """Add a UI component to the panel"""
        self.components.append(component)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all components in the panel"""
        for component in self.components:
            if hasattr(component, 'handle_event'):
                if component.handle_event(event):
                    return True
        return False
    
    def draw(self, screen: pygame.Surface):
        """Draw the panel and all its components"""
        # Draw panel background
        pygame.draw.rect(screen, self.style.bg_color, self.rect)
        pygame.draw.rect(screen, self.style.border_color, self.rect, self.style.border_width)
        
        # Draw title
        if self.title:
            title_surface = self.title_font.render(self.title, True, self.style.title_color)
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.rect.centerx
            title_rect.top = self.rect.top + 10
            screen.blit(title_surface, title_rect)
        
        # Draw all components
        for component in self.components:
            if hasattr(component, 'draw'):
                component.draw(screen)


class InfoDisplay:
    """Display information text"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 font_size: int = 14, text_color: Tuple[int, int, int] = (0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.lines = []
        
    def set_text(self, text: str):
        """Set the display text"""
        self.lines = text.split('\n')
    
    def add_line(self, line: str):
        """Add a line of text"""
        self.lines.append(line)
    
    def clear(self):
        """Clear all text"""
        self.lines = []
    
    def draw(self, screen: pygame.Surface):
        """Draw the text"""
        y_offset = self.rect.top
        line_height = self.font.get_height() + 2
        
        for line in self.lines:
            if y_offset + line_height > self.rect.bottom:
                break
            
            text_surface = self.font.render(line, True, self.text_color)
            screen.blit(text_surface, (self.rect.left, y_offset))
            y_offset += line_height


class Chart:
    """Simple line chart for displaying data over time"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", max_points: int = 100):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.max_points = max_points
        self.data_series = {}  # {series_name: [(x, y), ...]}
        self.colors = {
            'grass': (34, 139, 34),
            'cow': (139, 69, 19),
            'tiger': (255, 140, 0)
        }
        self.font = pygame.font.Font(None, 16)
        
    def add_data_point(self, series_name: str, x: float, y: float):
        """Add a data point to a series"""
        if series_name not in self.data_series:
            self.data_series[series_name] = []
        
        self.data_series[series_name].append((x, y))
        
        # Keep only the last max_points
        if len(self.data_series[series_name]) > self.max_points:
            self.data_series[series_name] = self.data_series[series_name][-self.max_points:]
    
    def clear(self):
        """Clear all data"""
        self.data_series = {}
    
    def draw(self, screen: pygame.Surface):
        """Draw the chart"""
        # Draw background
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)
        
        # Draw title
        if self.title:
            title_surface = self.font.render(self.title, True, (0, 0, 0))
            title_rect = title_surface.get_rect()
            title_rect.centerx = self.rect.centerx
            title_rect.top = self.rect.top + 5
            screen.blit(title_surface, title_rect)
        
        if not self.data_series:
            return
        
        # Calculate bounds
        all_points = []
        for series in self.data_series.values():
            all_points.extend(series)
        
        if not all_points:
            return
        
        min_x = min(point[0] for point in all_points)
        max_x = max(point[0] for point in all_points)
        min_y = 0  # Always start from 0 for population counts
        max_y = max(point[1] for point in all_points)
        
        if max_x == min_x or max_y == min_y:
            return
        
        # Draw chart area
        chart_rect = pygame.Rect(self.rect.left + 30, self.rect.top + 30,
                               self.rect.width - 60, self.rect.height - 60)
        
        # Draw series
        for series_name, points in self.data_series.items():
            if len(points) < 2:
                continue
            
            color = self.colors.get(series_name, (128, 128, 128))
            screen_points = []
            
            for x, y in points:
                screen_x = chart_rect.left + int((x - min_x) / (max_x - min_x) * chart_rect.width)
                screen_y = chart_rect.bottom - int((y - min_y) / (max_y - min_y) * chart_rect.height)
                screen_points.append((screen_x, screen_y))
            
            if len(screen_points) >= 2:
                pygame.draw.lines(screen, color, False, screen_points, 2)
        
        # Draw legend
        legend_y = self.rect.bottom - 20
        legend_x = self.rect.left + 10
        for series_name, points in self.data_series.items():
            if points:
                color = self.colors.get(series_name, (128, 128, 128))
                pygame.draw.circle(screen, color, (legend_x, legend_y), 5)
                text_surface = self.font.render(series_name.capitalize(), True, (0, 0, 0))
                screen.blit(text_surface, (legend_x + 15, legend_y - 8))
                legend_x += 80