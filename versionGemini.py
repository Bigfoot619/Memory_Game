import pygame
import random

pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)

# Define screen dimensions
WIDTH = 400
HEIGHT = 400

# Define card size
CARD_WIDTH = WIDTH // 4
CARD_HEIGHT = HEIGHT // 4

# Define font
FONT = pygame.font.Font(None, 32)

# Define game state variables
board = []  # List to store card states (covered/uncovered)
first_card = None  # Keeps track of the first clicked card
second_card = None  # Keeps track of the second clicked card
game_over = False

# Function to initialize the game
def init_game():
  global board, first_card, second_card
  # Create an empty board with covered cards
  for _ in range(4):
    board.append([False] * 4)
  # Shuffle letters (A-H) twice to create pairs
  letters = list("AABBCCDDEEFFGGHH")
  random.shuffle(letters)
  random.shuffle(letters)
  # Assign letters to the board
  for i in range(4):
    for j in range(4):
      board[i][j] = letters.pop()
  # Reset card selection
  first_card = None
  second_card = None

# Function to draw the game board
def draw_board():
  # Draw grid lines
  for i in range(1, 4):
    pygame.draw.line(screen, GREY, (0, i * CARD_HEIGHT), (WIDTH, i * CARD_HEIGHT), 2)
    pygame.draw.line(screen, GREY, (i * CARD_WIDTH, 0), (i * CARD_WIDTH, HEIGHT), 2)
  # Draw cards
  for i in range(4):
    for j in range(4):
      color = WHITE if board[i][j] else GREY
      pygame.draw.rect(screen, color, (j * CARD_WIDTH, i * CARD_HEIGHT, CARD_WIDTH, CARD_HEIGHT))
      # Draw card text
      text = FONT.render(board[i][j], True, BLACK)
      text_rect = text.get_rect(center=(j * CARD_WIDTH + CARD_WIDTH // 2, i * CARD_HEIGHT + CARD_HEIGHT // 2))
      if not board[i][j]:  # Only show text for uncovered cards
        screen.blit(text, text_rect)


# Function to handle user clicks
def handle_click(pos):
  global first_card, second_card
  # Get the clicked card coordinates
  x, y = pos
  card_x = x // CARD_WIDTH
  card_y = y // CARD_HEIGHT
  # Check if a card is already clicked
  if not board[card_y][card_x]:
    # Reveal the clicked card
    board[card_y][card_x] = True
    if not first_card:
      first_card = (card_x, card_y)
    else:
      second_card = (card_x, card_y)

# Function to check for a match
def check_match():
  global first_card, second_card, game_over
  if first_card and second_card and first_card != second_card:
    # Check if cards match
    if board[first_card[1]][first_card[0]] == board[second_card[1]][second_card[0]]:
      # Cards match, keep them revealed
      pass
    else:
      # Cards don't match, cover them again after a short delay
      pygame.time.delay(1000)
      board[first_card[1]][first_card[0]] = False
      board[second_card[1]][second_card[0]] = False
    first_card = None
    second_card = None
  # Check if all cards are matched (game won)
  game_over = all(card for row in board for card in row)

# Main game loop
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")
