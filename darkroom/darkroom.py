import pygame
import sys
import time
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading


# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TEXT_AREA_WIDTH = 500  # Reduced text area width to make image area larger
IMAGE_AREA_WIDTH = SCREEN_WIDTH - TEXT_AREA_WIDTH

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
FONT = pygame.font.Font(pygame.font.match_font('courier'), 14)  # Font size
LINE_HEIGHT = FONT.get_linesize()

# Load Audio Files
audio_files = {
    "intro": "audio/intro.wav",
    "exit_prompt": "audio/exit_prompt.wav",
    "exit_yes": "audio/exit_yes.wav",
    "exit_no": "audio/exit_no.wav",
    "door_open": "audio/door_open.wav",
    "match_light": "audio/match_light.wav",
    "match_extinguish": "audio/match_extinguish.wav"
}

# Load Image Files
door_image = pygame.image.load("images/door.jpg")
door_image = pygame.transform.scale(door_image, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))
doorknob_image = pygame.image.load("images/doorknob.jpg")
doorknob_image = pygame.transform.scale(doorknob_image, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))
creep1 = pygame.image.load("images/creep1.png")
creep1 = pygame.transform.scale(creep1, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))
creep2 = pygame.image.load("images/creep2.png")
creep2 = pygame.transform.scale(creep2, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))
creep3 = pygame.image.load("images/creep3.png")
creep3 = pygame.transform.scale(creep3, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))
creep4 = pygame.image.load("images/creep4.png")
creep4 = pygame.transform.scale(creep4, (IMAGE_AREA_WIDTH, SCREEN_HEIGHT))

# Variable to store the current image
current_image = None

# Function to open the image window
def open_image_window():
    def reopen_window():
        root.destroy()
        open_image_window()

    root = tk.Tk()
    root.title(" ")
    root.geometry("400x300")

    img = Image.open("images/black-eyes.jpg")
    img = img.resize((400, 300), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    label = tk.Label(root, image=photo)
    label.image = photo  # Keep a reference to avoid garbage collection
    label.pack()

    root.protocol("WM_DELETE_WINDOW", reopen_window)
    root.mainloop()

# Function to open the image window in a separate thread
def open_image_window_thread():
    thread = threading.Thread(target=open_image_window)
    thread.daemon = True  # Ensure the thread exits when the main program exits
    thread.start()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("darkroom")

# Command input
command = ""
output_lines = []

# Game state variables
running = True
matches_left = 20
commands_since_last_match = 0
match_lit = False
inventory = []
awaiting_exit_confirmation = False
first_match_lit = False


# Items in the current scene
current_scene_items = ["box of matches", "key"]


# Function to wrap text
def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
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
def add_output(text, audio_key=None):
    global output_lines
    wrapped_lines = wrap_text(text, FONT, TEXT_AREA_WIDTH - 20)
    output_lines.extend(wrapped_lines)
    max_lines = (SCREEN_HEIGHT - 60) // LINE_HEIGHT  # Adjust to leave space for input
    while len(output_lines) > max_lines:
        output_lines.pop(0)

    # Play audio if provided
    if audio_key and audio_key in audio_files:
        pygame.mixer.music.load(audio_files[audio_key])
        pygame.mixer.music.play()

# Function to process commands
def process_command(command):
    global running, match_lit, first_match_lit, matches_left, commands_since_last_match, current_scene_items, awaiting_exit_confirmation
    commands_since_last_match += 1

    if match_lit and commands_since_last_match >= 5:
        match_lit = False
        add_output("The match goes out. The room is dark again.")
    
    if current_image:
        screen.blit(current_image, (TEXT_AREA_WIDTH, 0))

    if awaiting_exit_confirmation:
        if command.lower() in ["y", "yes"]:
            add_output("That's nice.", "exit_yes")
        else:
            add_output("Ok.", "exit_no")
        awaiting_exit_confirmation = False
        return

    if command.lower() == "help":               # Help Command
        add_output("Available commands:\nhelp\nexit\nlook\ninspect <item>\nscream\ninventory\ntake <item>\ndrop <item>\nuse <item>")
    elif command.lower() == "exit":             # Exit Command
        add_output("Do you want to leave the darkroom?(y/n)", "exit_prompt")
        awaiting_exit_confirmation = True
    elif command.lower() == "look":
        if match_lit:
            add_output("With the match lit, you see a dark, empty room. It's unsettlingly quiet. You notice a door in the corner.")
            if current_scene_items:
                add_output("You see the following items: " + ", ".join(current_scene_items))
            else:
                add_output("There are no items here.")
        else:
            add_output("It's pitch black. You can't see anything.")
    elif command.lower().startswith("inspect "):        # Inspect Command
        item = command[8:].strip()
        if item == "room":
            if match_lit:
                add_output("The room is empty, except for a small table and a door. The match is flickering. You feel someone watching you.")
            elif "box of matches" in inventory:
                add_output("It's too dark to inspect the room.")
            else:
                add_output("You feel around in the dark. You find a small table with a small cardboard box on it.")
        elif item in ["box of matches", "matches"]:
            if "box of matches" in inventory:
                add_output(f"You have {matches_left} matches left in the box.")
            else:
                add_output("You don't have any matches.")
        elif item in ["key"]:
            add_output("The key is old and rusty, but it looks like it might fit a lock.")
        elif item in ["door", "hidden door"]:
            if match_lit:
                add_output("The door looks old, but sturdy. There's a keyhole in the handle.")
                open_door_window()
            else:
                add_output("It's too dark to see the door.")
        else:
            add_output(f"You can't inspect {item}.")
    elif command.lower() == "scream":                   # Scream Command
        add_output("You scream into the void. Nothing happens.")
    elif command.lower() == "inventory":                # Inventory Command
        if inventory:
            add_output("You are carrying: " + ", ".join(inventory))
        else:
            add_output("You are carrying nothing.")
    elif command.lower().startswith("take "):           # Take Command
        item = command[5:].strip()
        if item in current_scene_items:
            inventory.append(item)
            current_scene_items.remove(item)
            add_output(f"You take the {item}.")
        elif item in ["box of matches", "matches", "box", "matchbox"] and "box of matches" in current_scene_items:
            inventory.append("box of matches")
            current_scene_items.remove("box of matches")
            add_output("You take the box of matches.")
        else:
            add_output(f"There is no {item} here.")
    elif command.lower().startswith("drop "):           # Drop Command
        item = command[5:].strip()
        if item in inventory:
            inventory.remove(item)
            current_scene_items.append(item)
            add_output(f"You drop the {item}.")
        else:
            add_output(f"You don't have a {item}.")
    elif command.lower().startswith("use "):            # Use Command
        item = command[4:].strip()
        if item in ["matches", "match", "box of matches", "matchbox"]:
            if matches_left > 0:
                matches_left -= 1
                match_lit = True
                commands_since_last_match = 0
                add_output(f"You light a match. The room is illuminated.")
                if not first_match_lit:
                    first_match_lit = True
                    open_image_window_thread()
            else:
                add_output("You have no matches left.")
        else:
            add_output(f"You can't use {item}.")
    else:
        add_output("Unknown command. Type HELP for a list of commands.")

    # Random chance for glitch effect
    if random.random() < 0.1:  # 10% chance
        display_glitch()
def open_door_window():
    root = tk.Tk()
    root.title("Inspecting the Door")
    root.geometry("400x300")

    label = tk.Label(root, text="You see a creepy door.", font=("Courier", 14))
    label.pack(pady=20)

    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=20)

    root.mainloop()

# Function to open a message window using tkinter
def open_message_window():
    root = tk.Tk()
    root.title("YOU ARE STILL HERE")
    root.geometry("300x200")

    label = tk.Label(root, text="NOBODY LEAVES THE DARKROOM NOBODY LEAVES THE DARKROOM NOBODY LEAVES THE DARKROOM NOBODY LEAVES THE DARKROOM NOBODY LEAVES THE DARKROOM NOBODY LEAVES THE DARKROOM", font=("Courier", 14))
    label.pack(pady=20)

    root.mainloop()

# Function to display intro sequence
def display_intro():
    intro_text = [
        "Initializing...",
        "Loading assets...",
        "System check: OK",
        "Memory check: OK",
        "Disk check: OK",
        "Security check: --ERROR--",
        "Overriding...",
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
        time.sleep(random.uniform(0.2, 1.5))  # Varied pause between 0.5 and 2.5 seconds

    # Display loading bar below the last line of text with varied pauses and jumps
    loading_bar = ""
    for i in range(30):
        loading_bar += "="
        if i < 10:
            time.sleep(random.uniform(0.05, 1))  # Slower updates at the beginning
        elif i < 20:
            time.sleep(random.uniform(0.05, 0.1))  # Medium updates in the middle
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
def main():
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
                open_message_window()
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