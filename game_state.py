"""Game state and level management."""

import random
from config import LEVELS
from enemies import ENEMY_CLASSES

class GameState:
    """Manages current game state."""

    def __init__(self, level_number, override_topology=None):
        self.level = LEVELS[level_number - 1]
        self.level_number = level_number

        # Use override topology if provided; else use default
        if override_topology:
            topo = override_topology
        else:
            topo = self.level['topology']

        self.nodes = topo['nodes']
        self.edges = topo['edges']
        self.start_node = topo['start']
        self.goal_node = topo['goal']

        self.money = self.level['starting_money']
        self.core_health = 100
        self.score = 0

        self.packets_spawned = 0
        self.packets_blocked = 0
        self.packets_leaked = 0
        self.legitimate_blocked = 0
        self.legitimate_allowed = 0

        self.spawn_timer = 0
        self.spawn_interval = self.level['spawn_interval']

        self.level_complete = False
        self.level_failed = False

    def update(self, enemies):
        if self.core_health <= 0:
            self.level_failed = True

        if self.level.get('mode') != 'ENDLESS':
            total_packets = self.level['total_packets']
            if self.packets_spawned >= total_packets and len(enemies) == 0:
                success_rate = self.calculate_success_rate()
                if success_rate >= self.level['success_threshold']:
                    self.level_complete = True
                else:
                    self.level_failed = True

    def should_spawn_enemy(self):
        if self.level.get('mode') != 'ENDLESS':
            if self.packets_spawned >= self.level['total_packets']:
                return False

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True

        return False

    def get_enemy_to_spawn(self):
        if self.level_number == 5:
            legit_ratio = self.level.get('legitimate_ratio', 0.3)
            if random.random() < legit_ratio:
                return 'LEGITIMATE'

        enemy_types = [t for t in self.level['enemy_types'] if t != 'LEGITIMATE']
        return random.choice(enemy_types)

    def spawn_enemy(self, enemy_type):
        path = self.find_path(self.start_node, self.goal_node)
        enemy_config = self.level['enemy_config'][enemy_type]

        enemy_class = ENEMY_CLASSES[enemy_type]
        enemy = enemy_class(path, enemy_config)

        self.packets_spawned += 1
        return enemy

    def find_path(self, start, goal):
        graph = {i: [] for i in range(len(self.nodes))}
        for edge in self.edges:
            graph[edge[0]].append(edge[1])
            graph[edge[1]].append(edge[0])

        queue = [(start, [start])]
        visited = {start}

        while queue:
            node, path = queue.pop(0)
            if node == goal:
                return [self.nodes[i] for i in path]
            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return [self.nodes[start], self.nodes[goal]]

    def enemy_destroyed(self, enemy):
        if hasattr(enemy, 'is_legitimate') and enemy.is_legitimate:
            self.legitimate_blocked += 1
            self.score -= 100
            return -100
        else:
            self.packets_blocked += 1
            self.score += enemy.reward
            self.money += enemy.reward
            return enemy.reward

    def enemy_reached_goal(self, enemy):
        if hasattr(enemy, 'is_legitimate') and enemy.is_legitimate:
            self.legitimate_allowed += 1
            self.score += 10
        else:
            self.packets_leaked += 1
            self.core_health -= 10
            self.score -= 50

    def calculate_success_rate(self):
        total = self.packets_blocked + self.packets_leaked
        if total == 0:
            return 0
        return (self.packets_blocked / total) * 100

    def get_accuracy(self):
        total = (self.packets_blocked + self.packets_leaked +
                 self.legitimate_allowed + self.legitimate_blocked)
        if total == 0:
            return 100

        correct = self.packets_blocked + self.legitimate_allowed
        return (correct / total) * 100
