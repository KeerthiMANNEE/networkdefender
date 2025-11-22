import pygame
import math

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.cooldown = 0

        if tower_type == 'Firewall':
            self.damage = 2
            self.range = 80
            self.cooldown_time = 20
            self.color = (80, 170, 255)
            self.effect = None
        elif tower_type == 'IDS':
            self.damage = 0
            self.range = 100
            self.cooldown_time = 10
            self.color = (255, 200, 50)
            self.effect = 'slow'
        elif tower_type == 'Honeypot':
            self.damage = 0
            self.range = 120
            self.cooldown_time = 0
            self.color = (255, 150, 255)
            self.effect = 'attract'

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            if self.effect == 'slow':  # IDS slows packets
                for enemy in enemies:
                    if getattr(enemy, 'is_legitimate', False):
                        continue
                    dist = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                    if dist <= self.range:
                        enemy.apply_slow(0.3)  # stronger slow effect
                        self.cooldown = self.cooldown_time
                        break
            elif self.effect == 'attract':  # Honeypot attracts malicious packets
                for enemy in enemies:
                    if getattr(enemy, 'is_legitimate', False):
                        continue
                    dx = self.x - enemy.x
                    dy = self.y - enemy.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < self.range * 2:
                        enemy.x += dx * 0.05
                        enemy.y += dy * 0.05

            elif self.damage > 0:
                for enemy in enemies:
                    if getattr(enemy, 'is_legitimate', False):
                        continue
                    dist = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
                    if dist <= self.range:
                        enemy.health -= self.damage
                        self.cooldown = self.cooldown_time
                        break

    def draw(self, screen):
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (*self.color, 30), (self.range, self.range), self.range)
        screen.blit(range_surface, (self.x - self.range, self.y - self.range))

        pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 15, 2)

        font = pygame.font.SysFont(None, 12)
        label = font.render(self.type[:3], True, (255, 255, 255))
        screen.blit(label, (self.x - 10, self.y - 5))


class TowerManager:
    def __init__(self, tower_limit=10):
        self.towers = []
        self.tower_limit = tower_limit

    def can_place_tower(self, node_pos, tower_type, money):
        costs = {'Firewall': 100, 'IDS': 80, 'Honeypot': 120}
        if len(self.towers) >= self.tower_limit:
            return False, f"Tower limit ({self.tower_limit}) reached!"
        cost = costs.get(tower_type, 100)
        if money < cost:
            return False, "Not enough money!"
        for tower in self.towers:
            if (tower.x, tower.y) == node_pos:
                return False, "Tower already here!"
        return True, "OK"

    def add_tower(self, x, y, tower_type):
        costs = {'Firewall': 100, 'IDS': 80, 'Honeypot': 120}
        tower = Tower(x, y, tower_type)
        self.towers.append(tower)
        return costs.get(tower_type, 100)

    def remove_tower_at(self, pos):
        for tower in self.towers:
            if (tower.x, tower.y) == pos:
                self.towers.remove(tower)
                return True
        return False

    def update(self, enemies):
        for tower in self.towers:
            tower.update(enemies)

    def draw(self, screen):
        for tower in self.towers:
            tower.draw(screen)

    def clear_towers(self):
        self.towers.clear()
