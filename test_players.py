from random import randint
import random

class Player():
    def __init__(self, name="Player"):
        self.name = name

    def move(self, game, time_left):
        pass

    def get_name(self):
        return self.name


class RandomPlayer(Player):
    """Player that chooses a move randomly."""
    def __init__(self, name="RandomPlayer"):
        super().__init__(name)

    def move(self, game, time_left):
        if not game.get_player_moves(self):
            return None
        else:
            return random.choice(game.get_player_moves(self))

    def get_name(self):
        return self.name


class HumanPlayer(Player):
    """
    Player that chooses a move according to user's input. 
    (Useful if you play in the terminal)
    """
    def __init__(self, name="HumanPlayer"):
        super().__init__(name)

    def move(self, game, time_left):
        legal_moves = game.get_player_moves(self)
        choice = {}

        if not len(legal_moves):
            print("No more moves left.")
            return None, None

        counter = 1
        for move in legal_moves:
            choice.update({counter: move})
            print('\t'.join(['[%d] (%d,%d)' % (counter, move[0], move[1])]))
            counter += 1

        print("-------------------------")
        print(game.print_board(legal_moves))
        print("-------------------------")
        print(">< - impossible, o - valid move")
        print("-------------------------")

        valid_choice = False

        while not valid_choice:
            try:
                index = int(input('Select move index [1-' + str(len(legal_moves)) + ']:'))
                valid_choice = 1 <= index <= len(legal_moves)

                if not valid_choice:
                    print('Illegal move of queen! Try again.')
            except Exception:
                print('Invalid entry! Try again.')

        return choice[index]

    def get_name(self):
        return self.name
