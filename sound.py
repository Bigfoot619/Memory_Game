from gtts import gTTS

# Generate speech for "Nice match!"
tts = gTTS("Nice match!", lang="en")
tts.save("match_sound.wav")

print("Sound file 'match_sound.wav' has been saved.")
