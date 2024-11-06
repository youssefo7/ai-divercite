from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.game.light_action import LightAction  # Import if LightAction is used in the generated actions

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes moves based on a simple greedy heuristic.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "MyPlayer")
        """
        super().__init__(piece_type, name)

    def compute_action(self, current_state: GameStateDivercite, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use a greedy algorithm to choose the best action based on immediate score.

        Args:
            current_state (GameStateDivercite): The current game state.

        Returns:
            Action: The best action as determined by the greedy heuristic.
        """
        best_move = None
        max_score = -float("inf")
        
        # Iterate over all possible light actions to evaluate each one
        for action in current_state.generate_possible_light_actions():
            # Apply the action to get a new game state and evaluate its score
            new_state = current_state.apply_action(action)
            score = new_state.scores[self.get_id()]  # Get the agent's score in this new state

            # Update the best move if this action yields a higher score
            if score > max_score:
                max_score = score
                best_move = action

        return best_move if best_move else random.choice(list(current_state.generate_possible_light_actions()))
