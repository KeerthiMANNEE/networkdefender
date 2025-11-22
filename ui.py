import pygame
import time
from config import TOWERS

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 18)
        self.font_tiny = pygame.font.SysFont('Arial', 14)

        self.selected_tower_type = None

        self.popup_end_time = None
        self.popup_message = None

        self.message = None
        self.message_end_time = 0

        self.blink_nodes = []
        self.blink_start_time = time.time()
        self.blink_visible = True

    def update(self):
        if self.popup_end_time and time.time() > self.popup_end_time:
            self.popup_end_time = None
            self.popup_message = None
        if self.message and time.time() > self.message_end_time:
            self.message = None
            self.message_end_time = 0
        elapsed = time.time() - self.blink_start_time
        self.blink_visible = (int(elapsed * 2) % 2) == 0

    def show_popup(self, message, duration=2):
        self.popup_message = message
        self.popup_end_time = time.time() + duration

    def show_message(self, text, duration=5):
        self.message = text
        self.message_end_time = time.time() + duration

    def draw_popup(self, message, alpha=180):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))
        text = self.font_large.render(message, True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(text, rect)

    def draw_message(self):
        if self.message and time.time() < self.message_end_time:
            text_surf = self.font_medium.render(self.message, True, (255, 255, 0))
            rect = text_surf.get_rect(center=(self.screen.get_width() // 2, 60))
            bg_rect = rect.inflate(32, 16)
            panel = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            panel.fill((0, 0, 0, 192))
            self.screen.blit(panel, bg_rect.topleft)
            self.screen.blit(text_surf, rect)

    def draw_blinking_nodes(self, nodes):
        if not self.blink_visible:
            return
        for node_idx in self.blink_nodes:
            pos = nodes[node_idx]
            radius = 30
            color = (255, 255, 0, 150)
            blink_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(blink_surface, color, (radius, radius), radius, 4)
            self.screen.blit(blink_surface, (pos[0] - radius, pos[1] - radius))

    def draw_network(self, nodes, edges, start_node, goal_node):
        for edge in edges:
            start_pos = nodes[edge[0]]
            end_pos = nodes[edge[1]]
            pygame.draw.line(self.screen, (120, 220, 150), start_pos, end_pos, 4)
        for i, pos in enumerate(nodes):
            if i == start_node:
                color = (100, 255, 100)
            elif i == goal_node:
                color = (255, 100, 100)
            else:
                color = (200, 200, 100)
            pygame.draw.circle(self.screen, color, pos, 25)
            pygame.draw.circle(self.screen, (60, 60, 60), pos, 25, 3)
            label = self.font_small.render(str(i), True, (255, 255, 255))
            self.screen.blit(label, (pos[0] - 7, pos[1] - 10))

    def draw_hud(self, game_state):
        rect = pygame.Rect(0, 0, self.screen.get_width(), 70)
        pygame.draw.rect(self.screen, (40, 40, 40), rect)
        pygame.draw.line(self.screen, (100, 100, 100), (0, 70), (self.screen.get_width(), 70), 2)
        level_text = self.font_medium.render(f"Level {game_state.level_number}: {game_state.level['name']}", True, (255, 255, 255))
        self.screen.blit(level_text, (20, 10))
        money_color = (255, 215, 0) if game_state.money >= 100 else (255, 100, 100)
        self.screen.blit(self.font_small.render(f"💰 ${game_state.money}", True, money_color), (20, 45))
        health_color = (100, 255, 100) if game_state.core_health > 50 else (255, 100, 100)
        self.screen.blit(self.font_small.render(f"❤️ {game_state.core_health}%", True, health_color), (150, 45))
        self.screen.blit(self.font_small.render(f"⭐ {game_state.score}", True, (150, 200, 255)), (280, 45))
        if game_state.level.get("mode") != "ENDLESS":
            packets_text = f"📦 {game_state.packets_spawned}/{game_state.level['total_packets']}"
            self.screen.blit(self.font_small.render(packets_text, True, (200, 200, 200)), (410, 45))
        else:
            wave_num = game_state.packets_spawned // 10 + 1
            self.screen.blit(self.font_small.render(f"🌊 Wave {wave_num}", True, (200, 200, 200)), (410, 45))
        success_rate = game_state.calculate_success_rate()
        self.screen.blit(self.font_small.render(f"✓ {success_rate:.0f}%", True, (200, 255, 200)), (550, 45))
        self.draw_packet_legend()

    def draw_packet_legend(self):
        legend_x, legend_y = 20, 80
        gap = 30
        type_colors = {
            "BASIC": (255, 50, 50),
            "FAST": (255, 150, 50),
            "TANK": (150, 50, 255),
            "STEALTH": (100, 100, 100),
            "ENCRYPTED": (0, 120, 200),
            "LEGITIMATE": (50, 255, 50),
            "ADAPTIVE": (180, 0, 180),
        }
        for name, color in type_colors.items():
            pygame.draw.circle(self.screen, color, (legend_x + 10, legend_y + 10), 8)
            self.screen.blit(self.font_small.render(name, True, (255, 255, 255)), (legend_x + 25, legend_y))
            legend_y += gap

    def draw_tower_menu(self, available_towers, money):
        menu_x = self.screen.get_width() - 220
        menu_y = 90
        rect = pygame.Rect(menu_x - 10, menu_y - 10, 210, len(available_towers) * 80 + 20)
        pygame.draw.rect(self.screen, (50, 50, 50), rect)
        pygame.draw.rect(self.screen, (100, 100, 100), rect, 2)
        self.screen.blit(self.font_small.render("TOWERS", True, (255, 255, 255)), (menu_x + 70, menu_y))
        y = menu_y + 30
        for t in available_towers:
            config = TOWERS[t]
            can_afford = (money >= config['cost'])
            button_rect = pygame.Rect(menu_x, y, 190, 70)
            pygame.draw.rect(self.screen, (80, 120, 180) if self.selected_tower_type == t else (70, 70, 70), button_rect)
            pygame.draw.rect(self.screen, (150, 150, 150), button_rect, 2)
            pygame.draw.circle(self.screen, config['color'], (menu_x + 25, y + 35), 15)
            self.screen.blit(self.font_small.render(t, True, (255, 255, 255) if can_afford else (150, 150, 150)), (menu_x + 50, y + 10))
            self.screen.blit(self.font_tiny.render(f"${config['cost']}", True, (255, 215, 0) if can_afford else (255, 100, 100)), (menu_x + 50, y + 30))
            self.screen.blit(self.font_tiny.render(config['description'][:20], True, (200, 200, 200)), (menu_x + 50, y + 50))
            y += 80

    def draw_level_intro(self, game_state):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        center_x = self.screen.get_width() // 2
        self.screen.blit(self.font_large.render(f"LEVEL {game_state.level_number}", True, (255, 255, 255)), (center_x - 80, 150))
        self.screen.blit(self.font_medium.render(game_state.level["name"], True, (100, 200, 255)), (center_x - 70, 210))
        self.screen.blit(self.font_small.render(game_state.level["description"], True, (200, 200, 200)), (center_x - 100, 270))
        self.screen.blit(self.font_small.render(f"Concept: {game_state.level['concept']}", True, (150, 255, 150)), (center_x - 70, 310))
        if "mode" in game_state.level and game_state.level["mode"] != "ENDLESS":
            text = f"Objective: Block {game_state.level['success_threshold']}% of {game_state.level['total_packets']} packets"
            self.screen.blit(self.font_small.render(text, True, (255, 255, 200)), (center_x - 150, 360))
        else:
            self.screen.blit(self.font_small.render("Objective: Survive as many waves as possible!", True, (255, 255, 200)), (center_x - 150, 360))
        self.screen.blit(self.font_medium.render("Press SPACE to start", True, (255, 255, 100)), (center_x - 80, 450))

    def draw_level_complete(self, game_state):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        center_x = self.screen.get_width() // 2
        self.screen.blit(self.font_large.render("LEVEL COMPLETE!", True, (100, 255, 100)), (center_x - 100, 200))
        stats = [
            f"Score: {game_state.score}",
            f"Blocked: {game_state.packets_blocked}",
            f"Leaked: {game_state.packets_leaked}",
            f"Success Rate: {game_state.calculate_success_rate():.1f}%",
        ]
        y = 300
        for stat in stats:
            self.screen.blit(self.font_small.render(stat, True, (255, 255, 255)), (center_x - 70, y))
            y += 40
        self.screen.blit(self.font_medium.render("Press SPACE for next level", True, (255, 255, 100)), (center_x - 100, 500))

    def draw_level_failed(self, game_state):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((50, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))
        center_x = self.screen.get_width() // 2
        self.screen.blit(self.font_large.render("CORE BREACHED", True, (255, 100, 100)), (center_x - 70, 250))
        self.screen.blit(self.font_medium.render("Press R to retry", True, (255, 255, 100)), (center_x - 50, 400))
