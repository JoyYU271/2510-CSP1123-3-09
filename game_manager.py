# game_manager.py
import pygame
from main_page import main_menu
from Intro1 import SimpleChapterIntro, GameStateManager
from Dialogue1 import run_dialogue
import sys

class GameManager:
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Mindscape Chamber")
        self.clock = pygame.time.Clock()
        self.current_scene = "main_menu"  # 明确初始场景
        self.bgm_vol = 0.5
        self.sfx_vol = 0.5
        self.font_size = 30
        self.language = "EN"
        
    def run(self):
        while True:
            if self.current_scene == "main_menu":
                # 直接调用main_menu并传递self作为game_manager
                self.run_main_menu()
            elif self.current_scene == "intro":
                self.run_intro()
            elif self.current_scene == "dialogue":
                self.run_dialogue()
            else:
                self.current_scene = "main_menu"
    
    def run_main_menu(self):
        # 专门处理主菜单场景
        result = main_menu(self)  # 传递game_manager实例
        if result == "intro":
            self.current_scene = "intro"
        else:
            self.current_scene = "main_menu"
    
    def run_intro(self):
        game_state_manager = GameStateManager('intro')
        intro = SimpleChapterIntro(self.screen, game_state_manager)
        intro.start("chapter_1")
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            keys = pygame.key.get_pressed()
            if not intro.update(keys):
                running = False
            
            intro.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
        
        self.current_scene = "dialogue"
    
    def run_dialogue(self):
        run_dialogue(self.font_size, self.language, self.bgm_vol, self.sfx_vol)
        self.current_scene = "main_menu"  # 对话结束后返回主菜单

if __name__ == "__main__":
    game = GameManager()
    game.run()