import pyaudio
import pygame
import random
import time
from vosk import Model, KaldiRecognizer
import json
from word2number import w2n

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 700
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
reset_button = pygame.Rect(500, screen_height - 60, 120, 50)
play_again_button = pygame.Rect(screen_width / 2 - 60, screen_height / 2 - 25, 120, 50)
player_button_1 = pygame.Rect(20, screen_height - 60, 120, 50)
player_button_2 = pygame.Rect(160, screen_height - 60, 120, 50)
time_attack_button = pygame.Rect(300, screen_height - 60, 140, 50)
voice_control_button = pygame.Rect(460, screen_height - 60, 160, 50)  # Adjusted for visibility
home_button = pygame.Rect(640, screen_height - 60, 100, 50)

current_player = 0
num_players = 0
voice_control_active = False  # Flag for voice control mode


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
        draw_home_button()

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
        draw_home_button()

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

    pygame.draw.rect(screen, green, voice_control_button)  # Voice control button
    font = pygame.font.Font(None, 30)
    text = font.render('Voice Control', True, black)
    screen.blit(text, text.get_rect(center=voice_control_button.center))

# Global voice model and stream variables
model = None
rec = None
p = None
stream = None

def initialize_voice_recognition():
    global model, rec, p, stream
    model = Model("vosk-model-small-en-us-0.15")  # Path might need adjustment based on your setup
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

def terminate_voice_recognition():
    global stream, p
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()

# Add voice recognition function
def voice_recognition():
    global rec, stream
    if stream is None:
        print("Voice recognition is not initialized.")
        return None
    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                try:
                    card_number = w2n.word_to_num(text)
                    # Ensure the number is within the range of cards 1-16
                    if 1 <= card_number <= 16:
                        return card_number
                    else:
                        print("Please say a number between 1 and 16.")

                except ValueError:
                    print("Please say a number.")  # Feedback for unrecognized input
                    continue  # If conversion fails, keep listening
    except Exception as e:
        print(f"An error occurred during voice recognition: {e}")

def select_card_by_voice():
    card_number = voice_recognition() - 1  # Subtract 1 for zero-based index
    if 0 <= card_number < len(cards):
        return cards[card_number]
    else:
        return None

def game_loop():
    global cards, start_time, time_attack_mode, time_limit, voice_control_active
    running = True
    first_selection = None
    all_matched = False
    num_players = 0
    current_player = 1
    selections_this_turn = 0  # Add a counter for selections in the current turn
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
                    elif voice_control_button.collidepoint(event.pos):
                        num_players = 1
                        time_attack_mode = False
                        voice_control_active = True  # Activate voice control
                        pygame.mixer.music.stop()
                        cards, start_time = initialize_game()
                        time_limit = 60 # Reset time limit

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if home_button.collidepoint(event.pos):
                    num_players = 0  # Reset to player selection
                    time_attack_mode = False
                    voice_control_active = False  # Deactivate voice control
                    cards, start_time = initialize_game()
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
                    elif voice_control_button.collidepoint(event.pos):
                        num_players = 1
                        pygame.mixer.music.stop()
                        voice_control_active = True  # Activate voice control
                        cards, start_time = initialize_game()

                if not voice_control_active:
                    for card in cards:
                      if card['rect'].collidepoint(event.pos) and card['state'] == face_down:
                          flip_card_animation(card, True)  # Animate flipping card up
                          selections_this_turn += 1  # Increment selections count
                          
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

                              if num_players == 2:
                                  current_player = 2 if current_player == 1 else 1
                                  selections_this_turn = 0  # Reset selections for the next player
                                  first_selection = None  # Reset first selection for the next turn
                                 
                          else:
                              first_selection = card  # Make current card the first selection
                          break  # Exit the loop after dealing with the card

                if all_matched and play_again_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    if time_attack_mode:
                        time_limit -= 5  # Decrease time limit for next round
                        if time_limit <= 0:
                            time_limit = 5  # Set a minimum time limit
                    
                if reset_button.collidepoint(event.pos):
                    cards, start_time = initialize_game()
                    all_matched = False
                    current_player = 1
                    if time_attack_mode:
                        time_limit = 60  # Reset time limit for time attack mode
                    

                if voice_control_active:
                    print(voice_control_active)
                    initialize_voice_recognition()
                    first_card = select_card_by_voice()
                    if first_card and first_card['state'] == face_down:
                        flip_card_animation(first_card, True)
                        second_card = select_card_by_voice()
                        if second_card and second_card != first_card and second_card['state'] == face_down:
                            flip_card_animation(second_card, True)
                            pygame.time.delay(400)  # Short delay to show the cards
                            if first_card['value'] == second_card['value']:
                                first_card['state'] = second_card['state'] = matched
                                match_sound.play()
                            else:
                                flip_card_animation(first_card, False)
                                flip_card_animation(second_card, False)


        screen.fill(white)
        if num_players == 2:
            player_turn_text = pygame.font.Font(None, 30).render(f'Player {current_player}\'s turn', True, black)
            screen.blit(player_turn_text, (0, 0))
        if num_players == 0:
            draw_player_buttons()
        else:
            draw_cards()
            draw_reset_button()
        draw_timer(time_attack_mode, time_limit)  # Draw timer after updating screen
        draw_home_button()
       

        if all_matched:
            font = pygame.font.Font(None, 60)
            text = font.render('Well done!', True, green)
            screen.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - 100))
            draw_play_again()

        pygame.display.flip()

    if voice_control_active:
        terminate_voice_recognition()

if __name__ == "__main__":
    game_loop()
    pygame.quit()