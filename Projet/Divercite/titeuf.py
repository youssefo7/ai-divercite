from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from seahorse.game.light_action import LightAction
from seahorse.game.game_layout.board import Piece

class MyPlayer(PlayerDivercite):

    def __init__(self, piece_type: str, name: str = "MyPlayer", depth_limit: int = 3):
        super().__init__(piece_type, name)
        self.depth_limit = depth_limit

    def get_adaptive_depth(self, current_state: GameStateDivercite) -> int:

        # Count number of pieces placed on the board
        board_env = current_state.get_rep().get_env()
        pieces_placed = len([piece for piece in board_env.values() if piece])
        
        # Adjust depth based on game progress
                
        if pieces_placed <= 5:
            return 2  # Deep search for endgame
        if pieces_placed > 5 and pieces_placed <= 20:
              return 2  # Deep search for endgame
        if pieces_placed >= 30:
            return 5  # Deep search for endgame
        elif pieces_placed >= 20:
            return 4  # Increased depth for mid-late game
        else:
            return self.depth_limit  # Base depth for early game
    
    def compute_action(self, current_state: GameStateDivercite, remaining_time: int = 1e9, **kwargs) -> Action:
        
        current_depth = self.get_adaptive_depth(current_state)

        def check_one_off_divercite(state, player_id):
            """Helper to find positions where a player is one move away from Divercite"""
            board_env = state.get_rep().get_env()
            dimensions = state.get_rep().get_dimensions()
            critical_moves = []

            for i in range(dimensions[0]):
                for j in range(dimensions[1]):
                    if not state.in_board((i, j)) or board_env.get((i, j)):
                        continue

                    # Check if this empty position would complete a Divercite
                    neighbors = state.get_neighbours(i, j)
                    piece_types = [n[0].get_type() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                    owner_ids = [n[0].get_owner_id() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                    
                    # Filter pieces owned by the player
                    player_pieces = [pt for pt, id in zip(piece_types, owner_ids) if id == player_id]
                    if player_pieces:
                        colors = set(p[0] for p in player_pieces if p)
                        if len(colors) >= 3:  # Player already has 3 different colors
                            # Check if placing a piece here would complete a Divercite
                            for action in state.generate_possible_light_actions():
                                # Ensure action has 'position' in its dictionary and is valid
                                if hasattr(action, "data") and "position" in action.data:
                                    if action.data["position"] == (i, j):
                                        new_state = state.apply_action(action)
                                        if new_state.check_divercite((i, j)):
                                            critical_moves.append(action)
            
            return critical_moves

        # Get current scores
        my_score = current_state.scores[self.get_id()]
        opponent_id = current_state.players[1].get_id() if self.get_id() == current_state.players[0].get_id() else current_state.players[0].get_id()
        opponent_score = current_state.scores[opponent_id]

        # Check for critical Divercite situations
        opponent_critical_moves = check_one_off_divercite(current_state, opponent_id)
        my_critical_moves = check_one_off_divercite(current_state, self.get_id())

        # Case 1: If opponent is one off a Divercite, block immediately
        if opponent_critical_moves and not my_critical_moves:
            return opponent_critical_moves[0]  # Block the first critical move found
        
        # Case 2: If we are one off a Divercite and opponent is not, complete our Divercite
        if my_critical_moves and not opponent_critical_moves:
            return my_critical_moves[0]  # Complete our Divercite
        
        # Case 3: If both players are one off a Divercite
        if my_critical_moves and opponent_critical_moves:
            if opponent_score >= my_score:
                # If opponent is winning or tied, block them
                return opponent_critical_moves[0]
            else:
                # If we're winning, complete our Divercite
                return my_critical_moves[0]

        # If no critical situations, proceed with normal minimax search
        best_action = None
        max_score = -float("inf")
        alpha = -float("inf")
        beta = float("inf")

        # Regular minimax logic
        for action in current_state.generate_possible_light_actions():
            new_state = current_state.apply_action(action)
            score = self.minimax(new_state, current_depth - 1, alpha, beta, maximizing_player=False)
            
            if score > max_score:
                max_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action

    def minimax(self, state: GameStateDivercite, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:

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
