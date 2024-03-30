import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors
white = (255, 255, 255)
gray = (200, 200, 200)
green = (0, 255, 0)
black = (0, 0, 0)

# Game Variables
card_size = (100, 120)
cards_rows = 4
cards_columns = 4
gap = 20
reset_button = pygame.Rect(screen_width - 120, screen_height - 50, 100, 40)

# Card states
face_down = 0
face_up = 1
matched = 2

# Load sound effect
match_sound = pygame.mixer.Sound("match_sound.wav")

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

def game_loop():
    global cards, start_time
    running = True
    first_selection = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if reset_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
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
                            else:
                                pygame.display.flip()
                                time.sleep(0.7)
                                first_selection['state'] = card['state'] = face_down
                            first_selection = None
                        break

        screen.fill(white)
        draw_cards()
        draw_timer()
        draw_reset_button()
        pygame.display.flip()

if __name__ == "__main__":
    game_loop()
    pygame.quit()
