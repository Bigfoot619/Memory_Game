import pyaudio
import pygame
import random
import time
from vosk import Model, KaldiRecognizer
import json
from word2number import w2n
import threading

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
voice_recognition_thread = None  # Global variable to control the voice recognition thread
voice_command_result = None  # Holds the result from voice recognition
voice_commands = []
players_matches = [0,0]
message_start_time = None
show_time_attack_message = False


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

def display_time_attack_message():
    message = "Time Attack Mode!\nYou have 60 seconds to match all cards\nSucceed, and the next level will have 5 seconds less.\nGood luck!"
    render_multiline_text(message, 20, 100, 40, red)

def render_multiline_text(text, x, y, font_size, color):
    font = pygame.font.Font(None, font_size)
    lines = text.split('\n')
    for line in lines:
        text_surface = font.render(line, True, color)
        screen.blit(text_surface, (x, y))
        y += font_size  # Move to the next line position

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

def draw_scores(player1_score, player2_score):
    font = pygame.font.Font(None, 40)
    score_text_1 = font.render(f'Player 1: {player1_score}', True, black)
    score_text_2 = font.render(f'Player 2: {player2_score}', True, black)

    # Calculate positions for the score displays on the right side of the screen
    score_x_position = screen_width - 150  # X position for scores, 150 pixels from the right edge
    score_y_position_1 = 50  # Y position for player 1 score, placed below the timer with some padding
    score_y_position_2 = 90  # Y position for player 2 score, placed below player 1 score with some spacing

    # Position the score displays on the screen
    screen.blit(score_text_1, (score_x_position - score_text_1.get_width(), score_y_position_1))  # Right-align text
    screen.blit(score_text_2, (score_x_position - score_text_2.get_width(), score_y_position_2))  # Right-align text

# Global voice model and stream variables
model = None
rec = None
p = None
stream = None


def initialize_voice_recognition():
    global model, rec, p, stream, voice_recognition_thread, voice_control_active
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()
    if voice_recognition_thread is None or not voice_recognition_thread.is_alive():
        voice_control_active = True
        voice_recognition_thread = threading.Thread(target=voice_recognition, daemon=True)
        voice_recognition_thread.start()

def terminate_voice_recognition():
    global voice_control_active, voice_recognition_thread, stream, p
    voice_control_active = False
    if voice_recognition_thread is not None:
        voice_recognition_thread.join()
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p is not None:
        p.terminate()

# Function to handle voice recognition on a separate thread
def voice_recognition():
    global voice_control_active, rec, stream, voice_command_result, voice_commands
    try:
        while voice_control_active:
            data = stream.read(4096, exception_on_overflow=False)
            if len(data) == 0 or not voice_control_active:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                try:
                    card_number = w2n.word_to_num(text)
                    if 1 <= card_number <= 16:
                        voice_commands.append(card_number)
                    else:
                        print("Please say a number between 1 and 16.")
                except ValueError:
                    print("Please say a number between 1 and 16")
    except Exception as e:
        print(f"An error occurred during voice recognition: {e}")
        

def game_loop():
    global cards, start_time, time_attack_mode, time_limit, voice_control_active, voice_commands, players_matches, num_players, message_start_time, show_time_attack_message
    won_last_hand = 0
    running = True
    first_selection = None
    all_matched = False
    current_player = 1
    selections_this_turn = 0  # Add a counter for selections in the current turn
    time_attack_mode = False
    time_limit = 60  # Time limit for time attack mode
    voice_initialization_flag = False
    

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if home_button.collidepoint(event.pos):
                    num_players = 0  # Reset to player selection
                    time_attack_mode = False
                    voice_initialization_flag = False
                    if voice_control_active:
                        terminate_voice_recognition()
                        pygame.mixer.music.play(-1)
                    cards, start_time = initialize_game()
                    # continue
                if num_players == 0:
                    if player_button_1.collidepoint(event.pos):
                        num_players = 1
                    elif player_button_2.collidepoint(event.pos):
                        num_players = 2
                        players_matches = [0 for _ in players_matches]
                    elif time_attack_button.collidepoint(event.pos):
                        num_players = 1
                        time_attack_mode = True
                        cards, start_time = initialize_game()
                        time_limit = 60  # Reset time limit
                        message_start_time = pygame.time.get_ticks()  # Note the start time to track 3 seconds
                        show_time_attack_message = True 

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
                                  won_last_hand = current_player
                                  players_matches[current_player - 1] += 1

                              else:
                                  # Cards don't match, flip both back down
                                  flip_card_animation(first_selection, False)  # Flip first selection back down
                                  flip_card_animation(card, False)  # Flip current card back down
                                  won_last_hand = None

                              if num_players == 2:
                                if won_last_hand != current_player:
                                    current_player = 2 if current_player == 1 else 1

                              selections_this_turn = 0
                              first_selection = None 
                              
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
                    if (num_players == 2):
                        players_matches = [0 for _ in players_matches]
                    all_matched = False
                    current_player = 1
                    if time_attack_mode:
                        time_limit = 60  # Reset time limit for time attack mode
                    
                
        if voice_control_active:
            if not voice_initialization_flag:
                voice_initialization_flag = True
                initialize_voice_recognition()
            if len(voice_commands) > 1:
                first_card_number = voice_commands.pop(0) - 1 
                first_card = cards[first_card_number]
                if first_card and first_card['state'] == face_down:
                    flip_card_animation(first_card, True)
                    if len(voice_commands) > 0:
                        second_card_number = voice_commands.pop(0) - 1 
                        second_card = cards[second_card_number]
                        if second_card and second_card != first_card and second_card['state'] == face_down:
                            flip_card_animation(second_card, True)
                            pygame.time.delay(400)  # Short delay to show the cards
                            if first_card['value'] == second_card['value']:
                                first_card['state'] = second_card['state'] = matched
                                match_sound.play()
                            else:
                                flip_card_animation(first_card, False)
                                flip_card_animation(second_card, False)  
                            first_selection = None


        screen.fill(white)
        if num_players == 0:
            draw_player_buttons()
        else:
            draw_cards()
            draw_reset_button()

        if num_players == 2:
            draw_scores(players_matches[0], players_matches[1])
            player_turn_text = pygame.font.Font(None, 30).render(f'Player {current_player}\'s turn', True, black)
            screen.blit(player_turn_text, (0, 0))

        draw_timer(time_attack_mode, time_limit)  # Draw timer after updating screen
        draw_home_button()
       
        if all_matched:
            font = pygame.font.Font(None, 60)
            text = font.render('Well done!', True, green)
            screen.blit(text, (screen_width / 2 - text.get_width() / 2, screen_height / 2 - 100))
            draw_play_again()

        if show_time_attack_message:
            display_time_attack_message()
            current_time = pygame.time.get_ticks()
            if current_time - message_start_time > 5000:  # 3 seconds have passed
                show_time_attack_message = False

        pygame.display.flip()

    if voice_control_active:
        terminate_voice_recognition()

if __name__ == "__main__":
    game_loop()
    pygame.quit()
