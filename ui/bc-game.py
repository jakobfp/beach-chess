import pygame

import core

from pygame.locals import (
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_RETURN,
    K_SPACE,
    KEYDOWN,
    QUIT,
)

number_keys = [
    K_1,
    K_2,
    K_3,
    K_4,
    K_5,
    K_6,
]

pygame.init()

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
BLUE = pygame.Color(0, 0, 128)
MIK_YELLOW = pygame.Color(250, 203, 3)
MIK_BLUE = pygame.Color(22, 45, 142)
MIK_GOLD = pygame.Color(161, 135, 115)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class InputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, text=''):
        super(InputBox, self).__init__()
        self.show = False
        self.color = MIK_GOLD
        self.text = text
        self.W = w
        self.H = h
        self.X = x
        self.Y = y
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.font = pygame.font.SysFont("Helvetica", 20, bold=False)
        self.text_surf = self.font.render(text, True, self.color)
        self.rect = self.surf.get_rect(
            center=(
                self.X+self.W/2,
                self.Y+self.H/2
            )
        )
        self.active = False

    def toggle(self):
        self.show = not self.show

    def reset_surface(self):
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                self.X+self.W/2,
                self.Y+self.H/2
            )
        )

    def get_text(self):
        return self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = MIK_YELLOW if self.active else MIK_GOLD
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == K_RETURN:
                    self.text = self.text
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.text_surf = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        self.reset_surface()
        width = max(200, self.text_surf.get_width()+10)
        self.rect.w = width
        self.surf.blit(self.text_surf, [self.W/2-self.text_surf.get_width()/2, self.H/2-self.text_surf.get_height()/2])

class ActionSprite(pygame.sprite.Sprite):
    def __init__(self, text, idx):
        super(ActionSprite, self).__init__()
        self.idx = idx
        self.font = pygame.font.SysFont("Helvetica", 20, bold=False)
        self.text_surf = self.font.render(f"{text} ({idx+1})", 1, WHITE)
        self.W = 600
        self.H = 70
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH/2,
                150+self.idx*self.H+self.idx*5
            )
        )
        self.surf.blit(self.text_surf, [self.W/2-self.text_surf.get_width()/2, self.H/2-self.text_surf.get_height()/2])

class ChooseSprite(pygame.sprite.Sprite):
    def __init__(self, action_list, name):
        super(ChooseSprite, self).__init__()
        self.font = pygame.font.SysFont("Helvetica", 20, bold=False)
        self.name = name
        self.text_surf = self.font.render(f"Choose {name}, confirm with Enter.", 1, BLACK)
        self.action_sprites = pygame.sprite.Group()
        for idx, action in enumerate(action_list):
            self.action_sprites.add(ActionSprite(action.name, action.index))
        self.surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.surf.fill((MIK_YELLOW))
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH/2,
                SCREEN_HEIGHT/2
            )
        )
        self.surf.blit(self.text_surf, [100, 50])
        self.keys_to_handle = [number_keys[i] for i, _ in enumerate(self.action_sprites)]
        self.action_list = action_list
        self.reset()

    def reset(self):
        self.done = False
        self.action = None

    def handle_event(self, event):
        if event.type == KEYDOWN:
            if event.key in self.keys_to_handle:
                try:
                    self.done = True
                    self.action = self.action_list[int(event.unicode)-1]
                except ValueError:
                    print(f"not a valid action: {event.unicode}")


    def update(self, r, s):
        for action in self.action_sprites:
            self.surf.blit(action.surf, action.rect)

class ResultSprite(pygame.sprite.Sprite):
    def __init__(self):
        super(ResultSprite, self).__init__()
        self.name = "result"
        self.font = pygame.font.SysFont("Helvetica", 25, bold=False)
        self.font_stats = pygame.font.SysFont("Helvetica", 15, bold=False)
        self.text_surf_result = self.font.render(f"", 1, MIK_YELLOW)
        self.text_surf_stats = self.font_stats.render(f"", 1, MIK_GOLD)
        self.W = SCREEN_WIDTH
        self.H = SCREEN_HEIGHT
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH/2,
                SCREEN_HEIGHT/2
            )
        )
        self.action = None
        self.done = True
        self.reset()

    def reset(self):
        self.done = True
        self.action = None

    def reset_surface(self):
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH/2,
                SCREEN_HEIGHT/2
            )
        )

    def handle_event(self, event):
        pass

    def blit_result(self):
        self.surf.blit(self.text_surf_result, [self.W/2-self.text_surf_result.get_width()/2, self.H/2-self.text_surf_result.get_height()/2])
        self.surf.blit(self.text_surf_stats, [self.W/2-self.text_surf_stats.get_width()/2, self.H/3-self.text_surf_stats.get_height()/2])

    def update(self, result_text, stats_text):
        self.reset_surface()
        self.text_surf_result = self.font.render(f"{result_text}", True, MIK_YELLOW)
        self.text_surf_stats = self.font_stats.render(f"{stats_text}", True, MIK_GOLD)
        self.blit_result()

class ScoreSprite(pygame.sprite.Sprite):
    def __init__(self):
        super(ScoreSprite, self).__init__()
        self.font = pygame.font.SysFont("Helvetica", 20, bold=False)
        self.text_surf_player1 = self.font.render(f"player: 0", 1, WHITE)
        self.text_surf_player2 = self.font.render(f"player: 0", 1, WHITE)
        self.W = 140
        self.H = 80
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH-170,
                50
            )
        )
        self.blit_score_board((10, self.text_surf_player1.get_height()))

    def blit_score_board(self, circle_pos):
        pygame.draw.circle(self.surf, WHITE, circle_pos, 2)
        self.surf.blit(self.text_surf_player1, [20, self.text_surf_player1.get_height()/2])
        self.surf.blit(self.text_surf_player2, [20, self.H-self.text_surf_player2.get_height() * 1.5])

    def reset_surface(self):
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.fill(MIK_BLUE)
        self.rect = self.surf.get_rect(
            center=(
                SCREEN_WIDTH-170,
                50
            )
        )

    def render_score(self, score, defender, attacker):
        p_names = list([attacker, defender])
        p_names.sort()
        if p_names[0] == attacker:
            circle_pos = (10, self.text_surf_player1.get_height())
        else:
            circle_pos = (10, self.H-self.text_surf_player2.get_height())
        self.text_surf_player1 = self.font.render(f"{p_names[0]}: {score[p_names[0]]}", 1, WHITE)
        self.text_surf_player2 = self.font.render(f"{p_names[1]}: {score[p_names[1]]}", 1, WHITE)
        return circle_pos

    def update(self, score, defender, attacker):
        self.reset_surface()
        circle_pos = self.render_score(score, defender, attacker)
        self.blit_score_board(circle_pos)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

player1_input = InputBox(200, 100, 150, 20, '')
player2_input = InputBox(200, 200, 150, 20, '')

welcome_screen = pygame.sprite.Group()
welcome_screen.add(player1_input)
welcome_screen.add(player2_input)

clock = pygame.time.Clock()

# choose names
running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                running = False
        screen.fill(MIK_YELLOW)
        for box in welcome_screen:
            box.handle_event(event)
            box.update()
            screen.blit(box.surf, box.rect)
        pygame.display.flip()

outcome_lookup = core.create_defense_lookup_table()
player_names = [player1_input.get_text(), player2_input.get_text()]
print(player_names)
player1 = core.Player(player_names[0])
player2 = core.Player(player_names[1])
game_state = core.Game(player1, player2, outcome_lookup)
game_state.coin_toss()

attack_choose = ChooseSprite(core.ATTACKS.ATTACK_LIST, "attack")
block_choose = ChooseSprite(core.BLOCKS.BLOCK_LIST, "block")
defense1_choose = ChooseSprite(core.DEFENSES.DEFENSE_LIST, "defense1")
defense2_choose = ChooseSprite(core.DEFENSES.DEFENSE_LIST, "defense2")

score_sprite = ScoreSprite()
result_sprite = ResultSprite()

screens = [attack_choose, block_choose, defense1_choose, defense2_choose, result_sprite]
active_idx = 0
active_screen = screens[active_idx]

# play
stop = False
res = ""
stats = ""
while not stop:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                stop = True
            elif event.key == K_RETURN and active_screen.done:
                res, stats = game_state.update(active_screen.action, active_screen.name)
                active_screen.reset()
                active_idx = (active_idx+1)%len(screens)
                active_screen = screens[active_idx]
        elif event.type == QUIT:
            stop = True
        score_sprite.update(game_state.score, game_state.current_defender.get_name(), game_state.current_attacker.get_name())
        active_screen.handle_event(event)
        active_screen.update(res, stats)
        if game_state.game_finished():
            stop = True
        screen.fill(MIK_YELLOW)
        screen.blit(active_screen.surf, active_screen.rect)
        screen.blit(score_sprite.surf, score_sprite.rect)
        pygame.display.flip()
