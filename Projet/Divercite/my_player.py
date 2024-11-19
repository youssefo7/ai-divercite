from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.game.light_action import LightAction
from seahorse.game.game_layout.board import Piece

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game using minimax with alpha-beta pruning.
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer", depth_limit: int = 4):
        """
        Initialize the PlayerDivercite instance with alpha-beta depth control.

        Args:
            piece_type (str): Type of the player's game piece.
            name (str, optional): Name of the player.
            depth_limit (int, optional): Maximum depth for alpha-beta pruning.
        """
        super().__init__(piece_type, name)
        self.depth_limit = depth_limit

    def compute_action(self, current_state: GameStateDivercite, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Choose the best action based on minimax with alpha-beta pruning.

        Args:
            current_state (GameStateDivercite): The current game state.

        Returns:
            Action: The best action as determined by alpha-beta pruning.
        """
        best_action = None
        max_score = -float("inf")

        # Alpha and Beta initialized
        alpha = -float("inf")
        beta = float("inf")

        # Iterate over possible actions and apply minimax with alpha-beta pruning
        for action in current_state.generate_possible_light_actions():
            # Apply action to get a new game state
            new_state = current_state.apply_action(action)

            # Recursively call minimax on the new state, decreasing depth
            score = self.minimax(new_state, self.depth_limit - 1, alpha, beta, maximizing_player=False)

            # Update the best move if we find a higher score
            if score > max_score:
                max_score = score
                best_action = action
            # Update alpha
            alpha = max(alpha, score)

        return best_action

    def minimax(self, state: GameStateDivercite, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """
        Minimax function with alpha-beta pruning.

        Args:
            state (GameStateDivercite): The current game state.
            depth (int): Depth of search left.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            maximizing_player (bool): True if the current player is maximizing.

        Returns:
            float: The evaluated score of the game state.
        """
        if depth == 0 or state.is_done():
            # Return heuristic evaluation at leaf nodes or end-game
            return self.evaluate_state(state)

        if maximizing_player:
            max_eval = -float("inf")
            for action in state.generate_possible_light_actions():
                # Apply action to get a new game state
                new_state = state.apply_action(action)
                eval_score = self.minimax(new_state, depth - 1, alpha, beta, maximizing_player=False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float("inf")
            for action in state.generate_possible_light_actions():
                # Apply action to get a new game state
                new_state = state.apply_action(action)
                eval_score = self.minimax(new_state, depth - 1, alpha, beta, maximizing_player=True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval

    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Enhanced heuristic evaluation function:
        5 × (blocking Divercites from opponent)
        + 5 × (Divercites for you)
        + 2 × (Similar Resource Points)
        - 3 × (Opponent Potential Divercites)
        """
        player1, player2 = state.players
        board_env = state.get_rep().get_env()
        dimensions = state.get_rep().get_dimensions()
        
        my_divercites = 0
        blocking_divercites = 0
        opponent_potential_divercites = 0
        similar_resource_points = 0

        # Scan the board
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                if not state.in_board((i, j)):
                    continue
                    
                # Count existing Divercites
                if state.check_divercite((i, j)):
                    piece = board_env.get((i, j))
                    if piece and piece.get_owner_id() == self.get_id():
                        my_divercites += 1

                # Check neighbors for potential Divercites and blocking
                neighbors = state.get_neighbours(i, j)
                piece_types = [n[0].get_type() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                owner_ids = [n[0].get_owner_id() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                
                # Count similar resource points
                if (i, j) in board_env:
                    curr_piece = board_env[(i, j)]
                    if curr_piece.get_owner_id() == self.get_id():
                        for neighbor in neighbors.values():
                            if (isinstance(neighbor[0], Piece) and 
                                neighbor[0].get_owner_id() == self.get_id() and 
                                neighbor[0].get_type()[1] == curr_piece.get_type()[1]):
                                similar_resource_points += 1

                # Check if we're blocking opponent's potential Divercite
                if any(id == player2.get_id() for id in owner_ids):
                    unique_colors = len(set(pt[0] for pt in piece_types if pt))
                    if unique_colors >= 2:  # If we're blocking a potential Divercite
                        blocking_divercites += 1

                # Count opponent's potential Divercites
                if not board_env.get((i, j)):
                    opponent_pieces = [pt for pt, id in zip(piece_types, owner_ids) 
                                    if id == player2.get_id()]
                    if len(set(p[0] for p in opponent_pieces if p)) >= 2:
                        opponent_potential_divercites += 1

        # Calculate final score using the provided weights
        heuristic_score = (
            6 * blocking_divercites +
            5 * my_divercites +
            2 * similar_resource_points -
            3 * opponent_potential_divercites
        )

        # Add base game score
        base_score = state.scores[self.get_id()] - state.scores[player2.get_id()]
        
        return heuristic_score + base_score
