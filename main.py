import pygame
import sys
import time
import random
from config import LEVELS, SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game_state import GameState
from towers import TowerManager
from ai_learning import AILearningSystem, generate_random_topology
from ui import UI

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Network Defender")
clock = pygame.time.Clock()

current_level = 1
game_state = None
tower_manager = None
enemies = []
ai_system = AILearningSystem()
ui = UI(screen)

GAME_STATE_INTRO, GAME_STATE_PLAYING, GAME_STATE_COMPLETE, GAME_STATE_FAILED = (
    "intro", "playing", "complete", "failed"
)
game_flow_state = GAME_STATE_INTRO
wave_popup_time = None

def init_level(level_num):
    global game_state, tower_manager, enemies, game_flow_state, wave_popup_time
    wave_popup_time = None
    override_topo = None

    if LEVELS[level_num - 1].get("mode") == "ENDLESS":
        override_topo = generate_random_topology(
            node_count=8, edge_count=12,
            screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT
        )

    game_state = GameState(level_num, override_topology=override_topo)
    game_state.tower_manager = TowerManager(tower_limit=10)  # tower cap 10
    tower_manager = game_state.tower_manager

    enemies.clear()
    game_flow_state = GAME_STATE_INTRO

def spawn_enemy():
    global enemies
    if game_state.level_number < 5:
        enemy_type = game_state.get_enemy_to_spawn()
    else:
        player_strategy = ai_system.analyze_defense_patterns()
        available_types = [
            t for t in game_state.level["enemy_types"] if t != "LEGITIMATE"
        ]
        legit_ratio = game_state.level.get("legitimate_ratio", 0)
        if legit_ratio > 0 and random.random() < legit_ratio:
            enemy_type = "LEGITIMATE"
        else:
            enemy_type = ai_system.select_counter_enemy_type(available_types, player_strategy)
    enemy = game_state.spawn_enemy(enemy_type)
    enemies.append(enemy)

def update_game():
    global game_flow_state, wave_popup_time
    if game_state is None or tower_manager is None:
        return

    for enemy in enemies:
        enemy.reset_slow()

    tower_manager.update(enemies)

    for enemy in enemies[:]:
        enemy.update()
        if enemy.health <= 0 and not enemy.is_legitimate:
            enemies.remove(enemy)
            game_state.enemy_destroyed(enemy)
        elif enemy.reached_goal:
            enemies.remove(enemy)
            game_state.enemy_reached_goal(enemy)

    if game_state.should_spawn_enemy(enemies):
        spawn_enemy()

    if game_state.level.get("mode") == "ENDLESS":
        if game_state.packets_spawned > 0 and game_state.packets_spawned % 20 == 0:
            ai_system.switch_topology(game_state, tower_manager, enemies)
            wave_popup_time = time.time()

    game_state.update(enemies)

    if game_flow_state == GAME_STATE_PLAYING and wave_popup_time:
        elapsed = time.time() - wave_popup_time
        if elapsed < 2:
            ui.draw_popup(f"Wave {game_state.packets_spawned // 10 + 1} Starting!")

    if game_state.level_complete:
        game_flow_state = GAME_STATE_COMPLETE
        ai_system.end_session(game_state.level_number, True)
    elif game_state.level_failed:
        game_flow_state = GAME_STATE_FAILED
        ai_system.end_session(game_state.level_number, False)

def draw_game():
    screen.fill((30, 30, 30))
    if game_state is None:
        font = pygame.font.SysFont(None, 48)
        screen.blit(
            font.render("Initializing...", True, (255, 255, 255)),
            (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2),
        )
        return
    ui.draw_network(
        game_state.nodes, game_state.edges, game_state.sources[0], game_state.goal_node
    )
    tower_manager.draw(screen)
    for e in enemies:
        e.draw(screen)
    ui.draw_hud(game_state)
    ui.draw_tower_menu(game_state.level["towers_available"], game_state.money)

    if game_flow_state == GAME_STATE_INTRO:
        ui.draw_level_intro(game_state)
    elif game_flow_state == GAME_STATE_COMPLETE:
        ui.draw_level_complete(game_state)
    elif game_flow_state == GAME_STATE_FAILED:
        ui.draw_level_failed(game_state)

def handle_tower_selection(mouse_pos):
    if game_state is None:
        return
    menu_x = SCREEN_WIDTH - 220
    menu_y = 120
    for i, tower_type in enumerate(game_state.level["towers_available"]):
        button_rect = pygame.Rect(menu_x, menu_y + i * 80, 190, 70)
        if button_rect.collidepoint(mouse_pos):
            ui.selected_tower_type = tower_type
def handle_tower_placement(mouse_pos, is_removal=False):
    if game_state is None or tower_manager is None:
        return
    node_id, node_pos = get_node_at_position(mouse_pos)
    if node_id is None:
        return

    # Enforce chokepoint placement restriction only on final level
    is_final_level = (game_state.level_number == len(LEVELS))
    if is_final_level and node_id not in game_state.chokepoints:
        print("X Tower placement only allowed on chokepoints in final level!")
        return

    if is_removal:
        removed = tower_manager.remove_tower_at(node_pos)
        if removed:
            print("Tower removed.")
        else:
            print("No tower to remove here.")
        return

    if ui.selected_tower_type is None:
        print("No tower selected to place")
        return

    can_place, message = tower_manager.can_place_tower(node_pos, ui.selected_tower_type, game_state.money)
    if can_place:
        cost = tower_manager.add_tower(node_pos[0], node_pos[1], ui.selected_tower_type)
        game_state.money -= cost
        print(f"Placed tower {ui.selected_tower_type} at {node_pos}, money left {game_state.money}")
    else:
        print(f"X Cannot place tower: {message}")



def get_node_at_position(pos):
    if game_state is None:
        return None, None
    for i, node_pos in enumerate(game_state.nodes):
        dx = pos[0] - node_pos[0]
        dy = pos[1] - node_pos[1]
        dist_sq = dx * dx + dy * dy
        if dist_sq < 900:
            print(f"Click near node {i} at {node_pos} detected")
            return i, node_pos
    print(f"No node near click at {pos}")
    return None, None


def main():
    global game_flow_state, current_level, wave_popup_time
    init_level(current_level)
    wave_popup_time = None
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_flow_state == GAME_STATE_PLAYING:
                    if event.button == 1:  # left click
                        if event.pos[0] > SCREEN_WIDTH - 230:
                            handle_tower_selection(event.pos)
                        else:
                            handle_tower_placement(event.pos, is_removal=False)
                    elif event.button == 3:  # right click remove tower
                        handle_tower_placement(event.pos, is_removal=True)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_flow_state == GAME_STATE_INTRO:
                        game_flow_state = GAME_STATE_PLAYING
                        wave_popup_time = time.time()
                    elif game_flow_state == GAME_STATE_COMPLETE:
                        current_level += 1
                        if current_level <= len(LEVELS):
                            init_level(current_level)
                            wave_popup_time = None
                        else:
                            running = False
                    elif game_flow_state == GAME_STATE_FAILED:
                        init_level(current_level)
                        wave_popup_time = None
                elif event.key == pygame.K_r:
                    if game_flow_state == GAME_STATE_FAILED:
                        init_level(current_level)
                        wave_popup_time = None
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if game_flow_state == GAME_STATE_PLAYING:
            update_game()

        draw_game()

        ui.update()
        ui.draw_message()
        if game_state is not None:
            ui.draw_blinking_nodes(game_state.nodes)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
