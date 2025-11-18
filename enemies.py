# enemies.py
"""Enemy packet classes with different types and behaviors."""

import pygame
import math
from typing import List, Tuple

class Enemy:
    """Base enemy class."""
    
    def __init__(self, path: List[Tuple[int, int]], enemy_config: dict):
        self.path = path
        self.current_point = 0
        self.x, self.y = self.path[0] if path else (0, 0)
        
        # Stats from config
        self.health = enemy_config['health']
        self.max_health = enemy_config['health']
        self.base_speed = enemy_config['speed']
        self.speed = self.base_speed
        
        # State
        self.slow_factor = 1.0  # 1.0 = normal, 0.5 = 50% slow
        self.reached_goal = False
        self.is_legitimate = False
        
    def update(self):
        """Move along path."""
        if self.current_point >= len(self.path) - 1:
            self.reached_goal = True
            return
        
        target_x, target_y = self.path[self.current_point + 1]
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        
        actual_speed = self.speed * self.slow_factor
        
        if dist < actual_speed:
            self.x, self.y = target_x, target_y
            self.current_point += 1
        else:
            self.x += actual_speed * dx / dist
            self.y += actual_speed * dy / dist
    
    def apply_slow(self, factor):
        """Apply slow effect from IDS."""
        self.slow_factor = min(self.slow_factor, factor)
    
    def reset_slow(self):
        """Reset slow effect each frame."""
        self.slow_factor = 1.0
    
    def draw(self, screen):
        """Draw enemy with type-specific visuals."""
        # Draw main body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw icon/label
        if hasattr(self, 'icon'):
            font = pygame.font.SysFont(None, 16, bold=True)
            label = font.render(self.icon, True, (255, 255, 255))
            label_rect = label.get_rect(center=(self.x, self.y - self.radius - 15))
            
            # Background for label
            bg_rect = label_rect.inflate(6, 2)
            pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
            screen.blit(label, label_rect)
        
        # Draw health bar (if not infinite)
        if self.health != float('inf'):
            self.draw_health_bar(screen)
    
    def draw_health_bar(self, screen):
        """Draw health bar above enemy."""
        bar_width = 30
        bar_height = 4
        health_ratio = max(0, self.health / self.max_health)
        
        # Red background
        pygame.draw.rect(screen, (255, 0, 0),
                        (self.x - bar_width // 2, self.y - 22, bar_width, bar_height))
        # Green health
        pygame.draw.rect(screen, (0, 255, 0),
                        (self.x - bar_width // 2, self.y - 22, bar_width * health_ratio, bar_height))


class BasicMalware(Enemy):
    """Basic malicious packet."""
    
    def __init__(self, path, enemy_config):
        super().__init__(path, enemy_config)
        self.type = 'BASIC'
        self.color = (255, 50, 50)
        self.radius = 12
        self.icon = 'MAL'
        self.reward = 50


class FastPacket(Enemy):
    """Fast, low-health packet."""
    
    def __init__(self, path, enemy_config):
        super().__init__(path, enemy_config)
        self.type = 'FAST'
        self.color = (255, 150, 50)
        self.radius = 10
        self.icon = '⚡'
        self.reward = 75


class TankPacket(Enemy):
    """Slow, high-health packet."""
    
    def __init__(self, path, enemy_config):
        super().__init__(path, enemy_config)
        self.type = 'TANK'
        self.color = (150, 50, 255)
        self.radius = 18
        self.icon = '🛡'
        self.reward = 150
    
    def draw(self, screen):
        """Draw with armor effect."""
        # Main body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Armor border
        pygame.draw.circle(screen, (100, 100, 100), (int(self.x), int(self.y)), self.radius, 3)
        
        # Icon and health bar
        super().draw(screen)


class LegitimatePacket(Enemy):
    """Legitimate traffic that must NOT be blocked."""
    
    def __init__(self, path, enemy_config):
        super().__init__(path, enemy_config)
        self.type = 'LEGITIMATE'
        self.color = (50, 255, 50)
        self.radius = 10
        self.icon = '✓'
        self.reward = 0
        self.is_legitimate = True
        self.health = float('inf')  # Cannot be destroyed
    
    def draw(self, screen):
        """Draw bright green with checkmark."""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        font = pygame.font.SysFont(None, 18, bold=True)
        label = font.render(self.icon, True, (255, 255, 255))
        screen.blit(label, (self.x - 8, self.y - self.radius - 18))


# Enemy type mapping
ENEMY_CLASSES = {
    'BASIC': BasicMalware,
    'FAST': FastPacket,
    'TANK': TankPacket,
    'LEGITIMATE': LegitimatePacket
}
