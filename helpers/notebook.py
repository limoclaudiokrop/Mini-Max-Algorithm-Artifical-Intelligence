def play(Q1, Q2, size=7, time_limit=6000, print_moves=True, seed=None):
    """
        Args:
            Q1: Player 1
            Q2: Player 2
            size: game board size
            time_limit: timeout threshold in milliseconds
            print_moves: Whether or not moves should be printed
            seed: seed for random library
        Returns:
            (str, [(int, int)], str): Name of Winner, Move history, Reason for game over.
                                      Each move in move history takes the form of (row, column).
    """
    import random
    from isolation import Board
    import multiprocessing
    lock = multiprocessing.Lock()
    
    if seed is not None:
        random.seed(seed)
    game = Board(Q1, Q2, size, size)
    # assign a random move to each player before playing
    for idx in range(2):
        moves = game.get_active_moves()
        random.shuffle(moves)
        move = moves[0]
        game, _, _ = game.forecast_move(move)
    winner, move_history, termination = game.play_isolation(time_limit=time_limit, print_moves=print_moves)
    lock.acquire()
    print("\n", winner, " has won. Reason: ", termination)
    lock.release()
    return winner, move_history, termination