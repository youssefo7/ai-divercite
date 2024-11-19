from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from game_state_divercite import GameStateDivercite
from seahorse.game.light_action import LightAction
from seahorse.game.game_layout.board import Piece

class MyPlayer(PlayerDivercite):
    """
    Strategic Divercite player that prioritizes:
    1. Blocking opponent's potential Divercités
    2. Placing cities before resources unless blocking is needed
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer", depth_limit: int = 3):
        super().__init__(piece_type, name)
        self.depth_limit = depth_limit

    def detect_potential_divercite(self, state: GameStateDivercite, position: tuple, player_id: int) -> bool:
        """
        Check if placing a piece at the given position would create a Divercité for the specified player.
        
        Args:
            state: Current game state
            position: Position to check (x, y)
            player_id: ID of the player to check for
            
        Returns:
            bool: True if a Divercité is possible at this position
        """
        # Get neighboring pieces
        neighbors = state.get_neighbours(position[0], position[1])
        
        # Count unique colors of resources around the position
        resource_colors = set()
        for neighbor in neighbors.values():
            if isinstance(neighbor[0], Piece):
                piece_type = neighbor[0].get_type()
                if piece_type[0] != 'C':  # If it's a resource
                    resource_colors.add(piece_type[0])
        
        # If there are already 3 or more different colors, a Divercité is possible
        return len(resource_colors) >= 3

    def get_blocking_move(self, state: GameStateDivercite) -> LightAction:
        """
        Find a move that blocks the opponent's potential Divercité.

        Args:
            state (GameStateDivercite): The current game state.

        Returns:
            LightAction: A blocking move if found, or None otherwise.
        """
        # Determine the opponent's ID
        my_id = self.get_id()
        opponent_id = state.players[1].get_id() if my_id == state.players[0].get_id() else state.players[0].get_id()

        # Retrieve board environment and dimensions
        board_env = state.get_rep().get_env()
        dimensions = state.get_rep().get_dimensions()

        # Iterate through all positions on the board
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                position = (i, j)

                # Skip positions outside the board or already occupied
                if not state.in_board(position) or board_env.get(position):
                    continue

                # Check if this position creates a Divercité for the opponent
                if self.detect_potential_divercite(state, position, opponent_id):
                    # Look for a legal blocking move
                    for action in state.generate_possible_light_actions():
                        # Ensure action has a 'data' attribute and contains the necessary keys
                        if hasattr(action, "data"):
                            action_data = action.data
                            if "position" in action_data and action_data["position"] == position:
                                # Debug: Log piece type if needed
                                piece = action_data.get("piece", None)
                                print(f"Blocking action found: {action_data} with piece type: {piece}")
                                return action
                            else:
                                # Debug: Log mismatched action
                                print(f"Mismatched action: {action_data}, expected position: {position}")
                        else:
                            print(f"Action has no 'data': {action.__dict__}")

        # Return None if no blocking move is found
        return None


    def should_place_city(self, state: GameStateDivercite) -> bool:
        """
        Determine if we should place a city or resource next.
        """
        board_env = state.get_rep().get_env()
        city_count = 0
        total_pieces = 0
        
        # Count cities and total pieces
        for piece in board_env.values():
            if piece and piece.get_owner_id() == self.get_id():
                total_pieces += 1
                if piece.get_type()[0] == 'C':
                    city_count += 1
                    
        # Place all cities first (unless we need to block)
        return city_count < 4

    def compute_action(self, current_state: GameStateDivercite, remaining_time: int = 1e9, **kwargs) -> Action:
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
        possible_actions = list(current_state.generate_possible_light_actions())
        
        # Separate cities and resources
        city_moves = []
        resource_moves = []
        for action in possible_actions:
            # Inspect the internal data of the object
            print(action.__dict__)  # Display the internal data of the object

            # Check if 'data' exists in action.__dict__
            if hasattr(action, "data"):
                action_data = action.data
                # Verify if 'piece' exists in the action data
                if "piece" in action_data:
                    # Check if the first character of 'piece' is 'C' (for city)
                    if action_data["piece"][0] == 'C':
                        city_moves.append(action)
                    else:
                        resource_moves.append(action)
                else:
                    print(f"L'action n'a pas d'attribut 'piece' dans 'data': {action_data}")
            else:
                print(f"L'action n'a pas d'attribut 'data': {action.__dict__}")



        # Second priority: Follow city-first strategy
        if self.should_place_city(current_state) and city_moves:
            # Use minimax to choose the best city placement
            return self.get_best_move(current_state, city_moves)
        elif resource_moves:
            # Use minimax to choose the best resource placement
            return self.get_best_move(current_state, resource_moves)
        else:
            # Fallback to any legal move
            return self.get_best_move(current_state, possible_actions)

    def get_best_move(self, state: GameStateDivercite, moves: list) -> Action:
        """
        Use minimax to select the best move from the given list of moves.
        """
        best_action = None
        max_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for action in moves:
            new_state = state.apply_action(action)
            score = self.minimax(new_state, self.depth_limit - 1, alpha, beta, False)
            
            if score > max_score:
                max_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action

    def minimax(self, state: GameStateDivercite, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """
        Minimax implementation with alpha-beta pruning.
        """
        if depth == 0 or state.is_done():
            return self.evaluate_state(state)

        if maximizing_player:
            value = float("-inf")
            for action in state.generate_possible_light_actions():
                value = max(value, self.minimax(state.apply_action(action), depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float("inf")
            for action in state.generate_possible_light_actions():
                value = min(value, self.minimax(state.apply_action(action), depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value

    def evaluate_state(self, state: GameStateDivercite) -> float:
        """
        Evaluate the current state with emphasis on Divercités and blocking.
        """
        opponent_id = state.players[1].get_id() if self.get_id() == state.players[0].get_id() else state.players[0].get_id()
        my_score = state.scores[self.get_id()]
        opponent_score = state.scores[opponent_id]
        
        # Base evaluation from scores
        evaluation = my_score - opponent_score
        
        # Count potential Divercités
        board_env = state.get_rep().get_env()
        dimensions = state.get_rep().get_dimensions()
        my_potential_divercites = 0
        opponent_potential_divercites = 0
        
        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                if not state.in_board((i, j)) or board_env.get((i, j)):
                    continue
                
                if self.detect_potential_divercite(state, (i, j), self.get_id()):
                    my_potential_divercites += 1
                if self.detect_potential_divercite(state, (i, j), opponent_id):
                    opponent_potential_divercites += 1
        
        # Heavily weight potential Divercités
        evaluation += my_potential_divercites * 3
        evaluation -= opponent_potential_divercites * 5  # Penalize opponent's opportunities more
        
        return evaluation