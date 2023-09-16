# Board visualization with ipywidgets
import copy
from time import sleep
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import VBox, HBox, Label, Button, GridspecLayout
from ipywidgets import Button, GridBox, Layout, ButtonStyle
from IPython.display import display, clear_output

from isolation import Board
from test_players import Player

import time
import platform
# import io
from io import StringIO

# import resource
if platform.system() != 'Windows':
    import resource


def get_details(name):
    if name == 'Q1':
        color = 'SpringGreen'
    elif name == 'Q2':
        color = 'tomato'
    elif name == 'q1':
        color = 'HoneyDew'
        name = ' '
    elif name == 'q2':
        color = 'MistyRose'
        name = ' '
    elif name == 'X':
        color = 'black'
    elif name == 'O':
        color = 'orange'
        name = ' '
    else:
        color = 'Lavender'
    style = ButtonStyle(button_color=color)
    return name, style

def create_cell(button_name='', grid_loc=None, click_callback=None):
    layout = Layout(width='auto', height='auto')
    name, style = get_details(button_name)
    button = Button(description=name,layout = layout, style=style)
    button.x, button.y = grid_loc
    if click_callback: button.on_click(click_callback)
    return button

def get_viz_board_state(game, show_legal_moves):
    board_state = game.get_state()
    legal_moves = game.get_active_moves()
    active_player = 'q1' if game.__active_player__ is game.__player_1__ else 'q2'
    if show_legal_moves:
        for r,c in legal_moves: 
            if board_state[r][c][0] != 'Q':
                board_state[r][c] = active_player
    return board_state

def create_board_gridbox(game, show_legal_moves, click_callback=None):
    h, w = game.height, game.width
    board_state = get_viz_board_state(game, show_legal_moves)

    grid_layout = GridspecLayout(n_rows=h,
                                 n_columns=w,
                                 grid_gap='2px 2px',
                                 width='480px',
                                 height='480px',
                                 justify_content='center'
                                )
    for r in range(h):
        for c in range(w):
            cell = create_cell(board_state[r][c], grid_loc=(r,c), click_callback=click_callback)
            grid_layout[r,c] = cell

    return grid_layout

class InteractiveGame():
    """This class is used to play the game interactively (only works in jupyter)"""
    def __init__(self, opponent=None, show_legal_moves=False):
        self.game = Board(Player, opponent)
        self.width = self.game.width
        self.height = self.game.height
        self.show_legal_moves = show_legal_moves
        self.gridb = create_board_gridbox(self.game, 
                                          self.show_legal_moves, 
                                          click_callback=self.select_move)
        self.visualized_state = None
        self.opponent = opponent
        self.output_section = widgets.Output(layout={'border': '1px solid black'})
        self.game_is_over = False
        display(self.gridb)

    def select_move(self, b):
        if platform.system() == 'Windows':
            def curr_time_millis():
                return int(round(time.time() * 1000))
        else:
            def curr_time_millis():
                return 1000 * resource.getrusage(resource.RUSAGE_SELF).ru_utime
        move_start = curr_time_millis()
        
        def time_left(time_limit = 1000):
            # print("Limit: "+str(time_limit) +" - "+str(curr_time_millis()-move_start))
            return time_limit - (curr_time_millis() - move_start)

        if self.game_is_over:
            return print('The game is over!')
        ### swap move workaround ###
        # find if current location is in the legal moves
        # legal_moves is of length 1 if move exists, and len 0 if move is illegal
        legal_moves = [(x,y) for x,y in self.game.get_active_moves() if (x,y) == (b.x, b.y)]
        if not legal_moves:
            print(f"move {(b.x, b.y)} is illegal!")
            return
        else:
            # there is only one move in swap isolation game
            move = legal_moves[0] 
        ### swap move workaround end ###
        self.game_is_over, winner = self.game.__apply_move__(move)
        if (not self.game_is_over) and (self.opponent is not None):
            opponents_legal_moves = self.game.get_active_moves()
            opponent_move = self.opponent.move(self.game, time_left=time_left)
            assert opponent_move in opponents_legal_moves, \
            f"Opponents move {opponent_move} is not in list of legal moves {opponents_legal_moves}"
            self.game_is_over, winner = self.game.__apply_move__(opponent_move)
        if self.game_is_over: print(f"Game is over, the winner is: {winner}")
        board_vis_state = get_viz_board_state(self.game, self.show_legal_moves)
        for r in range(self.height):
            for c in range(self.width):
                new_name, new_style = get_details(board_vis_state[r][c])
                self.gridb[r,c].description = new_name
                self.gridb[r,c].style = new_style

class ReplayGame():
    """This class is used to replay games (only works in jupyter)"""
    def __init__(self, game, move_history, show_legal_moves=False):
        self.game = game
        self.width = self.game.width
        self.height = self.game.height
        self.move_history = move_history
        self.show_legal_moves = show_legal_moves
        self.board_history = []
        self.new_board = self.setup_new_board()
        self.gridb = create_board_gridbox(self.new_board, self.show_legal_moves)
        self.generate_board_state_history()
        self.visualized_state = None
        self.output_section = widgets.Output(layout={'border': '1px solid black'})
    
    def setup_new_board(self,):
        return Board(player_1=self.game.__player_1__, 
                     player_2=self.game.__player_2__,
                     width=self.width,
                     height=self.height)

    def update_board_gridbox(self, move_i):
        board_vis_state, board_state = self.board_history[move_i]
        self.visualized_state = board_state
        for r in range(self.height):
            for c in range(self.width):
                new_name, new_style = get_details(board_vis_state[r][c])
                self.gridb[r,c].description = new_name
                self.gridb[r,c].style = new_style

    def equal_board_states(self, state1, state2):
        for r in range(self.height):
            for c in range(self.width):
                if state1[r][c] != state2[r][c]:
                    return False
        return True

    def generate_board_state_history(self,):        
        for move_pair in self.move_history:
            for move in move_pair:
                self.new_board.__apply_move__(move)
                board_vis_state = get_viz_board_state(self.new_board, self.show_legal_moves)
                board_state = self.new_board.get_state()
                self.board_history.append((copy.deepcopy(board_vis_state), copy.deepcopy(board_state)))
        assert self.equal_board_states(self.game.get_state(), self.new_board.get_state()), \
        "End game state based of move history is not consistent with state of the 'game' object."
    
    def get_board_state(self, x):
        """You can use this state to with game.set_state() to replicate same Board instance."""
        self.output_section.clear_output()
        with self.output_section:
            display(self.visualized_state)
    
    def show_board(self):
        # Show slider for move selection
        input_move_i = widgets.IntText(layout = Layout(width='auto'))
        slider_move_i = widgets.IntSlider(description=r"\(move[i]\)",
                                          min=0,
                                          max=len(self.board_history)-1,
                                          continuous_update=False,
                                          layout = Layout(width='auto')
                                         )
        mylink = widgets.link((input_move_i, 'value'), (slider_move_i, 'value'))   
        slider = VBox([input_move_i,interactive(self.update_board_gridbox, move_i=slider_move_i)])
        
        get_state_button = Button(description='get board state')
        get_state_button.on_click(self.get_board_state)
        
        grid = GridspecLayout(4, 6)#, width='auto')
        #Left side
        grid[:3, :-3] = self.gridb
        grid[3, :-3] = slider

        #Right side
        grid[:-1, -3:] = self.output_section
        grid[-1, -3:] = get_state_button
        display(grid)
