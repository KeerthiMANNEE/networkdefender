# ui.py
"""UI rendering and visual elements."""

import pygame
from config import TOWERS

class UI:
    """Manages all UI elements."""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 18)
        self.font_tiny = pygame.font.SysFont('Arial', 14)
        
        # UI state
        self.selected_tower_type = None
        self.hover_node = None
    
    def draw_network(self, nodes, edges, start_node, goal_node):
        """Draw network topology."""
        # Draw edges
        for edge in edges:
            start_pos = nodes[edge[0]]
            end_pos = nodes[edge[1]]
            pygame.draw.line(self.screen, (120, 220, 150), start_pos, end_pos, 4)
        
        # Draw nodes
        for i, pos in enumerate(nodes):
            if i == start_node:
                color = (100, 255, 100)  # Green for start
            elif i == goal_node:
                color = (255, 100, 100)  # Red for goal
            else:
                color = (200, 200, 100)  # Yellow for normal
            
            pygame.draw.circle(self.screen, color, pos, 25)
            pygame.draw.circle(self.screen, (60, 60, 60), pos, 25, 3)
            
            # Node number
            label = self.font_small.render(str(i), True, (255, 255, 255))
            self.screen.blit(label, (pos[0] - 7, pos[1] - 10))
    
    def draw_hud(self, game_state):
        """Draw heads-up display."""
        # Background panel
        panel_rect = pygame.Rect(0, 0, self.screen.get_width(), 70)
        pygame.draw.rect(self.screen, (40, 40, 40), panel_rect)
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (0, 70), (self.screen.get_width(), 70), 2)
        
        # Level name
        level_text = self.font_medium.render(
            f"Level {game_state.level_number}: {game_state.level['name']}", 
            True, (255, 255, 255)
        )
        self.screen.blit(level_text, (20, 10))
        
        # Money
        money_color = (255, 215, 0) if game_state.money >= 100 else (255, 100, 100)
        money_text = self.font_small.render(f"💰 ${game_state.money}", True, money_color)
        self.screen.blit(money_text, (20, 45))
        
        # Core health
        health_color = (100, 255, 100) if game_state.core_health > 50 else (255, 100, 100)
        health_text = self.font_small.render(f"❤️ {game_state.core_health}%", True, health_color)
        self.screen.blit(health_text, (150, 45))
        
        # Score
        score_text = self.font_small.render(f"⭐ {game_state.score}", True, (150, 200, 255))
        self.screen.blit(score_text, (280, 45))
        
        # Packets (for non-endless levels)
        if game_state.level.get('mode') != 'ENDLESS':
            packet_text = self.font_small.render(
                f"📦 {game_state.packets_spawned}/{game_state.level['total_packets']}", 
                True, (200, 200, 200)
            )
            self.screen.blit(packet_text, (410, 45))
        else:
            # Endless mode - show wave number
            wave_num = game_state.packets_spawned // 10 + 1
            wave_text = self.font_small.render(f"🌊 Wave {wave_num}", True, (200, 200, 200))
            self.screen.blit(wave_text, (410, 45))
        
        # Success rate
        success_rate = game_state.calculate_success_rate()
        rate_text = self.font_small.render(f"✓ {success_rate:.0f}%", True, (200, 255, 200))
        self.screen.blit(rate_text, (550, 45))
    
    def draw_tower_menu(self, available_towers, money):
        """Draw tower selection menu."""
        menu_x = self.screen.get_width() - 220
        menu_y = 90
        
        # Menu background
        menu_rect = pygame.Rect(menu_x - 10, menu_y - 10, 210, len(available_towers) * 80 + 20)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), menu_rect, 2)
        
        # Title
        title = self.font_small.render("TOWERS", True, (255, 255, 255))
        self.screen.blit(title, (menu_x + 70, menu_y))
        
        y = menu_y + 30
        for tower_type in available_towers:
            config = TOWERS[tower_type]
            can_afford = money >= config['cost']
            
            # Tower button
            button_rect = pygame.Rect(menu_x, y, 190, 70)
            
            # Highlight if selected or hovered
            if self.selected_tower_type == tower_type:
                pygame.draw.rect(self.screen, (80, 120, 180), button_rect)
            else:
                pygame.draw.rect(self.screen, (70, 70, 70), button_rect)
            
            pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 2)
            
            # Tower icon (colored circle)
            pygame.draw.circle(self.screen, config['color'], (menu_x + 25, y + 35), 15)
            
            # Tower name
            name_text = self.font_small.render(tower_type, True, (255, 255, 255) if can_afford else (150, 150, 150))
            self.screen.blit(name_text, (menu_x + 50, y + 10))
            
            # Cost
            cost_color = (255, 215, 0) if can_afford else (255, 100, 100)
            cost_text = self.font_tiny.render(f"${config['cost']}", True, cost_color)
            self.screen.blit(cost_text, (menu_x + 50, y + 30))
            
            # Description
            desc_text = self.font_tiny.render(config['description'][:20], True, (200, 200, 200))
            self.screen.blit(desc_text, (menu_x + 50, y + 50))
            
            y += 80
    
    def draw_level_intro(self, game_state):
        """Draw level introduction screen."""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Level info
        center_x = self.screen.get_width() // 2
        
        # Level number
        level_num = self.font_large.render(f"LEVEL {game_state.level_number}", True, (255, 255, 255))
        level_num_rect = level_num.get_rect(center=(center_x, 150))
        self.screen.blit(level_num, level_num_rect)
        
        # Level name
        level_name = self.font_medium.render(game_state.level['name'], True, (100, 200, 255))
        level_name_rect = level_name.get_rect(center=(center_x, 210))
        self.screen.blit(level_name, level_name_rect)
        
        # Description
        desc = self.font_small.render(game_state.level['description'], True, (200, 200, 200))
        desc_rect = desc.get_rect(center=(center_x, 270))
        self.screen.blit(desc, desc_rect)
        
        # Concept
        concept = self.font_small.render(f"Concept: {game_state.level['concept']}", True, (150, 255, 150))
        concept_rect = concept.get_rect(center=(center_x, 310))
        self.screen.blit(concept, concept_rect)
        
        # Objective
        if game_state.level.get('mode') != 'ENDLESS':
            objective = self.font_small.render(
                f"Objective: Block {game_state.level['success_threshold']}% of {game_state.level['total_packets']} packets",
                True, (255, 255, 200)
            )
        else:
            objective = self.font_small.render(
                "Objective: Survive as many waves as possible!",
                True, (255, 255, 200)
            )
        objective_rect = objective.get_rect(center=(center_x, 360))
        self.screen.blit(objective, objective_rect)
        
        # Start prompt
        prompt = self.font_medium.render("Press SPACE to start", True, (255, 255, 100))
        prompt_rect = prompt.get_rect(center=(center_x, 450))
        self.screen.blit(prompt, prompt_rect)
    
    def draw_level_complete(self, game_state):
        """Draw level completion screen."""
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(220)
        overlay.fill((0, 50, 0))
        self.screen.blit(overlay, (0, 0))
        
        center_x = self.screen.get_width() // 2
        
        # Success message
        title = self.font_large.render("LEVEL COMPLETE!", True, (100, 255, 100))
        title_rect = title.get_rect(center=(center_x, 200))
        self.screen.blit(title, title_rect)
        
        # Stats
        stats = [
            f"Score: {game_state.score}",
            f"Blocked: {game_state.packets_blocked}",
            f"Leaked: {game_state.packets_leaked}",
            f"Success Rate: {game_state.calculate_success_rate():.1f}%"
        ]
        
        y = 300
        for stat in stats:
            stat_text = self.font_small.render(stat, True, (255, 255, 255))
            stat_rect = stat_text.get_rect(center=(center_x, y))
            self.screen.blit(stat_text, stat_rect)
            y += 40
        
        # Continue prompt
        prompt = self.font_medium.render("Press SPACE for next level", True, (255, 255, 100))
        prompt_rect = prompt.get_rect(center=(center_x, 500))
        self.screen.blit(prompt, prompt_rect)
    
    def draw_level_failed(self, game_state):
        """Draw level failure screen."""
        overlay = pygame.Surface(self.screen.get_size())
        overlay.set_alpha(220)
        overlay.fill((50, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        center_x = self.screen.get_width() // 2
        
        # Failure message
        title = self.font_large.render("CORE BREACHED", True, (255, 100, 100))
        title_rect = title.get_rect(center=(center_x, 250))
        self.screen.blit(title, title_rect)
        
        # Retry prompt
        prompt = self.font_medium.render("Press R to retry", True, (255, 255, 100))
        prompt_rect = prompt.get_rect(center=(center_x, 400))
        self.screen.blit(prompt, prompt_rect)
