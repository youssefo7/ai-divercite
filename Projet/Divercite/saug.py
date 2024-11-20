from board_divercite import BoardDivercite
from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.game.game_layout.board import Piece

import random


class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game implementing Minimax with Alpha-Beta Pruning.
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece.
            name (str, optional): Name of the player.
        """
        super().__init__(piece_type, name)
        self.colors_used = []  # Use a list instead of a set to track colors.

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Compute the best action using either a predefined strategy or Minimax with Alpha-Beta Pruning.

        Args:
            current_state (GameState): The current game state.
            remaining_time (int): Remaining time for the player.

        Returns:
            Action: The chosen action.
        """
        step = current_state.get_step()

        # Otherwise, proceed with normal strategies
        if step < 7:
            return self.place_different_cities(current_state)
        else:
            max_depth = self.adaptive_depth(step)
            _, best_action = self.minimax(
                current_state=current_state,
                depth=max_depth,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing_player=True
            )
            return best_action


    def place_different_cities(self, current_state: GameState) -> Action:
        """
        Place cities of different colors on the board during the first 4 moves.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The chosen action.
        """
        possible_actions = list(current_state.generate_possible_heavy_actions())
        random.shuffle(possible_actions)

        for action in possible_actions:
            next_state = action.get_next_game_state()  # State after the action
            current_rep = current_state.get_rep().get_env()  # Current board representation
            next_rep = next_state.get_rep().get_env()  # Next board representation

            # Find the new piece added to the board
            new_pieces = {pos: piece for pos, piece in next_rep.items() if pos not in current_rep}
            if new_pieces:  # If a new piece is detected
                (pos, piece) = list(new_pieces.items())[0]  # Get the position and the piece
                piece_color = piece.get_type()[0]  # Assuming `get_type()` gives "Color+Type+Owner"
                piece_type = piece.get_type()[1]  # Assuming "C" means city

                if piece_color not in self.colors_used and piece_type == "C":
                    self.colors_used.append(piece_color)
                    return action

        # Fallback: If no valid action found, return any action
        return random.choice(possible_actions)


    def adaptive_depth(self, step: int) -> int:
        """
        Determine the depth of search adaptively based on the current step of the game.

        Args:
            step (int): Current step in the game.

        Returns:
            int: Depth of the search tree.
        """
        # Depth starts small early in the game, increases as the board fills.
        if step < 10:
            return 2
        elif step < 25:
            return 3
        elif step < 30:
            return 4
        elif step < 40:
            return 5
        else:
            return 2

    def minimax(self, current_state: GameStateDivercite, depth: int, alpha: float, beta: float, maximizing_player: bool):
        """
        Perform the minimax algorithm with alpha-beta pruning.

        Args:
            current_state (GameStateDivercite): Current game state.
            depth (int): Depth of the search tree.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            maximizing_player (bool): True if maximizing player, False if minimizing.

        Returns:
            tuple: (best_score, best_action)
        """
        # Base case: If depth is 0 or the game is finished
        if depth == 0 or current_state.is_done():
            return self.evaluate_state(current_state), None

        possible_actions = list(current_state.generate_possible_heavy_actions())
        if not possible_actions:  # If no valid actions, evaluate the state
            return self.evaluate_state(current_state), None

        best_action = None

        if maximizing_player:
            max_eval = float('-inf')
            for action in possible_actions:
                # Apply the action to get the resulting state
                next_state = action.get_next_game_state()

                # Recursively call minimax
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = action
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Prune the remaining branches
            return max_eval, best_action

        else:  # Minimizing player
            min_eval = float('inf')
            for action in possible_actions:
                # Apply the action to get the resulting state
                next_state = action.get_next_game_state()

                # Recursively call minimax
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_action = action
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Prune the remaining branches
            return min_eval, best_action

    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Evaluate a game state based on the player's score and heuristic.

        Args:
            state (GameStateDivercite): The state to evaluate.

        Returns:
            float: Heuristic score for the state.
        """
        my_id = self.get_id()
        my_score = state.scores[my_id]
        opponent_id = [p.get_id() for p in state.players if p.get_id() != my_id][0]
        opponent_score = state.scores[opponent_id]

        # Additional heuristic: Penalize exhausting resources and reward creating Divercités
        resource_penalty = sum(
            state.players_pieces_left[my_id][piece] for piece in state.players_pieces_left[my_id]
        )
        divercite_bonus = 0
        for i in range(state.get_rep().get_dimensions()[0]):
            for j in range(state.get_rep().get_dimensions()[1]):
                if state.in_board((i, j)) and state.get_rep().get_env().get((i, j)):
                    piece = state.get_rep().get_env()[(i, j)]
                    if piece.get_owner_id() == my_id and state.check_divercite((i, j)):
                        divercite_bonus += 5  # Example bonus for forming Divercités

        # Heuristic: Maximize my score and Divercités, minimize opponent's score, conserve resources
        return my_score - opponent_score + divercite_bonus - 2 * resource_penalty
