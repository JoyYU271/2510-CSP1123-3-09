import json
import os


SAVE_PATH = "save_data.json"

import json
import os

SAVE_PATH = "save_data.json"

def save_checkpoint(npc_name, chapter, step, player_choices, flags=None, shown_dialogues=None):
    npc_state = {}

    if os.path.exists(SAVE_PATH) and os.path.getsize(SAVE_PATH) > 0:
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                npc_state = old_data.get("npc_state", {})
        except json.JSONDecodeError:
            npc_state = {}

    npc_state[npc_name] = {
        "chapter": chapter,
        "step": step
    }

    save_data = {
        "npc_state": npc_state,
        "player_choices": player_choices,
        "flags": flags or {},
        "shown_dialogues": shown_dialogues or {}
    }

    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(save_data, f, indent=4)



def load_checkpoint():
    if not os.path.exists(SAVE_PATH):
        return None
    if os.path.getsize(SAVE_PATH) == 0:  # if is empty
        return None
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("WARNING: Save file is corrupted or not valid JSON.")
        return None