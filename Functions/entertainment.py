import os
import random
import requests
import webbrowser
import time
import pygame
from typing import Dict, List, Any, Union, Tuple

# Initialize pygame mixer for audio playback
pygame.mixer.init()

class MusicPlayer:
    def __init__(self, music_folder: str = "music"):
        self.music_folder = music_folder
        self.current_track = None
        self.playing = False
        self.volume = 0.5
        
        # Create music folder if it doesn't exist
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
    
    def get_all_tracks(self) -> List[str]:
        """Get all music tracks in the music folder"""
        if not os.path.exists(self.music_folder):
            return []
        
        supported_formats = ('.mp3', '.wav', '.ogg')
        return [f for f in os.listdir(self.music_folder) 
                if os.path.isfile(os.path.join(self.music_folder, f)) 
                and f.lower().endswith(supported_formats)]
    
    def play(self, track_name: str = None) -> str:
        """Play a specific track or a random one if none specified"""
        tracks = self.get_all_tracks()
        
        if not tracks:
            return "No music files found in the music folder"
        
        if track_name:
            if track_name in tracks:
                selected_track = track_name
            else:
                matching_tracks = [t for t in tracks if track_name.lower() in t.lower()]
                if matching_tracks:
                    selected_track = matching_tracks[0]
                else:
                    return f"No track found matching '{track_name}'"
        else:
            selected_track = random.choice(tracks)
        
        try:
            pygame.mixer.music.load(os.path.join(self.music_folder, selected_track))
            pygame.mixer.music.play()
            self.current_track = selected_track
            self.playing = True
            return f"Now playing: {selected_track}"
        except Exception as e:
            return f"Error playing music: {str(e)}"
    
    def pause(self) -> str:
        """Pause the currently playing track"""
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            return "Music paused"
        return "No music is currently playing"
    
    def resume(self) -> str:
        """Resume the paused track"""
        if self.current_track and not self.playing:
            pygame.mixer.music.unpause()
            self.playing = True
            return "Music resumed"
        return "No paused music to resume"
    
    def stop(self) -> str:
        """Stop the currently playing track"""
        if self.current_track:
            pygame.mixer.music.stop()
            self.playing = False
            self.current_track = None
            return "Music stopped"
        return "No music is currently playing"
    
    def set_volume(self, volume: float) -> str:
        """Set the music volume (0.0 to 1.0)"""
        if 0.0 <= volume <= 1.0:
            pygame.mixer.music.set_volume(volume)
            self.volume = volume
            return f"Volume set to {int(volume * 100)}%"
        return "Volume must be between 0 and 1"

def get_random_quote() -> Dict[str, str]:
    """Get a random inspirational quote"""
    try:
        response = requests.get("https://api.quotable.io/random")
        data = response.json()
        return {
            "content": data.get("content", "No quote available"),
            "author": data.get("author", "Unknown")
        }
    except Exception as e:
        return {"content": f"Error getting quote: {str(e)}", "author": "Error"}

def get_riddle() -> Dict[str, str]:
    """Get a random riddle"""
    riddles = [
        {"question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", 
         "answer": "An echo"},
        {"question": "What has keys but no locks, space but no room, and you can enter but not go in?", 
         "answer": "A keyboard"},
        {"question": "What gets wetter as it dries?", 
         "answer": "A towel"},
        {"question": "The more you take, the more you leave behind. What am I?", 
         "answer": "Footsteps"},
        {"question": "What has a head, a tail, is brown, and has no legs?", 
         "answer": "A penny"},
        {"question": "What comes once in a minute, twice in a moment, but never in a thousand years?", 
         "answer": "The letter 'M'"},
        {"question": "I'm light as a feather, yet the strongest person can't hold me for more than a few minutes. What am I?", 
         "answer": "Breath"},
        {"question": "What can travel around the world while staying in a corner?", 
         "answer": "A stamp"},
        {"question": "What has 13 hearts but no other organs?", 
         "answer": "A deck of cards"},
        {"question": "What gets bigger when more is taken away?", 
         "answer": "A hole"}
    ]
    return random.choice(riddles)

def play_number_guessing_game() -> Dict[str, Any]:
    """Initialize a number guessing game"""
    number = random.randint(1, 100)
    return {
        "number": number,
        "attempts": 0,
        "max_attempts": 10,
        "game_over": False,
        "message": "I'm thinking of a number between 1 and 100. Can you guess it?"
    }

def check_number_guess(game_state: Dict[str, Any], guess: int) -> Dict[str, Any]:
    """Process a guess in the number guessing game"""
    if game_state.get("game_over", True):
        return game_state
    
    game_state["attempts"] += 1
    
    if game_state["attempts"] >= game_state["max_attempts"]:
        game_state["game_over"] = True
        game_state["message"] = f"Sorry, you've used all your attempts. The number was {game_state['number']}."
        return game_state
    
    if guess < game_state["number"]:
        game_state["message"] = f"Too low! You have {game_state['max_attempts'] - game_state['attempts']} attempts left."
    elif guess > game_state["number"]:
        game_state["message"] = f"Too high! You have {game_state['max_attempts'] - game_state['attempts']} attempts left."
    else:
        game_state["game_over"] = True
        game_state["message"] = f"Congratulations! You guessed the number {game_state['number']} in {game_state['attempts']} attempts!"
    
    return game_state

def tell_joke() -> Dict[str, str]:
    """Tell a random joke"""
    jokes = [
        {"setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything!"},
        {"setup": "Did you hear about the mathematician who's afraid of negative numbers?", "punchline": "He'll stop at nothing to avoid them!"},
        {"setup": "Why was the math book sad?", "punchline": "Because it had too many problems!"},
        {"setup": "What do you call a parade of rabbits hopping backwards?", "punchline": "A receding hare-line!"},
        {"setup": "Why don't we tell secrets on a farm?", "punchline": "Because the potatoes have eyes and the corn has ears!"},
        {"setup": "What's orange and sounds like a parrot?", "punchline": "A carrot!"},
        {"setup": "How do you organize a space party?", "punchline": "You planet!"},
        {"setup": "Why did the scarecrow win an award?", "punchline": "Because he was outstanding in his field!"},
        {"setup": "What do you call a fake noodle?", "punchline": "An impasta!"},
        {"setup": "What do you call a belt made of watches?", "punchline": "A waist of time!"}
    ]
    return random.choice(jokes)

def play_rock_paper_scissors(player_choice: str) -> Dict[str, str]:
    """Play rock, paper, scissors game"""
    choices = ["rock", "paper", "scissors"]
    player_choice = player_choice.lower()
    
    if player_choice not in choices:
        return {"result": "invalid", "message": "Invalid choice. Please choose rock, paper, or scissors."}
    
    computer_choice = random.choice(choices)
    
    result = {
        "player": player_choice,
        "computer": computer_choice
    }
    
    if player_choice == computer_choice:
        result["result"] = "tie"
        result["message"] = f"It's a tie! Both chose {player_choice}."
    elif (player_choice == "rock" and computer_choice == "scissors") or \
         (player_choice == "paper" and computer_choice == "rock") or \
         (player_choice == "scissors" and computer_choice == "paper"):
        result["result"] = "win"
        result["message"] = f"You win! {player_choice.capitalize()} beats {computer_choice}."
    else:
        result["result"] = "lose"
        result["message"] = f"You lose! {computer_choice.capitalize()} beats {player_choice}."
    
    return result 