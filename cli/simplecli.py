import os
import numpy as np


ATTACK_DICT = {
    0: "cut",
    1: "dia hit",
    2: "dia shot",
    3: "line hit",
    4: "line shot"
}

BLOCK_DICT = {
    0: "dia",
    1: "line"
}

DEFENSE_DICT = {
    0: "cut",
    1: "dia hit",
    2: "dia shot",
    3: "line hit",
    4: "line shot"
}

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

class font:
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


def create_defense_lookup_table():
    attack = np.arange(0, 8, 1)
    block = np.arange(0, 3, 1)
    defence_choice = np.arange(0, 2, 1)
    defense = np.arange(0, 8, 1)

    mesh = np.array(np.meshgrid(attack, block, defence_choice, defense))
    combinations = mesh.T.reshape(-1, 4)
    lookup = {}
    for comb in combinations:
        if comb[0] == comb[3]:
            lookup[tuple(comb.tolist())] = ATTACK_DEFENSE_MATCH_CHANCE[comb[2]]
        elif (comb[0] == 0 or comb[0] == 2) and comb[1] == 0:
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        elif comb[0] == 1 and comb[1] == 0:
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["match"]
        elif comb[0] == 3 and comb[1] == 1:
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["match"]
        elif comb[0] == 4 and comb[1] == 1:
            lookup[tuple(comb.tolist())] = BLOCK_CHANCE["direction_match"]
        else:
            lookup[tuple(comb.tolist())] = GENERAL_ATTACK_MISTAKE_CHANCE

    return lookup

def print_commentary(comment, attack, block, defense, attacker, defender):
    comment = comment.replace('[attack]', ATTACK_DICT[attack])
    comment = comment.replace('[block]', BLOCK_DICT[block])
    comment = comment.replace('[a]', attacker)
    comment = comment.replace('[d]', defender)
    print(f"{font.YELLOW}{comment}{font.END}")

def print_rally(attack, block, defense, defence_chance, attack_score, attacker, defender):
    print(f"{font.BOLD}attack:{font.END} {ATTACK_DICT[attack]}\t {font.BOLD}block:{font.END} {BLOCK_DICT[block]}\t {font.BOLD}defense:{font.END} {DEFENSE_DICT[defense]}")
    print(f"defence chance: {defence_chance}, attack score: {attack_score}")
    if attack_score <= 5 and defence_chance == 5:
        print_commentary(DEFENSE_MADE_TEXT_LOOKUP[5], attack, block, defense, attacker, defender)
    elif attack_score <= defence_chance:
        print_commentary(DEFENSE_MADE_TEXT_LOOKUP[defence_chance], attack, block, defense, attacker, defender)
    else:
        print_commentary(SUCCESSFUL_ATTACK_TEXT_LOOKUP[defence_chance], attack, block, defense, attacker, defender)


def ask_input_until_plausible(prompt, plausible):
    value = plausible + 1
    while value > plausible:
        try:
            value = int(input(prompt))
        except ValueError:
            pass
    return value

def attack_input(player):
    attack = ask_input_until_plausible(f"{player}, choose an attack ({ATTACK_DICT}): ", max(ATTACK_DICT.keys()))
    os.system('clear')
    return attack

def block_input(player):
    block = ask_input_until_plausible(f"{player}, choose a block ({BLOCK_DICT}): ", max(BLOCK_DICT.keys()))
    os.system('clear')
    return block

def defense_input(player):
    first_defense = ask_input_until_plausible(f"{player}, choose the first defense ({DEFENSE_DICT}): ", max(DEFENSE_DICT.keys()))
    second_defense = ask_input_until_plausible(f"{player}, choose the second defense ({DEFENSE_DICT}): ", max(DEFENSE_DICT.keys()))
    os.system('clear')
    return np.array([first_defense, second_defense])

def calculate_point(lookup, attack_player, defense_player, attack, block, defenses):
    defense_chances = np.array([lookup[(attack, block, 0, defenses[0])], lookup[(attack, block, 1, defenses[1])]])
    defense_chance_max_idx = np.argmax(defense_chances)
    defense_chance = np.max(defense_chances)
    attack_score = np.random.randint(0, 101)
    print_rally(attack, block, defenses[defense_chance_max_idx], defense_chance, attack_score, attack_player, defense_player)
    return (defense_player, attack_player) if attack_score <= defense_chance else (attack_player, defense_player)

def game_finished(points):
    if points[0] < 21 and points[1] < 21:
        return False
    if abs(points[0] - points[1]) < 2:
        return False
    return True

def multi_player(lookup):
    os.system('clear')
    player1 = input("Player 1 Name: ")
    player2 = input("Player 2 Name: ")
    assert player1 != player2, "Enter two different names, please!"
    players = [player1, player2]
    points_dict = {}
    points_dict[player1] = 0
    points_dict[player2] = 0
    # set start player
    who_starts = ask_input_until_plausible(f"Who will serve? [0:{players[0]}/1:{players[1]}] ", 1)
    os.system('clear')
    defense_player = players[who_starts]
    attack_player = players[0] if who_starts == 1 else players[1]
    # until 21
    while not game_finished(list(points_dict.values())):
        os.system('clear')
        print(f"{defense_player} serves!")
        attack = attack_input(attack_player)
        block = block_input(defense_player)
        defenses = defense_input(defense_player)
        (defense_player, attack_player) = calculate_point(lookup, attack_player, defense_player, attack, block, defenses)
        points_dict[defense_player] += 1
        print(f"score: {font.GREEN}{points_dict}{font.END}")
        _ = input("Next rally...")

    os.system('clear')
    print(f"{defense_player} has beaten {attack_player} {points_dict[defense_player]} : {points_dict[attack_player]}!")
    print(f"Endscore: {font.PURPLE}{points_dict}{font.END}")

def play(mode):
    lookup = create_defense_lookup_table()
    if mode == SINGLE_PLAYER_MODE:
        pass
    else:
        multi_player(lookup)


if __name__ == '__main__':
    try:
        play(MULTI_PLAYER_MODE)
    except KeyboardInterrupt:
        print(f"\n{font.RED}ABORTED")
