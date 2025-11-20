import random
from config import LEVELS
from enemies import ENEMY_CLASSES

MAX_ACTIVE_ENEMIES = 8

class GameState:
    def __init__(self, level_number, override_topology=None):
        self.level = LEVELS[level_number - 1]
        self.level_number = level_number

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

        self.all_paths = None

    def find_all_paths(self, start, goal, max_paths=5):
        graph = {i: [] for i in range(len(self.nodes))}
        for edge in self.edges:
            graph[edge[0]].append(edge[1])
            graph[edge[1]].append(edge[0])

        paths = []

        def dfs(current, path):
            if len(paths) >= max_paths:
                return
            if current == goal:
                paths.append(list(path))
                return
            for neighbor in graph[current]:
                if neighbor not in path:
                    path.append(neighbor)
                    dfs(neighbor, path)
                    path.pop()

        dfs(start, [start])
        if not paths:
            paths.append([start, goal])
        return paths

    def update(self, enemies):
        print(f"Update called: packets_spawned={self.packets_spawned}, total_packets={self.level.get('total_packets')}, enemies={len(enemies)}")
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

        wave_number = max(1, self.packets_spawned // 10)
        base_interval = self.level['spawn_interval']
        min_interval = 25
        self.spawn_interval = max(base_interval - wave_number * 3, min_interval)

        if self.packets_spawned != 0 and self.packets_spawned % 50 == 0:
            self.core_health = min(self.core_health + 15, 100)

    def should_spawn_enemy(self, current_enemies):
        if self.level.get('mode') != 'ENDLESS' and self.packets_spawned >= self.level['total_packets']:
            return False
        if len(current_enemies) >= MAX_ACTIVE_ENEMIES:
            return False

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True
        return False

    def get_enemy_to_spawn(self):
        if self.level_number == 5 and 'LEGITIMATE' in self.level['enemy_types']:
            legit_ratio = self.level.get('legitimate_ratio', 0.3)
            if random.random() < legit_ratio:
                return 'LEGITIMATE'
        enemy_types = [t for t in self.level['enemy_types'] if t != 'LEGITIMATE']
        return random.choice(enemy_types)

    def spawn_enemy(self, enemy_type):
        if self.all_paths is None:
            self.all_paths = self.find_all_paths(self.start_node, self.goal_node, max_paths=5)

        path_points = random.choice(self.all_paths)
        path = [self.nodes[idx] for idx in path_points]

        enemy_config = self.level['enemy_config'][enemy_type]
        enemy_class = ENEMY_CLASSES[enemy_type]
        enemy = enemy_class(path, enemy_config)

        self.packets_spawned += 1
        return enemy

    def enemy_destroyed(self, enemy):
        if hasattr(enemy, 'is_legitimate') and enemy.is_legitimate:
            self.legitimate_blocked += 1
            self.score -= 100
        else:
            self.packets_blocked += 1
            self.score += enemy.reward
            self.money += enemy.reward

    def enemy_reached_goal(self, enemy):
        wave_number = self.packets_spawned // 10 + 1
        damage = min(10 + wave_number * 2, 50)

        if hasattr(enemy, 'is_legitimate') and enemy.is_legitimate:
            self.legitimate_allowed += 1
            self.score += 10
        else:
            self.packets_leaked += 1
            self.core_health -= damage
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
