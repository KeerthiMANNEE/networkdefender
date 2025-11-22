import random
from collections import defaultdict


def generate_random_topology(
    node_count=8,
    edge_count=12,
    screen_width=900,
    screen_height=700,
    max_nodes=12,
    max_edges=20,
    right_ui_margin=250,
    border_margin_x=80,
    border_margin_y=120,
    edge_node_margin=40
):
    node_count = min(node_count, max_nodes)
    edge_count = min(max(edge_count, node_count - 1), max_edges)

    usable_width = screen_width - right_ui_margin - 2 * border_margin_x - 2 * edge_node_margin
    usable_height = screen_height - 2 * border_margin_y - 2 * edge_node_margin

    grid_cols = max(3, int(usable_width // 80))
    grid_rows = max(3, int(usable_height // 80))

    grid_xs_central = [
        border_margin_x + edge_node_margin + i * (usable_width // (grid_cols - 1))
        for i in range(grid_cols)
    ]
    grid_ys_central = [
        border_margin_y + edge_node_margin + j * (usable_height // (grid_rows - 1))
        for j in range(grid_rows)
    ]
    central_positions = [(x, y) for x in grid_xs_central for y in grid_ys_central]
    random.shuffle(central_positions)

    start_x = border_margin_x
    start_y = screen_height // 2
    goal_x = screen_width - right_ui_margin - border_margin_x
    goal_y = screen_height // 2

    positions = [(start_x, start_y), (goal_x, goal_y)]
    positions += central_positions[: node_count - 2]

    edges = set((i, i + 1) for i in range(node_count - 1) if not (i == 0 and i + 1 == 1))

    while len(edges) < edge_count:
        a, b = random.sample(range(node_count), 2)
        if a == b:
            continue
        edge = tuple(sorted((a, b)))
        if edge in edges or edge == (0, 1):
            continue
        edges.add(edge)

    goal_node = 1
    goal_edges = [e for e in edges if goal_node in e]
    goal_degree = len(goal_edges)
    attempts = 0
    while goal_degree < 2 and attempts < 20:
        candidate = random.choice([n for n in range(node_count) if n != goal_node])
        new_edge = tuple(sorted((goal_node, candidate)))
        if new_edge not in edges:
            edges.add(new_edge)
            goal_degree += 1
        attempts += 1

    edges = list(edges)

    sources = [0]
    for n in range(2, node_count):
        if random.random() < 0.3:
            sources.append(n)

    def get_degree(node_id):
        return sum(1 for e in edges if node_id in e)

    chokepoints = [n for n in range(node_count) if get_degree(n) > 1]

    return {
        "nodes": positions,
        "edges": edges,
        "sources": sources,
        "goal": goal_node,
        "chokepoints": chokepoints,
    }



class AILearningSystem:
    def __init__(self):
        self.gameplay_history = []
        self.current_session = {
            'tower_placements': [],
            'enemy_outcomes': [],
            'defense_patterns': {}
        }
        self.successful_paths = defaultdict(int)
        self.failed_paths = defaultdict(int)
        self.tower_coverage = defaultdict(int)
        # Legacy fields, not used in random mode
        self.topology_list = []
        self.current_topology_idx = -1
        self.switch_count = 0  # Tracks number of topology switches in endless mode

    def record_tower_placement(self, node_id, tower_type):
        self.current_session['tower_placements'].append({
            'node': node_id,
            'type': tower_type
        })
        self.tower_coverage[node_id] += 1

    def record_enemy_outcome(self, enemy_type, path_nodes, destroyed):
        path_key = tuple(path_nodes)
        self.current_session['enemy_outcomes'].append({
            'type': enemy_type,
            'path': path_nodes,
            'destroyed': destroyed
        })
        if destroyed:
            self.failed_paths[path_key] += 1
        else:
            self.successful_paths[path_key] += 1

    def analyze_defense_patterns(self):
        placements = self.current_session['tower_placements']
        if not placements:
            return 'NONE'
        tower_counts = defaultdict(int)
        for p in placements:
            tower_counts[p['type']] += 1
        total = sum(tower_counts.values())
        if total == 0:
            return 'NONE'
        if tower_counts['Firewall'] / total > 0.7:
            return 'FIREWALL_HEAVY'
        elif tower_counts['IDS'] / total > 0.4:
            return 'IDS_FOCUSED'
        elif tower_counts.get('Honeypot', 0) > 2:
            return 'HONEYPOT_TRAP'
        else:
            return 'BALANCED'

    def select_counter_enemy_type(self, available_types, player_strategy):
        if player_strategy == 'FIREWALL_HEAVY':
            weights = {'BASIC': 1, 'FAST': 2, 'TANK': 4, 'ENCRYPTED': 3}
        elif player_strategy == 'IDS_FOCUSED':
            weights = {'BASIC': 1, 'FAST': 4, 'STEALTH': 3, 'TANK': 1}
        elif player_strategy == 'HONEYPOT_TRAP':
            weights = {'BASIC': 2, 'FAST': 3, 'ADAPTIVE': 4}
        else:
            weights = {t: 1 for t in available_types}
        filtered_weights = {t: w for t, w in weights.items() if t in available_types}
        if not filtered_weights:
            return random.choice(available_types)
        types = list(filtered_weights.keys())
        weights_list = list(filtered_weights.values())
        return random.choices(types, weights=weights_list)[0]

    def switch_topology(self, game_state, tower_manager=None, enemies=None):
        self.switch_count += 1
        MAX_NODES = 12
        MAX_EDGES = 20
        node_count = min(8 + self.switch_count, MAX_NODES)
        edge_count = min(node_count + 4 + self.switch_count, MAX_EDGES)
        new_topology = generate_random_topology(
            node_count=node_count,
            edge_count=edge_count,
            screen_width=900,
            screen_height=700,
            max_nodes=MAX_NODES,
            max_edges=MAX_EDGES
        )
        game_state.set_topology(new_topology)
        if tower_manager:
            tower_manager.clear_towers()
        if enemies is not None:
            enemies.clear()
        print(f"[AI] Switched to RANDOM topology #{self.switch_count}: nodes={len(new_topology['nodes'])}, edges={len(new_topology['edges'])}")

    def end_session(self, level_num, player_won):
        self.current_session['level'] = level_num
        self.current_session['player_won'] = player_won
        self.current_session['defense_strategy'] = self.analyze_defense_patterns()
        self.gameplay_history.append(self.current_session)
        self.current_session = {
            'tower_placements': [],
            'enemy_outcomes': [],
            'defense_patterns': {}
        }
        self.switch_count = 0  # Reset for new endless mode session

    def save_to_file(self, filename='ai_learning_data.json'):
        def convert_keys_to_str(d):
            return {str(k): v for k, v in d.items()}
        data = {
            'history': self.gameplay_history,
            'successful_paths': convert_keys_to_str(self.successful_paths),
            'failed_paths': convert_keys_to_str(self.failed_paths)
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename='ai_learning_data.json'):
        def convert_keys_to_tuple(d):
            new_d = defaultdict(int)
            for k, v in d.items():
                try:
                    key_tuple = tuple(int(x.strip()) for x in k.strip('()[]').split(','))
                    new_d[key_tuple] = v
                except Exception:
                    pass
            return new_d
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.gameplay_history = data.get('history', [])
                self.successful_paths = convert_keys_to_tuple(data.get('successful_paths', {}))
                self.failed_paths = convert_keys_to_tuple(data.get('failed_paths', {}))
                print(f"✓ Loaded AI learning data from {filename}")
        except FileNotFoundError:
            print(f"No previous learning data found. Starting fresh.")
if __name__ == "__main__":
    print("generate_random_topology is defined as:", generate_random_topology)
