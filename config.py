# config.py
"""Game configuration and level definitions."""

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

# Colors
COLOR_BACKGROUND = (30, 30, 30)
COLOR_NODE_START = (100, 255, 100)
COLOR_NODE_GOAL = (255, 100, 100)
COLOR_NODE_NORMAL = (200, 200, 100)
COLOR_EDGE = (120, 220, 150)

# Level definitions
LEVELS = [
    {
        'number': 1,
        'name': 'Firewall Basics',
        'description': 'Learn to use Firewalls to block basic threats',
        'concept': 'Packet Filtering',
        'topology': {
            'nodes': [(100, 350), (300, 350), (500, 350), (700, 350)],
            'edges': [(0, 1), (1, 2), (2, 3)],
            'start': 0,
            'goal': 2
        },
        'total_packets': 10,
        'spawn_interval': 90,
        'success_threshold': 70,  # 7 out of 10
        'starting_money': 400,
        'towers_available': ['Firewall'],
        'enemy_types': ['BASIC'],
        'enemy_config': {
            'BASIC': {'health': 5, 'speed': 1.5}
        }
    },
    
    {
        'number': 2,
        'name': 'Intrusion Detection',
        'description': 'Use IDS to slow enemies, then destroy with Firewall',
        'concept': 'Detection & Slowing',
        'topology': {
            'nodes': [(100, 350), (300, 350), (500, 250), (500, 450), (700, 350)],
            'edges': [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)],
            'start': 0,
            'goal': 4
        },
        'total_packets': 12,
        'spawn_interval': 80,
        'success_threshold': 70,
        'starting_money': 500,
        'towers_available': ['Firewall', 'IDS'],
        'enemy_types': ['BASIC'],
        'enemy_config': {
            'BASIC': {'health': 8, 'speed': 1.8}
        }
    },
    
    {
        'number': 3,
        'name': 'Honeypot Tactics',
        'description': 'Use Honeypots to redirect enemies into kill zones',
        'concept': 'Deception & Misdirection',
        'topology': {
            'nodes': [
                (100, 350), (250, 250), (250, 450), 
                (450, 200), (450, 500), (600, 350), (750, 350)
            ],
            'edges': [
                (0, 1), (0, 2), (1, 3), (2, 4), 
                (3, 5), (4, 5), (5, 6)
            ],
            'start': 0,
            'goal': 6
        },
        'total_packets': 15,
        'spawn_interval': 70,
        'success_threshold': 75,
        'starting_money': 700,
        'towers_available': ['Firewall', 'IDS', 'Honeypot'],
        'enemy_types': ['BASIC', 'FAST'],
        'enemy_config': {
            'BASIC': {'health': 10, 'speed': 1.5},
            'FAST': {'health': 5, 'speed': 3.0}
        }
    },
    
    {
        'number': 4,
        'name': 'Advanced Defense',
        'description': 'Combine all towers to defend against varied threats',
        'concept': 'Defense in Depth',
        'topology': {
        'nodes': [
            (50, 350), (150, 250), (150, 450),   
            (280, 180), (280, 350), (280, 520),
            (430, 120), (430, 280), (430, 420), (430, 580),
            (580, 250), (580, 450),
            (720, 350), (850, 350)
        ],
        'edges': [
            (0, 1), (0, 2),
            (1, 3), (1, 4), (2, 4), (2, 5),
            (3, 6), (4, 7), (4, 8), (5, 8), (5, 9),
            (6, 10), (7, 10), (7, 11), (8, 10), (8, 11), (9, 11),
            (10, 12), (11, 12), (12, 13)
        ],
        'start': 0,
        'goal': 13
    },
        'total_packets': 20,
        'spawn_interval': 60,
        'success_threshold': 75,
        'starting_money': 900,
        'towers_available': ['Firewall', 'IDS', 'Honeypot'],
        'enemy_types': ['BASIC', 'FAST', 'TANK'],
        'enemy_config': {
            'BASIC': {'health': 12, 'speed': 1.5},
            'FAST': {'health': 6, 'speed': 3.5},
            'TANK': {'health': 25, 'speed': 0.8}
        }
    },
    
    {
        'number': 5,
        'name': 'Advanced Persistent Threat',
        'description': 'Endless waves - AI learns and adapts!',
        'concept': 'AI-Driven Adaptive Defense',
        'topology': {
            'nodes': [
                (50, 350), (150, 250), (150, 450),
                (280, 180), (280, 350), (280, 520),
                (430, 120), (430, 280), (430, 420), (430, 580),
                (580, 250), (580, 450),
                (720, 350), (850, 350)
            ],
            'edges': [
                (0, 1), (0, 2),
                (1, 3), (1, 4), (2, 4), (2, 5),
                (3, 6), (3, 7), (4, 7), (4, 8),
                (5, 8), (5, 9),
                (6, 10), (7, 10), (7, 11),
                (8, 10), (8, 11), (9, 11),
                (10, 12), (11, 12), (12, 13)
            ],
            'start': 0,
            'goal': 13
        },
        'mode': 'ENDLESS',
        'spawn_interval': 50,
        'starting_money': 1200,
        'towers_available': ['Firewall', 'IDS', 'Honeypot'],
        'enemy_types': ['BASIC', 'FAST', 'TANK', 'STEALTH', 'ENCRYPTED', 'ADAPTIVE', 'LEGITIMATE'],
        'enemy_config': {
            'BASIC': {'health': 15, 'speed': 1.5},
            'FAST': {'health': 8, 'speed': 4.0},
            'TANK': {'health': 35, 'speed': 0.7},
            'STEALTH': {'health': 10, 'speed': 2.0},
            'ENCRYPTED': {'health': 18, 'speed': 1.6},
            'ADAPTIVE': {'health': 20, 'speed': 1.8},
            'LEGITIMATE': {'health': float('inf'), 'speed': 1.5}
        },
        'legitimate_ratio': 0.3,  # 30% legitimate traffic
        'ai_learning': True,
        'dynamic_topology': False
    }
]

# Tower configurations
TOWERS = {
    'Firewall': {
        'cost': 100,
        'damage': 2,
        'range': 80,
        'cooldown': 20,
        'color': (80, 170, 255),
        'description': 'Direct packet blocking - high damage'
    },
    'IDS': {
        'cost': 80,
        'damage': 0,
        'range': 100,
        'cooldown': 10,
        'effect': 'slow',
        'slow_factor': 0.5,  # Reduces speed by 50%
        'color': (255, 200, 50),
        'description': 'Slows enemies - use with Firewalls'
    },
    'Honeypot': {
        'cost': 120,
        'damage': 0,
        'range': 120,
        'cooldown': 0,
        'effect': 'attract',
        'color': (255, 150, 255),
        'description': 'Attracts enemies to this location'
    }
}
# ... [your original config.py content as shown above] ...


# ADD THIS BLOCK AT THE END OF config.py:

DYNAMIC_TOPOLOGIES = [
    # Existing simple topology
    {
        'nodes': [(100, 350), (250, 200), (250, 500), (400, 100), (400, 300), (400, 500), (550, 200), (550, 500), (700, 350)],
        'edges': [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 4), (3, 6), (4, 6), (4, 7), (5, 7), (6, 8), (7, 8)],
        'start': 0,
        'goal': 8
    },
    # New complex topology
    {
        'nodes': [
            (50, 350), (150, 250), (150, 450),   
            (280, 180), (280, 350), (280, 520),
            (430, 120), (430, 280), (430, 420), (430, 580),
            (580, 250), (580, 450),
            (720, 350), (850, 350)
        ],
        'edges': [
            (0, 1), (0, 2),
            (1, 3), (1, 4), (2, 4), (2, 5),
            (3, 6), (4, 7), (4, 8), (5, 8), (5, 9),
            (6, 10), (7, 10), (7, 11), (8, 10), (8, 11), (9, 11),
            (10, 12), (11, 12), (12, 13)
        ],
        'start': 0,
        'goal': 13
    }
]
