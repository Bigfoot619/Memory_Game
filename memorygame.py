import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 750
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
white = (255, 255, 255)
gray = (200, 200, 200)
green = (0, 255, 0)
black = (0, 0, 0)
red = (255, 0, 0)

# Game Variables
card_size = (100, 120)
cards_rows = 4
cards_columns = 4
gap = 20
reset_button = pygame.Rect(screen_width - 120, screen_height - 50, 100, 40)
play_again_button = pygame.Rect(screen_width / 2 - 50, screen_height / 2 - 20, 100, 40)
player_button_1 = pygame.Rect(screen_width / 4 - 150, screen_height / 2 - 20, 100, 40)
player_button_2 = pygame.Rect(3 * screen_width / 4 - 50, screen_height / 2 - 20, 100, 40)
time_attack_button = pygame.Rect(screen_width / 4 + 50, screen_height / 2 - 20, 150, 40)  # Time attack button
home_button = pygame.Rect(screen_width - 220, screen_height - 50, 100, 40)

# Card states
face_down = 0
face_up = 1
matched = 25

# Load sound effects
match_sound = pygame.mixer.Sound("match_sound.wav")

# Background music
pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1)

def initialize_game():
    # Generate pairs of numbers and shuffle them
    card_values = list(range(1, (cards_rows * cards_columns) // 2 + 1)) * 2
    random.shuffle(card_values)

    # Initialize card states
    cards = [{'rect': pygame.Rect(col * (card_size[0] + gap) + gap, row * (card_size[1] + gap) + gap, card_size[0], card_size[1]),
              'value': card_values.pop(),
              'state': face_down} for row in range(cards_rows) for col in range(cards_columns)]
    return cards, time.time()

cards, start_time = initialize_game()

def draw_cards():
    for card in cards:
        rect = card['rect']
        if card['state'] == face_down:
            pygame.draw.rect(screen, gray, rect)
        elif card['state'] == face_up:
            pygame.draw.rect(screen, white, rect)
            font = pygame.font.Font(None, 40)
            text = font.render(str(card['value']), True, green)
            screen.blit(text, text.get_rect(center=rect.center))
        else:
            pygame.draw.rect(screen, screen.get_at((0, 0)), rect)

def draw_home_button():
    pygame.draw.rect(screen, green, home_button)
    font = pygame.font.Font(None, 30)
    text = font.render('Home', True, black)
    screen.blit(text, text.get_rect(center=home_button.center))

def flip_card_animation(card, flip_to_face_up=True):
    global screen, cards, start_time, time_attack_mode, time_limit  # Ensure these global variables are accessible
    original_rect = card['rect'].copy()  # Copy the original rect to restore it after animation
    steps = 10  # Number of steps in the animation for smoothness

    for step in range(steps, 0, -1):
        card['rect'].width = original_rect.width * step // steps
        if card['rect'].width == 0:  # Avoid having width 0 which would make the rect invisible
            card['rect'].width = 1
        card['rect'].centerx = original_rect.centerx
        screen.fill(white)
        draw_cards()
        draw_timer(time_attack_mode, time_limit)  # Draw timer after updating screen
        draw_reset_button()  # Draw reset button after updating screen
        pygame.display.flip()
        pygame.time.delay(10)

    if flip_to_face_up:
        card['state'] = face_up
    else:
        card['state'] = face_down

    for step in range(1, steps + 1):
        card['rect'].width = original_rect.width * step // steps
        card['rect'].centerx = original_rect.centerx
        screen.fill(white)
        draw_cards()
        draw_timer(time_attack_mode, time_limit)  # Draw timer after updating screen
        draw_reset_button()  # Draw reset button after updating screen
        pygame.display.flip()
        pygame.time.delay(15)

    card['rect'] = original_rect  # Restore the original rect dimensions and position

        
def draw_timer(time_attack_mode, time_limit):
    current_time = time.time()
    if time_attack_mode:
        remaining_time = max(time_limit - (current_time - start_time), 0)
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_text = pygame.font.Font(None, 40).render(f'{minutes:02d}:{seconds:02d}', True, red)
    else:
        elapsed_time = current_time - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = pygame.font.Font(None, 40).render(f'{minutes:02d}:{seconds:02d}', True, black)
    screen.blit(timer_text, (screen_width - 100, 10))

def draw_reset_button():
    pygame.draw.rect(screen, green, reset_button)
    font = pygame.font.Font(None, 30)
    text = font.render('Reset', True, black)
    screen.blit(text, text.get_rect(center=reset_button.center))

def draw_play_again():
    pygame.draw.rect(screen, red, play_again_button)
    font = pygame.font.Font(None, 30)
    text = font.render('Play Again', True, white)
    screen.blit(text, text.get_rect(center=play_again_button.center))

def draw_player_buttons():
    font = pygame.font.Font(None, 30)
    pygame.draw.rect(screen, green, player_button_1)
    text = font.render('1 Player', True, black)
    screen.blit(text, text.get_rect(center=player_button_1.center))

    pygame.draw.rect(screen, green, player_button_2)
    text = font.render('2 Players', True, black)
    screen.blit(text, text.get_rect(center=player_button_2.center))

    pygame.draw.rect(screen, green, time_attack_button)  # Time attack button
    text = font.render('Time Attack', True, black)
    screen.blit(text, text.get_rect(center=time_attack_button.center))

    

def game_loop():
    global cards, start_time, time_attack_mode, time_limit
    running = True
    first_selection = None
    all_matched = False
    num_players = 0
    current_player = 1
    time_attack_mode = False
    time_limit = 60  # Time limit for time attack mode
    
    while running:
        all_matched = all(card['state'] == matched for card in cards)
        time_up = time_attack_mode and (time.time() - start_time) > time_limit

        if time_up and not all_matched:
            screen.fill(white)
            font = pygame.font.Font(None, 60)
            text = font.render('Maybe next time!', True, red)
            screen.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - 100))
            draw_player_buttons()
            draw_timer(time_attack_mode, time_limit)  # Ensure timer is visible
            draw_reset_button()  # Ensure reset button is visible
            pygame.display.flip()
            num_players = 0  # Ensure player buttons are reactivated
            while True:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_again_button.collidepoint(event.pos):
                        cards, start_time = initialize_game()
                        running = True  # Ensure the game loop continues
                        time_attack_mode = True  # Keep in time attack mode
                        time_limit = 60 # Reset time limit
                        break
                    if player_button_1.collidepoint(event.pos):
                        num_players = 1
                        time_attack_mode = False
                        cards, start_time = initialize_game()
                        break
                    elif player_button_2.collidepoint(event.pos):
                        num_players = 2
                        time_attack_mode = False
                        cards, start_time = initialize_game()
                        break
                    elif time_attack_button.collidepoint(event.pos):
                        num_players = 1
                        time_attack_mode = True
                        cards, start_time = initialize_game()
                        time_limit = 60 # Reset time limit
                        break
                    elif home_button.collidepoint(event.pos):
                        num_players = 0  # Reset to player selection
                        continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if home_button.collidepoint(event.pos):
                    num_players = 0  # Reset to player selection
                    time_attack_mode = False
                    continue
                if num_players == 0:
                    if player_button_1.collidepoint(event.pos):
                        num_players = 1
                    elif player_button_2.collidepoint(event.pos):
                        num_players = 2
                    elif time_attack_button.collidepoint(event.pos):
                        num_players = 1
                        time_attack_mode = True
                        cards, start_time = initialize_game()
                        time_limit = 60  # Reset time limit
                        continue

                if all_matched and play_again_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    if time_attack_mode:
                        time_limit -= 5  # Decrease time limit for next round
                        if time_limit <= 0:
                            time_limit = 5  # Set a minimum time limit
                    continue
                if reset_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    if time_attack_mode:
                        time_limit = 60  # Reset time limit for time attack mode
                    continue
                for card in cards:
                    if card['rect'].collidepoint(event.pos) and card['state'] == face_down:
                        flip_card_animation(card, True)  # Animate flipping card up
                        
                        if first_selection:
                            pygame.time.delay(400)  # Allow some time for the player to see the second card
                            if first_selection['value'] == card['value']:
                                # Cards match, keep them face up
                                first_selection['state'] = card['state'] = matched
                                match_sound.play()
                            else:
                                # Cards don't match, flip both back down
                                flip_card_animation(first_selection, False)  # Flip first selection back down
                                flip_card_animation(card, False)  # Flip current card back down
                            first_selection = None  # Reset first selection for the next turn
                        else:
                            first_selection = card  # Make current card the first selection
                        break  # Exit the loop after dealing with the card

        screen.fill(white)
        if num_players == 0:
            draw_player_buttons()
        else:
            draw_cards()
            draw_reset_button()
        draw_timer(time_attack_mode, time_limit)  # Draw timer after updating screen
        draw_home_button()
        if num_players == 2:
            player_turn_text = pygame.font.Font(None, 30).render(f'Player {current_player}\'s turn', True, black)
            screen.blit(player_turn_text, (0, 0))

        if all_matched:
            font = pygame.font.Font(None, 60)
            text = font.render('Well done!', True, green)
            screen.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - 100))
            draw_play_again()

        pygame.display.flip()


if __name__ == "__main__":
    game_loop()
    pygame.quit()
