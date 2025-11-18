import pygame

# Expanded network topology with more nodes
NODES = [
    (100, 300),   # 0 - Start
    (200, 300),   # 1
    (300, 300),   # 2
    (400, 200),   # 3
    (400, 400),   # 4
    (500, 250),   # 5
    (600, 350),   # 6
    (700, 300),   # 7 - End/Core
]

# More edges to create multiple paths
EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (2, 4),
    (3, 5),
    (4, 6),
    (5, 7),
    (6, 7),
]

def draw_board(screen):
    # Draw edges
    for start, end in EDGES:
        pygame.draw.line(screen, (120, 220, 150), NODES[start], NODES[end], 4)
    
    # Draw nodes
    for i, pos in enumerate(NODES):
        # Different color for start and end nodes
        if i == 0:
            color = (100, 255, 100)  # Green for start
        elif i == len(NODES) - 1:
            color = (255, 100, 100)  # Red for core/end
        else:
            color = (200, 200, 100)  # Yellow for intermediate
        
        pygame.draw.circle(screen, color, pos, 25)
        pygame.draw.circle(screen, (60, 60, 60), pos, 25, 3)
        
        # Draw node labels
        font = pygame.font.SysFont(None, 24)
        label = font.render(str(i), True, (255, 255, 255))
        screen.blit(label, (pos[0] - 7, pos[1] - 12))
