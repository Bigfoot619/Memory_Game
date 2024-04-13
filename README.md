# Memory Card Game with Voice Control

Welcome to the Memory Card Game! This Python-powered game blends the classic gameplay of memory card matching with modern voice control capabilities, providing both a challenging and interactive experience. Built with Pygame and integrated with voice recognition via Vosk API, this game offers multiple modes including single player, two-player, and a thrilling time attack mode.

## Features

- **Multiple Game Modes**: Choose from single player, two player, or time attack modes to test your memory skills.
- **Voice Control**: Use your voice to play the game, making it accessible and hands-free.
- **Dynamic Sound Effects and Music**: Engage with the game as sound effects and background music enhance the playing experience.
- **Customizable Settings**: Adjust various settings like card count and game timers to fit your preference.
- **High Score Tracking**: Compete against yourself or friends with saved high scores for each game mode.

## Installation

To run the Memory Card Game, you'll need Python installed on your computer, along with the following packages:

- Pygame
- PyAudio
- Vosk API
- word2number

You can install all required packages using pip:

pip install pygame pyaudio vosk word2number


Ensure you also have the Vosk model downloaded:

1. Download the small Vosk model from [Vosk-API Models](https://alphacephei.com/vosk/models).
2. Place the downloaded model in your project directory or update the model path in the game code.

## How to Play

- **Start the Game**: Run `python memory_card_game.py` to launch the game.
- **Game Modes**:
  - **Single Player**: Match all cards at your own pace.
  - **Two Player**: Take turns to find matches with a friend.
  - **Time Attack**: Match all cards within the specified time.
- **Voice Control**: Activate voice control mode and use spoken numbers to flip cards.
- **Navigation**: Use mouse clicks to interact with on-screen buttons like `Home`, `Reset`, and `Play Again`.

## Game Controls

- **Mouse Click**: Interact with buttons and cards.
- **Voice Commands**: In voice control mode, say card numbers to flip them.

## Contributing

Contributions to the Memory Card Game are welcome! Please feel free to fork the repository, make changes, and submit a pull request.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgements

- Pygame Community for their extensive documentation and helpful forums.
- Vosk API for providing an effective offline voice recognition solution.

Enjoy playing and improving your memory skills with our Memory Card Game!
