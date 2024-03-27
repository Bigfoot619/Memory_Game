import random
import pygame

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Define the dimensions of the game screen
WIDTH = 800
HEIGHT = 600
ROWS = 4
COLS = 4

# Set up the screen
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")

# Define card class
class Card:
    def __init__(self, content, x, y):
        self.content = content
        self.x = x
        self.y = y
        self.covered = True  # When true, card shows backside; when false, shows content

    def draw(self):
        if self.covered:
            # Draw card backside
            pygame.draw.rect(screen, GREY, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT))
        else:
            # Draw card face with content
            pygame.draw.rect(screen, WHITE, (self.x, self.y, CARD_WIDTH, CARD_HEIGHT))
            font = pygame.font.Font(None, 50)
            text = font.render(str(self.content), True, BLACK)
            text_rect = text.get_rect(center=(self.x + CARD_WIDTH // 2, self.y + CARD_HEIGHT // 2))
            screen.blit(text, text_rect)

    def flip(self):
        self.covered = not self.covered

# Define constants
CARD_WIDTH = WIDTH // COLS - 30  # Adjusting for margin
CARD_HEIGHT = HEIGHT // ROWS - 30  # Adjusting for margin
MARGIN = 20

# Create a list of card content (replace with letters/numbers)
card_contents = list("AABBCCDDEEFFGGHH")
random.shuffle(card_contents)

# Create a list of cards
cards = []
for i in range(ROWS):
    for j in range(COLS):
        content = card_contents[i * COLS + j]
        card = Card(content, j * (CARD_WIDTH + MARGIN) + MARGIN, i * (CARD_HEIGHT + MARGIN) + MARGIN)
        cards.append(card)

# Game variables
first_card = None
second_card = None
found = []  # Track matched cards

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            for card in cards:
                # Skip cards that are already found
                if card in found:
                    continue

                if card.x <= x <= card.x + CARD_WIDTH and card.y <= y <= card.y + CARD_HEIGHT:
                    if card.covered:  # Only allow flipping if the card is covered
                        card.flip()
                        if first_card is None:
                            first_card = card
                        elif second_card is None and card != first_card:
                            second_card = card
                            pygame.time.delay(500)  # Delay to allow the second card to be seen

                            if first_card.content == second_card.content:
                                found.extend([first_card, second_card])  # Add matched cards to found list
                                first_card = None
                                second_card = None
                            else:
                                first_card.flip()
                                second_card.flip()
                                first_card = None
                                second_card = None

    # Draw the game screen
    screen.fill(BLACK)
    for card in cards:
        card.draw()
    pygame.display.flip()
