import json
import os
from datetime import datetime

class SaveManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def get_save_files(self):
        """Return list of available save files"""
        saves = []
        for file in os.listdir(self.save_dir):
            if file.endswith(".sav"):
                saves.append(file)
        return saves
    
    def create_save_data(self, game_state):
        """Create a save data dictionary from current game state"""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_chapter": game_state.get("current_chapter", "chapter_1"),
            "player_position": game_state.get("player_position", (100, 520)),
            "shown_dialogues": game_state.get("shown_dialogues", {}),
            "player_choices": game_state.get("player_choices", {}),
            "settings": game_state.get("settings", {
                "bgm_vol": 0.5,
                "sfx_vol": 0.5,
                "text_size": "Medium",
                "language": "EN"
            })
        }
    
    def save_game(self, game_state, slot=0):
        """Save game to specified slot"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.sav")
        save_data = self.create_save_data(game_state)
        
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=4)
        
        return True
    
    def load_game(self, slot=0):
        """Load game from specified slot"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.sav")
        
        if not os.path.exists(save_path):
            return None
            
        with open(save_path, 'r') as f:
            save_data = json.load(f)
        
        return save_data
    
    def delete_save(self, slot=0):
        """Delete specified save file"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.sav")
        if os.path.exists(save_path):
            os.remove(save_path)
            return True
        return False