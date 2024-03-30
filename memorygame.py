import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 650
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
player_button_1 = pygame.Rect(screen_width / 4 - 50, screen_height / 2 - 20, 100, 40)
player_button_2 = pygame.Rect(3 * screen_width / 4 - 50, screen_height / 2 - 20, 100, 40)

# Card states
face_down = 0
face_up = 1
matched = 2

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

def draw_timer():
    current_time = time.time()
    elapsed_time = current_time - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    font = pygame.font.Font(None, 40)
    timer_text = font.render(f'{minutes:02d}:{seconds:02d}', True, black)
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

def game_loop():
    global cards, start_time
    running = True
    first_selection = None
    all_matched = False
    num_players = 0
    current_player = 1

    while running:
        all_matched = all(card['state'] == matched for card in cards)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if num_players == 0:
                    if player_button_1.collidepoint(event.pos):
                        num_players = 1
                    elif player_button_2.collidepoint(event.pos):
                        num_players = 2
                    continue

                if all_matched and play_again_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    continue
                if reset_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    continue
                for card in cards:
                    if card['rect'].collidepoint(event.pos) and card['state'] == face_down:
                        card['state'] = face_up
                        if first_selection is None:
                            first_selection = card
                        else:
                            if first_selection['value'] == card['value']:
                                first_selection['state'] = card['state'] = matched
                                match_sound.play()
                                if num_players == 2:
                                    continue
                            else:
                                pygame.display.flip()
                                time.sleep(0.7)
                                first_selection['state'] = card['state'] = face_down
                                if num_players == 2:
                                    current_player = 2 if current_player == 1 else 1
                            first_selection = None
                        break

        screen.fill(white)
        if num_players == 0:
            draw_player_buttons()
        else:
            draw_cards()
            draw_timer()
            draw_reset_button()
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
