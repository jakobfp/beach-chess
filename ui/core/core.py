import os
from collections import namedtuple
import numpy as np

BLOCK_CHANCE = {"match": 75, "direction_match": 25}
ATTACK_DEFENSE_MATCH_CHANCE = {0: 90, 1: 55}
GENERAL_ATTACK_MISTAKE_CHANCE = 5

SINGLE_PLAYER_MODE = "single-player"
MULTI_PLAYER_MODE = "mutli-player"

DEFENSE_MADE_TEXT_LOOKUP = {
    90: "[attack] easily defended by [d]",
    75: "MONSTERBLOCK",
    55: "[d] is too fast, [attack] spectaculary defended",
    25: "[d] reaches far over the net and blocks [attack]",
    5: "what on earth, [a] puts [attack] in out"
}

SUCCESSFUL_ATTACK_TEXT_LOOKUP = {
    5: "[a] placed [attack] in empty space",
    25: "beautiful [attack] from [a]",
    55: "[a] with a fast [attack], too fast for [d]",
    75: "[a] uses the [block] block from [d]",
    90: "[a] puts [attack] right on the line"
}

Attack = namedtuple('Attack', ['index', 'name'])
Defense = namedtuple('Defense', ['index', 'name'])
Block = namedtuple('Block', ['index', 'name'])

class ATTACKS:
    CUT = Attack(0, "cut")
    DIA_HIT = Attack(1, "dia hit")
    DIA_SHOT = Attack(2, "dia shot")
    LINE_HIT = Attack(3, "line hit")
    LINE_SHOT = Attack(4, "line shot")
    SHORT_POKE = Attack(5, "spob")
    ATTACK_LIST = [CUT, DIA_HIT, DIA_SHOT, LINE_HIT, LINE_SHOT, SHORT_POKE]
    ATTACK_DICT = {0: CUT, 1: DIA_HIT, 2: DIA_SHOT, 3: LINE_HIT, 4: LINE_SHOT, 5: SHORT_POKE}

class BLOCKS:
    DIA = Block(0, "dia")
    LINE = Block(1, "line")
    BLOCK_LIST = [DIA, LINE]
    BLOCK_DICT = {0: DIA, 1: LINE}

class DEFENSES:
    CUT = Defense(0, "cut")
    DIA_HIT = Defense(1, "dia hit")
    DIA_SHOT = Defense(2, "dia shot")
    LINE_HIT = Defense(3, "line hit")
    LINE_SHOT = Defense(4, "line shot")
    SHORT_POKE = Defense(5, "spob")
    DEFENSE_LIST = [CUT, DIA_HIT, DIA_SHOT, LINE_HIT, LINE_SHOT, SHORT_POKE]
    DEFENSE_DICT = {0: CUT, 1: DIA_HIT, 2: DIA_SHOT, 3: LINE_HIT, 4: LINE_SHOT, 5: SHORT_POKE}

class Font:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def action_list_to_string(l):
    s = ''
    for action in l:
        s += f"{action.name}: {action.index}, "
    return s[:-2]

def print_commentary(comment, attack, block, defense, attacker_name, defender_name):
    comment = comment.replace('[attack]', attack.name)
    comment = comment.replace('[block]', block.name)
    comment = comment.replace('[a]', attacker_name)
    comment = comment.replace('[d]', defender_name)
    return comment

def ask_input_until_plausible(prompt, plausible):
    value = plausible + 1
    while value > plausible:
        try:
            value = int(input(prompt))
        except ValueError:
            print(f"Enter one of {list(range(0, plausible))}")
    return value

class Player:
    def __init__(self, name):
        self.name = name
        self.attack = Attack(-1, "")
        self.block = Block(-1, "")
        self.defense1 = Defense(-1, "")
        self.defense2 = Defense(-1, "")

    def get_name(self):
        return self.name

    def set_attack(self, attack: Attack):
        self.attack = attack

    def get_attack(self):
        return self.attack

    def set_block(self, block: Block):
        self.block = block

    def get_block(self):
        return self.block

    def set_defense1(self, defense: Defense):
        self.defense1 = defense

    def set_defense2(self, defense: Defense):
        self.defense2 = defense

    def set_defense(self, defense1: Defense, defense2: Defense):
        self.set_defense1(defense1)
        self.set_defense2(defense2)

    def get_defense(self):
        return [self.defense1, self.defense2]

class Rally:
    def __init__(self, attacker: Player, defender: Player, lookup):
        self.attacker = attacker
        self.defender = defender
        self.lookup = lookup
        self.defense_chance = 0
        self.attack_score = 0
        self.stats = ""
        self.comment = ""

    def print_rally(self):
        print(f"{Font.BOLD}attack:{Font.END} {self.attacker.get_attack().name}\t {Font.BOLD}block:{Font.END} {self.defender.get_block().name}\t {Font.BOLD}defenses:{Font.END} {self.defender.get_defense()[0].name}, {self.defender.get_defense()[1].name}")
        self.stats = f"defence score: {self.defense_score:.2f}, attack score: {self.attack_score:.2f}"
        print(self.stats)
        if self.attack_score <= 5 and self.defense_score <= 5:
            comment = DEFENSE_MADE_TEXT_LOOKUP[5]
        elif self.attack_score <= self.defense_score:
            comment = DEFENSE_MADE_TEXT_LOOKUP[self.defense_chance]
        else:
            comment = SUCCESSFUL_ATTACK_TEXT_LOOKUP[self.defense_chance]
        return print_commentary(comment, self.attacker.get_attack(), self.defender.get_block(), self.defender.get_block(), self.attacker.get_name(), self.defender.get_name())

    def calc_outcome(self):
        defenses = self.defender.get_defense()
        block = self.defender.get_block()
        attack = self.attacker.get_attack()
        defense_chances = np.array([self.lookup[(attack.index, block.index, 0, defenses[0].index)], self.lookup[(attack.index, block.index, 1, defenses[1].index)]])
        self.defense_chance = np.max(defense_chances)
        self.defense_score = self.defense_chance * np.random.uniform(low=0.95, high=1.05, size=1)[0]
        self.attack_score = np.random.randint(0, 101) * np.random.uniform(low=0.95, high=1.05, size=1)[0]
        self.comment = self.print_rally()
        return (self.defender, self.attacker) if self.attack_score <= self.defense_score else (self.attacker, self.defender)

class Game:
    def __init__(self, player1: Player, player2: Player, lookup):
        self.players = [player1, player2]
        self.current_defender = None
        self.current_attacker = None
        self.score = {player1.name: 0, player2.name: 0}
        self.lookup = lookup
        self.current_comment = ""

    def coin_toss(self):
        coin = np.random.randint(0,2)
        self.current_defender = self.players[coin]
        self.current_attacker = self.players[abs(coin-1)]
        print(f"{self.players[coin].name} serves!")
        return f"{self.players[coin].name} serves!"

    def play_rally(self):
        rally = Rally(self.current_attacker, self.current_defender, self.lookup)
        self.current_defender, self.current_attacker = rally.calc_outcome()
        self.score[self.current_defender.name] += 1
        return (rally.comment, rally.stats)

    def update(self, action, t):
        if t == 'attack':
            self.current_attacker.set_attack(action)
        if t == 'block':
            self.current_defender.set_block(action)
        if t == 'defense1':
            self.current_defender.set_defense1(action)
        if t == 'defense2':
            self.current_defender.set_defense2(action)
            return self.play_rally()
        return ("", "")

    def choose_attack(self):
        chosen_attack = ask_input_until_plausible(f"{self.current_attacker.name}, choose an attack ({action_list_to_string(ATTACKS.ATTACK_LIST)}): ", len(ATTACKS.ATTACK_LIST))
        os.system('clear')
        self.current_attacker.set_attack(ATTACKS.ATTACK_DICT[chosen_attack])

    def choose_defense(self):
        chosen_block = ask_input_until_plausible(f"{self.current_defender.name}, choose a block ({action_list_to_string(BLOCKS.BLOCK_LIST)}): ", len(BLOCKS.BLOCK_LIST))
        chosen_defense1 = ask_input_until_plausible(f"{self.current_defender.name}, choose the first defense ({action_list_to_string(DEFENSES.DEFENSE_LIST)}): ", len(DEFENSES.DEFENSE_LIST))
        chosen_defense2 = ask_input_until_plausible(f"{self.current_defender.name}, choose the second defense ({action_list_to_string(DEFENSES.DEFENSE_LIST)}): ", len(DEFENSES.DEFENSE_LIST))
        os.system('clear')
        self.current_defender.set_defense(DEFENSES.DEFENSE_DICT[chosen_defense1], DEFENSES.DEFENSE_DICT[chosen_defense2])
        self.current_defender.set_block(BLOCKS.BLOCK_DICT[chosen_block])

    def game_finished(self):
        points = list(self.score.values())
        if points[0] < 21 and points[1] < 21:
            return False
        if abs(points[0] - points[1]) < 2:
            return False
        return True

    def play(self):
        os.system('clear')
        self.choose_attack()
        self.choose_defense()
        self.play_rally()
        print(f"{Font.GREEN}{self.score}{Font.END}")
        input("Next rally...")

def create_defense_lookup_table():
    attack = np.arange(0, len(ATTACKS.ATTACK_LIST)+1, 1)
    block = np.arange(0, len(BLOCKS.BLOCK_LIST)+1, 1)
    defence_choice = np.arange(0, 2, 1)
    defense = np.arange(0, len(DEFENSES.DEFENSE_LIST)+1, 1)

    mesh = np.array(np.meshgrid(attack, block, defence_choice, defense))
    combinations = mesh.T.reshape(-1, 4)
    lookup = {}
    for comb in combinations:
        if comb[0] == comb[3]:
            lookup[tuple(comb.tolist())] = ATTACK_DEFENSE_MATCH_CHANCE[comb[2]]
        elif comb[0] == 0 and comb[1] == 0: # cut vs dia block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        elif comb[0] == 1 and comb[1] == 0: # dia hit vs dia block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["match"]
        elif comb[0] == 2 and comb[1] == 0: # dia shot vs dia block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        elif comb[0] == 3 and comb[1] == 1: # line hit vs line block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["match"]
        elif comb[0] == 4 and comb[1] == 1: # line shot vs line block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        elif comb[0] == 5 and comb[1] == 1: # spob vs line block
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        else:
            lookup[tuple(comb.tolist())] = GENERAL_ATTACK_MISTAKE_CHANCE

    return lookup
