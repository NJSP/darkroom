import pygame
import sys
import time
import random
import pyttsx3
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
from pydub.generators import WhiteNoise
import wave
import os
import simpleaudio as sa


# Initialize Pygame
pygame.init()

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TEXT_AREA_WIDTH = 500  # Reduced text area width to make image area larger
IMAGE_AREA_WIDTH = SCREEN_WIDTH - TEXT_AREA_WIDTH

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
FONT = pygame.font.Font(pygame.font.match_font('courier'), 20)  # Reduced font size
LINE_HEIGHT = FONT.get_linesize()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("darkroom")

# Command input
command = ""
output_lines = []

# Inventory
inventory = []

# Items in the current scene
current_scene_items = ["flashlight", "key"]

# Flashlight state
flashlight_on = False

# Function to apply rough and distorted effect
def apply_audio_effects(audio_segment):
    # Apply effects: increase volume, add distortion
    audio_segment = audio_segment + 1  # Increase volume
    audio_segment = audio_segment.high_pass_filter(30)
    audio_segment = audio_segment.low_pass_filter(300)
    audio_segment = audio_segment.speedup(playback_speed=1.1)
    # Add white noise
    noise = WhiteNoise().to_audio_segment(duration=len(audio_segment))
    audio_segment = audio_segment.overlay(noise - 40)  # Adjust noise volume
    audio_segment = audio_segment.set_frame_rate(8000).set_sample_width(1)
    
    return audio_segment

# Function to speak text with effects
def speak_with_effects(text):
    try:
        print(f"Speaking text: {text}")
        # Generate TTS audio and store it in an in-memory buffer
        buffer = BytesIO()
        tts_engine.save_to_file(text, "temp.wav")
        tts_engine.runAndWait()
        print("TTS audio saved to temp.wav")
    
        # Read the saved file into the buffer
        with open("temp.wav", "rb") as f:
            buffer.write(f.read())
        buffer.seek(0)
        print("TTS audio loaded from temp.wav")

        # Load audio from buffer
        sound = AudioSegment.from_file(buffer, format="wav")
        print("Audio loaded from buffer")

        # Apply effects
        modified_sound = apply_audio_effects(sound)
        print("Effects applied")

        # Export modified sound to a new buffer
        modified_buffer = BytesIO()
        modified_sound.export(modified_buffer, format="wav")
        modified_buffer.seek(0)
        print("Modified audio exported to buffer")

        # Play the modified sound using simpleaudio
        with wave.open(modified_buffer, 'rb') as wf:
            wave_obj = sa.WaveObject.from_wave_read(wf)
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Wait until sound has finished playing
            print("Modified audio played successfully")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists("temp.wav"):
            print("Deleting temp.wav...")
            os.remove("temp.wav")


# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    
    lines.append(current_line)
    return lines

# Function to add text to the terminal
def add_output(text, is_dialogue=False):
    global output_lines
    wrapped_lines = wrap_text(text, FONT, TEXT_AREA_WIDTH - 20)
    output_lines.extend(wrapped_lines)
    if is_dialogue:
        speak_with_effects(text)  # Speak the line using Text-to-Speech with effects
    max_lines = (SCREEN_HEIGHT - 60) // LINE_HEIGHT  # Adjust to leave space for input
    while len(output_lines) > max_lines:
        output_lines.pop(0)

# Function to process commands
def process_command(command):
    global running, flashlight_on
    if command.lower() == "help":
        add_output("Available commands:\nhelp\nexit\nlook\nscream\ninventory\ntake <item>\ndrop <item>\nuse <item>")
    elif command.lower() == "exit":
        running = False
    elif command.lower() == "look":
        if flashlight_on:
            add_output("You see a dark, empty room. It's unsettlingly quiet. With the flashlight on, you notice a hidden door in the corner.", is_dialogue=True)
        else:
            add_output("You see a dark, empty room. It's unsettlingly quiet.", is_dialogue=True)
            if current_scene_items:
                add_output("You see the following items: " + ", ".join(current_scene_items), is_dialogue=True)
            else:
                add_output("There are no items here.", is_dialogue=True)
    elif command.lower() == "scream":
        add_output("You scream into the void. Nothing happens.", is_dialogue=True)
    elif command.lower() == "inventory":
        if inventory:
            add_output("You are carrying: " + ", ".join(inventory), is_dialogue=True)
        else:
            add_output("You are not carrying anything.", is_dialogue=True)
    elif command.lower().startswith("take "):
        item = command[5:].strip()
        if item in current_scene_items:
            inventory.append(item)
            current_scene_items.remove(item)
            add_output(f"You take the {item}.", is_dialogue=True)
        else:
            add_output(f"You can't take the {item}. It's not here.", is_dialogue=True)
    elif command.lower().startswith("drop "):
        item = command[5:].strip()
        if item in inventory:
            inventory.remove(item)
            current_scene_items.append(item)
            add_output(f"You drop the {item}.", is_dialogue=True)
        else:
            add_output("You don't have that item.", is_dialogue=True)

    # Random chance for glitch effect
    if random.random() < 0.1:  # 10% chance
        display_glitch()

# Function to display intro sequence
def display_intro():
    intro_text = [
        "Initializing...",
        "Loading assets...",
        "Setting up environment...",
        "System check: OK",
        "Memory check: OK",
        "Disk check: OK",
        "Network check: OK",
        "Launching darkroom..."
    ]

    # Display scrolling text with varied pauses
    for line in intro_text:
        add_output(line)
        screen.fill(BLACK)
        for i, output_line in enumerate(output_lines):
            text_surface = FONT.render(output_line, True, WHITE)
            screen.blit(text_surface, (10, 10 + i * LINE_HEIGHT))
        pygame.display.flip()
        time.sleep(random.uniform(0.5, 2.5))  # Varied pause between 0.5 and 2.5 seconds

    # Display loading bar below the last line of text with varied pauses and jumps
    loading_bar = ""
    for i in range(30):
        loading_bar += "="
        if i < 10:
            time.sleep(random.uniform(0.05, 1))  # Slower updates at the beginning
        elif i < 20:
            time.sleep(random.uniform(0.05, 1))  # Medium updates in the middle
        else:
            time.sleep(random.uniform(0.001, 0.02))  # Faster updates towards the end
        screen.fill(BLACK)
        for j, output_line in enumerate(output_lines):
            text_surface = FONT.render(output_line, True, WHITE)
            screen.blit(text_surface, (10, 10 + j * LINE_HEIGHT))
        text_surface = FONT.render(f"[{loading_bar:<30}]", True, WHITE)
        screen.blit(text_surface, (10, 10 + len(output_lines) * LINE_HEIGHT))
        pygame.display.flip()

    # Black screen for 2 seconds
    screen.fill(BLACK)
    pygame.display.flip()
    time.sleep(2)

    # Display "darkroom" text
    screen.fill(BLACK)
    text_surface = FONT.render("darkroom", True, WHITE)
    screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    time.sleep(2)

    # Display glitch effect
    display_glitch()

    # Black screen for 2 seconds
    screen.fill(BLACK)
    pygame.display.flip()
    time.sleep(2)

# Function to display glitch effect using PygameShader
def display_glitch():
    print("Displaying glitch effect...")
    for _ in range(5):  # Number of glitch frames
        for _ in range(10):  # Number of glitch lines per frame
            y = random.randint(0, SCREEN_HEIGHT)
            glitch_height = random.randint(1, 10)
            glitch_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.rect(screen, glitch_color, (0, y, SCREEN_WIDTH, glitch_height))
        pygame.display.flip()
        time.sleep(0.05)  # Brief pause to display each glitch frame
    print("Glitch effect displayed successfully.")

# Main game loop
running = True
display_intro()  # Display the intro sequence
output_lines.clear()  # Clear the intro text before starting the main game
while running:
    screen.fill(BLACK)

    # Draw output lines
    for i, line in enumerate(output_lines):
        text_surface = FONT.render(line, True, WHITE)
        screen.blit(text_surface, (10, 10 + i * LINE_HEIGHT))

    # Draw command input
    command_surface = FONT.render("> " + command, True, WHITE)
    screen.blit(command_surface, (10, SCREEN_HEIGHT - 50))

    # Draw image placeholder
    pygame.draw.rect(screen, WHITE, (TEXT_AREA_WIDTH, 0, IMAGE_AREA_WIDTH, SCREEN_HEIGHT), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                add_output("> " + command)
                process_command(command)
                command = ""
            elif event.key == pygame.K_BACKSPACE:
                command = command[:-1]
            else:
                command += event.unicode

    pygame.display.flip()

pygame.quit()
sys.exit()