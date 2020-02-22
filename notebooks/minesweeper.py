import random
import numpy as np
import pandas as pd

##########################
#### HELPER FUNCTIONS ####
##########################

def random_tuple(tuple_size):
    """Return a pair of random integers og a given size"""
    return np.random.randint(0,tuple_size[0]),np.random.randint(0,tuple_size[1])

def get_chunks(master_list, chunk_size):
    """Yield successive chunk_size-sized lists from master_list."""
    return [master_list[element:element + chunk_size]
            for element in range(0,len(master_list), chunk_size)]

def gen_deck(board_size,num_suits,deck_size):
    """Creates the deck. Returns a uniform number of cards for each suit"""

    num_cells = board_size[0]*board_size[1]
    alphabet = [chr(x).upper() for x in range(ord('a'), ord('z') + 1)]
    deck_size = max(deck_size,num_cells)

    # ensures that the number of suits are of equal sizes in the deck
    while deck_size % num_suits != 0:
        deck_size = deck_size - 1
    suit_size = int(deck_size/num_suits)

    # creates + shuffles the deck
    #deck = [[alphabet[num]]*int(suit_size) for num in range(num_suits)]
    deck = [card for num in range(num_suits)
                 for card in [alphabet[num]]*int(suit_size)]
    np.random.shuffle(deck)

    return deck

def gen_board(board_size,deck):
    """Creates the game boards.
       It generates the following  :
        - an empty game board (where cards will be flipped)
        - creates a Eboard with the suits to be revealed
        - separates the cards in the game board, and those remaining in the deck
    """

    # shapes the board in the appropriate dimensions
    ### THERE LOOKS LIKE THERE IS A BUG HERE ###
    num_cells = board_size[0]*board_size[1]
    board = get_chunks(deck[:num_cells], board_size[1])

    # create a board filled with empty strings, these will be flipped to reveal cards
    # empty_board = np.ones(board_size,dtype=bool)
    empty_board = np.array(get_chunks(['' for x in range(num_cells)], board_size[1]))

    # separates the deck into cards that are currently on the boar and cards that are not
    on_board = deck[:num_cells]
    off_board = deck[num_cells:]

    return empty_board, np.array(board), on_board, off_board

def create_game(board_size=(4,4),num_suits=4,deck_size=52):
    """Creates the game. Returns the game boards and deck"""

    deck  = gen_deck(board_size,num_suits,deck_size)
    empty_board, board, on_board, off_board = gen_board(board_size,deck)

    return deck, empty_board, np.array(board), on_board, off_board


def flip_random_card(board_size,empty_board,game_board):
    """Select a RANDOM card from the board to flip over.
        If all cards are flipped, the game is over"""
    flip_board = empty_board.copy()

    # if all cards are flipped (i.e., if no cards are an empty string), the game is over
    if ~np.all(flip_board != ''):
        # randomly search for a location to flip a card
        # while condition ensures that only face down cards will be selected to be flipped
        cell_location = random_tuple(board_size)
        while flip_board[cell_location] != '':
            cell_location = random_tuple(board_size)

        flip_board[cell_location] = board[cell_location]
    else:
        print('Conratulations! You won the game!')

    return cell_location, flip_board

def parse_cell(game_board,cell_location):
    """Checks the values of the cells adjacent to the cell_location
       Returns the adjacent values in a list
    """

    # extract row + column indices from location of flipped cards
    row, column = cell_location

    adj_vals = []

    # check the cards one index away from the flipped card (in the horizontal and vertical directions)

    try:
        adj_vals.append(game_board[row-1,column])
    except: pass

    try:
        adj_vals.append(game_board[row+1,column])
    except: pass

    try:
        adj_vals.append(game_board[row,column-1])
    except: pass

    try:
        adj_vals.append(game_board[row,column+1])
    except: pass

    return adj_vals

def check_match(game_board,cell_location):
    """ Check a cell to see if there is either a horizonal or vertical match
        for a given card flip.
        Returns a boolean
    """
    # extract row + column indices from location of flipped cards
    row, column = cell_location

    # checks the cards adjacent to the input cell
    adj_vals = parse_cell(game_board,cell_location)

    # if any card matches the flipped card, return false
    match_val = np.any(adj_vals == np.array(game_board[row,column]))

    return match_val

def get_match_prob(game_board):
    """Calculates the probability of a match for
       EACH unflipped cell.

       This is used to decide which card to flip next
    """
    max_row, max_column = board_size

    # get the location of each possible card, keep only those that ARE NOT flipped
    perms = [(row,col) for row in range(max_row) for col in range(max_column)]
    open_slots = [perm for perm in perms if empty_board[perm] == '']

    # for open slot, check the prob. of a suit match, append value to list
    match_prob_list = []
    for loc in open_slots:
        adj_vals = parse_cell(empty_board,loc)
        adj_suits = list(set([v for v in adj_vals if v != '']))
        match_prob = len(adj_suits)/len(adj_vals)

        match_prob_list.append(match_prob)

    # find the lowest prob. of a match
    min_prob = min(match_prob_list)

    # return ALL slots with lowest prob. of a match
    bools = np.array(match_prob_list) == min_prob
    min_locs = np.array(open_slots)[bools]

    # RANDOMLY return the coords of a single lowest prob. slot to flip
    return tuple(random.choice(min_locs))

def flip_best_odds(empty_board,loc_to_flip):
    """Select a card from the board to flip over.
        If all cards are flipped, the game is over"""
    flip_board = empty_board.copy()

    # if all cards are flipped (i.e., if no cards are an empty string), the game is over
    if ~np.all(flip_board != ''):
        # randomly search for a location to flip a card
        # while condition ensures that only face down cards will be selected to be flipped
        flip_board[loc_to_flip] = board[loc_to_flip]
    else:
        print('Conratulations! You won the game!')

    return flip_board
