from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.game.light_action import LightAction

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game using minimax with alpha-beta pruning.
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer", depth_limit: int = 3):
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
        Heuristic evaluation function for a game state.

        Args:
            state (GameStateDivercite): The game state to evaluate.

        Returns:
            float: Evaluated score of the game state.
        """
        player1, player2 = state.players
        # For now, use a basic heuristic based on the agent's score in the state
        return state.scores[self.get_id()] - state.scores[player2.get_id()]
