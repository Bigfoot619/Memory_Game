import random
import pygame

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Define card symbols
SYMBOLS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Define card properties
CARD_WIDTH, CARD_HEIGHT = 100, 150
CARD_GAP = 20
ROWS, COLS = 4, 4
CARDS = [(x, y) for x in range(COLS) for y in range(ROWS)]

# Shuffle the cards
random.shuffle(CARDS)

# Assign symbols to cards
card_symbols = SYMBOLS * (ROWS * COLS // len(SYMBOLS))
random.shuffle(card_symbols)

# Create a dictionary to store card states
card_states = {pos: False for pos in CARDS}

# Initialize game variables
score = 0
selected_cards = []
game_over = False

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            mouse_pos = pygame.mouse.get_pos()
            clicked_row = mouse_pos[1] // (CARD_HEIGHT + CARD_GAP)
            clicked_col = mouse_pos[0] // (CARD_WIDTH + CARD_GAP)
            clicked_pos = (clicked_col, clicked_row)

            if clicked_pos in card_states and not card_states[clicked_pos]:
                selected_cards.append(clicked_pos)

                if len(selected_cards) == 2:
                    pos1, pos2 = selected_cards
                    symbol1 = card_symbols[CARDS.index(pos1)]
                    symbol2 = card_symbols[CARDS.index(pos2)]

                    if symbol1 == symbol2:
                        card_states[pos1] = card_states[pos2] = True
                        score += 1

                    selected_cards = []

                    if all(card_states.values()):
                        game_over = True

    # Clear the window
    WINDOW.fill(WHITE)

    # Draw the cards
    for i, pos in enumerate(CARDS):
        col, row = pos
        x = col * (CARD_WIDTH + CARD_GAP) + CARD_GAP
        y = row * (CARD_HEIGHT + CARD_GAP) + CARD_GAP
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

        if card_states[pos]:
            pygame.draw.rect(WINDOW, GRAY, rect)
        else:
            pygame.draw.rect(WINDOW, BLACK, rect)
            if pos in selected_cards:
                symbol = card_symbols[i]
                text = pygame.font.Font(None, 72).render(symbol, True, WHITE)
                text_rect = text.get_rect(center=rect.center)
                WINDOW.blit(text, text_rect)

    # Draw the score
    score_text = pygame.font.Font(None, 36).render(f"Score: {score}", True, BLACK)
    WINDOW.blit(score_text, (10, 10))

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()