import json
import random
from collections import defaultdict

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
        self.topology_list = []
        self.current_topology_idx = 0

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

    def switch_topology(self, game_state):
        if not self.topology_list:
            print("No dynamic topologies set!")
            return
        self.current_topology_idx = (self.current_topology_idx + 1) % len(self.topology_list)
        new_topo = self.topology_list[self.current_topology_idx]
        game_state.nodes = new_topo['nodes']
        game_state.edges = new_topo['edges']
        game_state.start_node = new_topo['start']
        game_state.goal_node = new_topo['goal']
        print(f"[AI] Switched to topology {self.current_topology_idx + 1}")

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