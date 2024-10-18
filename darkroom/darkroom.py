import pygame
import sys
import time
import random



# Initialize Pygame
pygame.init()

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

# Game state variables
running = True
matches_left = 20
commands_since_last_match = 0
match_lit = False
inventory = []
current_scene_items = []

# Items in the current scene
current_scene_items = ["Box of Matches", "key"]


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
def add_output(text):
    global output_lines
    wrapped_lines = wrap_text(text, FONT, TEXT_AREA_WIDTH - 20)
    output_lines.extend(wrapped_lines)
    max_lines = (SCREEN_HEIGHT - 60) // LINE_HEIGHT  # Adjust to leave space for input
    while len(output_lines) > max_lines:
        output_lines.pop(0)

# Function to process commands
def process_command(command):
    global running, match_lit, matches_left, commands_since_last_match, current_scene_items
    commands_since_last_match += 1

    if match_lit and commands_since_last_match >= 5:
        match_lit = False
        add_output("The match goes out. The room is dark again.")

    if command.lower() == "help":
        add_output("Available commands:\nhelp\nexit\nlook\ninspect <item>\nscream\ninventory\ntake <item>\ndrop <item>\nuse <item>")
    elif command.lower() == "exit":
        running = False
    elif command.lower() == "look":
        if match_lit:
            add_output("With the match lit, you see a dark, empty room. It's unsettlingly quiet. You notice a hidden door in the corner.")
            if current_scene_items:
                add_output("You see the following items: " + ", ".join(current_scene_items))
            else:
                add_output("There are no items here.")
        else:
            add_output("It's pitch black. You can't see anything.")
    elif command.lower().startswith("inspect "):
        item = command[8:].strip()
        if item == "room":
            add_output("You feel around in the dark and find a box of matches on a table.")
            if "box of matches" not in inventory and "box of matches" not in current_scene_items:
                current_scene_items.append("box of matches")
        elif item == "matches":
            if "box of matches" in inventory:
                add_output(f"You have {matches_left} matches left in the box.")
            else:
                add_output("You don't have a box of matches.")
        else:
            add_output(f"You can't inspect {item}.")
    elif command.lower() == "scream":
        add_output("You scream into the void. Nothing happens.")
    elif command.lower() == "inventory":
        if inventory:
            add_output("You are carrying: " + ", ".join(inventory))
        else:
            add_output("You are carrying nothing.")
    elif command.lower().startswith("take "):
        item = command[5:].strip()
        if item in current_scene_items:
            inventory.append(item)
            current_scene_items.remove(item)
            add_output(f"You take the {item}.")
            if item == "box of matches":
                matches_left = 20
        else:
            add_output(f"There is no {item} here.")
    elif command.lower().startswith("drop "):
        item = command[5:].strip()
        if item in inventory:
            inventory.remove(item)
            current_scene_items.append(item)
            add_output(f"You drop the {item}.")
        else:
            add_output(f"You don't have a {item}.")
    elif command.lower().startswith("use "):
        item = command[4:].strip()
        if item == "matches":
            if matches_left > 0:
                matches_left -= 1
                match_lit = True
                commands_since_last_match = 0
                add_output(f"You light a match. You have {matches_left} matches left.")
            else:
                add_output("You have no matches left.")
        else:
            add_output(f"You can't use {item}.")
    else:
        add_output("Unknown command.")

    # Random chance for glitch effect
    if random.random() < 0.1:  # 10% chance
        display_glitch()

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