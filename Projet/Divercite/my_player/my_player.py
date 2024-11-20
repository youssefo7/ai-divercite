from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError

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

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm with alpha-beta pruning to choose the best action.

        Args:
            current_state (GameState): The current game state.
            remaining_time (int): Remaining time for the player.

        Returns:
            Action: The best action as determined by minimax.
        """
        max_depth = self.adaptive_depth(current_state.get_step())
        _, best_action = self.minimax(
            current_state=current_state,
            depth=max_depth,
            alpha=float('-inf'),
            beta=float('inf'),
            maximizing_player=True
        )
        return best_action

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
        elif step < 20:
            return 3
        elif step < 30:
            return 4
        else:
            return 5

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
        if depth == 0 or current_state.is_done():
            return self.evaluate_state(current_state), None

        possible_actions = list(current_state.generate_possible_heavy_actions())
        if not possible_actions:
            return self.evaluate_state(current_state), None

        best_action = None

        if maximizing_player:
            max_eval = float('-inf')
            for action in possible_actions:
                next_state = action.get_next_game_state()
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_action = action
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_action

        else:
            min_eval = float('inf')
            for action in possible_actions:
                next_state = action.get_next_game_state()
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_action = action
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_action

    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Evaluate a game state based on the player's score.

        Args:
            state (GameStateDivercite): The state to evaluate.

        Returns:
            float: Heuristic score for the state.
        """
        my_score = state.scores[self.get_id()]
        opponent_id = [p.get_id() for p in state.players if p.get_id() != self.get_id()][0]
        opponent_score = state.scores[opponent_id]

        # Heuristic: maximize my score and minimize the opponent's score.
        return my_score - opponent_score
