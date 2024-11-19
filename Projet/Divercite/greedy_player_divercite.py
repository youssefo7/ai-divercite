from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite

class MyPlayer(PlayerDivercite):
    """
    Strategic Divercite player that prioritizes:
    1. Blocking opponent's potential Divercités
    2. Placing cities before resources unless blocking is needed
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        super().__init__(piece_type, name)

    def detect_potential_divercite(self, state: GameStateDivercite, action: Action) -> bool:
        """
        Check if an action would create a Divercité.
        
        Args:
            state: Current game state
            action: Action to check
            
        Returns:
            bool: True if action would create a Divercité
        """
        next_state = action.get_next_game_state()
        pos = action.get_action_as_dict()["pos"]
        return next_state.check_divercite(pos)

    def get_blocking_move(self, current_state: GameStateDivercite) -> Action:
        """
        Find a move that blocks the opponent's potential Divercité.
        
        Returns:
            Action: Blocking move if found, None otherwise
        """
        opponent_id = 1 if self.get_id() == 0 else 0
        
        # Check all possible actions
        for action in current_state.generate_possible_heavy_actions():
            action_dict = action.get_action_as_dict()
            
            # If this is the opponent's potential move
            test_state = action.get_next_game_state()
            if test_state.check_divercite(action_dict["pos"]):
                # Find a blocking move for this position
                for blocking_action in current_state.generate_possible_heavy_actions():
                    blocking_dict = blocking_action.get_action_as_dict()
                    if blocking_dict["pos"] == action_dict["pos"]:
                        return blocking_action
        return None

    def is_city_move(self, action: Action) -> bool:
        """
        Check if an action places a city.
        """
        return action.get_action_as_dict()["piece_type"][0] == 'C'

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Choose the best action following our strategy:
        1. Block opponent's potential Divercités
        2. Place cities before resources (unless blocking)
        3. Otherwise use minimax for optimal play
        """
        # First priority: Block opponent's potential Divercité
        blocking_move = self.get_blocking_move(current_state)
        if blocking_move:
            return blocking_move

        # Generate all possible moves
        possible_actions = list(current_state.generate_possible_heavy_actions())
        
        # Separate cities and resources
        city_moves = []
        resource_moves = []
        for action in possible_actions:
            if self.is_city_move(action):
                city_moves.append(action)
            else:
                resource_moves.append(action)

        # Count how many cities we've placed
        my_cities_placed = 0
        board_env = current_state.get_rep().get_env()
        for piece in board_env.values():
            if piece and piece.get_owner_id() == self.get_id() and piece.get_type()[0] == 'C':
                my_cities_placed += 1

        # Second priority: Follow city-first strategy
        # Place cities first unless we've placed all 4
        if my_cities_placed < 4 and city_moves:
            return self.get_best_move(current_state, city_moves)
        elif resource_moves:
            return self.get_best_move(current_state, resource_moves)
        else:
            return self.get_best_move(current_state, possible_actions)

    def get_best_move(self, current_state: GameState, moves: list) -> Action:
        """
        Select the best move from the given list of moves.
        """
        if not moves:
            return next(current_state.generate_possible_heavy_actions())
            
        best_action = moves[0]
        best_score = self.evaluate_state(best_action.get_next_game_state())

        for action in moves[1:]:
            next_state = action.get_next_game_state()
            score = self.evaluate_state(next_state)
            if score > best_score:
                best_action = action
                best_score = score

        return best_action

    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Evaluate the current state with emphasis on Divercités and blocking.
        """
        opponent_id = 1 if self.get_id() == 0 else 0
        my_score = state.scores[self.get_id()]
        opponent_score = state.scores[opponent_id]
        
        # Base score difference
        evaluation = my_score - opponent_score * 2  # Weight opponent's score more heavily
        
        # Add bonus for our Divercités
        board_env = state.get_rep().get_env()
        dimensions = state.get_rep().get_dimensions()
        
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                if not state.in_board((i, j)):
                    continue
                    
                piece = board_env.get((i, j))
                if piece and piece.get_owner_id() == self.get_id():
                    if state.check_divercite((i, j)):
                        evaluation += 10  # Big bonus for our Divercités
                elif piece and piece.get_owner_id() == opponent_id:
                    if state.check_divercite((i, j)):
                        evaluation -= 15  # Bigger penalty for opponent's Divercités
        
        return evaluation