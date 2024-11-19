import copy
import json
import random
from typing import Dict, Generator, List, Optional, Set, Tuple

from board_divercite import BoardDivercite
from player_divercite import PlayerDivercite
from seahorse.game.game_layout.board import Piece
from seahorse.game.game_state import GameState
from seahorse.game.heavy_action import HeavyAction
from seahorse.game.light_action import LightAction
from seahorse.player.player import Player
from seahorse.utils.serializer import Serializable
from seahorse.game.action import Action

class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game using minimax with alpha-beta pruning and opening strategy.
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer", depth_limit: int = 4):
        super().__init__(piece_type, name)
        self.depth_limit = depth_limit
        self.move_count = 0

    def is_first_player(self, state: GameState) -> bool:
        return self.get_id() == state.players[0].get_id()

    def get_board_center(self, state: GameState) -> tuple:
        dimensions = state.get_rep().get_dimensions()
        return (dimensions[0] // 2, dimensions[1] // 2)

    def find_mirror_move(self, state: GameState, last_action: LightAction) -> LightAction:
        dimensions = state.get_rep().get_dimensions()
        center_x, center_y = self.get_board_center(state)
        
        # Get the opponent's last move position
        last_pos = last_action.position
        
        # Calculate the mirror position relative to the center
        mirror_x = 2 * center_x - last_pos[0]
        mirror_y = 2 * center_y - last_pos[1]
        
        # Create a mirrored action with the same piece type but our color
        for action in state.generate_possible_light_actions():
            if action.position == (mirror_x, mirror_y):
                return action
                
        # If mirror position is not available, fall back to minimax
        return None

    def get_last_opponent_action(self, state: GameState) -> LightAction:
        history = state.get_history()
        if history:
            return history[-1]
        return None

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        # Increment move counter
        self.move_count += 1

        # Opening strategy for first 5 moves
        if self.move_count <= 5:
            # If we're the first player
            if self.is_first_player(current_state):
                if self.move_count == 1:
                    # Place red in the center for first move
                    center = self.get_board_center(current_state)
                    for action in current_state.generate_possible_light_actions():
                        if action.data["position"] == center and action.data["piece"][0] == 'R':
                            return action
                
            # If we're the second player or it's not our first move
            last_action = self.get_last_opponent_action(current_state)
            if last_action:
                mirror_move = self.find_mirror_move(current_state, last_action)
                if mirror_move:
                    return mirror_move

        # Fall back to minimax strategy after opening or if mirror move is not available
        best_action = None
        max_score = -float("inf")
        alpha = -float("inf")
        beta = float("inf")

        for action in current_state.generate_possible_light_actions():
            new_state = current_state.apply_action(action)
            score = self.minimax(new_state, self.depth_limit - 1, alpha, beta, maximizing_player=False)
            if score > max_score:
                max_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action

    def minimax(self, state: GameState, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        if depth == 0 or state.is_done():
            return self.evaluate_state(state)

        if maximizing_player:
            max_eval = -float("inf")
            for action in state.generate_possible_light_actions():
                new_state = state.apply_action(action)
                eval_score = self.minimax(new_state, depth - 1, alpha, beta, maximizing_player=False)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for action in state.generate_possible_light_actions():
                new_state = state.apply_action(action)
                eval_score = self.minimax(new_state, depth - 1, alpha, beta, maximizing_player=True)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def evaluate_state(self, state: GameState) -> float:
        player1, player2 = state.players
        board_env = state.get_rep().get_env()
        dimensions = state.get_rep().get_dimensions()
        
        my_divercites = 0
        blocking_divercites = 0
        opponent_potential_divercites = 0
        similar_resource_points = 0

        for i in range(dimensions[0]):
            for j in range(dimensions[1]):
                if not state.in_board((i, j)):
                    continue
                    
                if state.check_divercite((i, j)):
                    piece = board_env.get((i, j))
                    if piece and piece.get_owner_id() == self.get_id():
                        my_divercites += 1

                neighbors = state.get_neighbours(i, j)
                piece_types = [n[0].get_type() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                owner_ids = [n[0].get_owner_id() if isinstance(n[0], Piece) else None for n in neighbors.values()]
                
                if (i, j) in board_env:
                    curr_piece = board_env[(i, j)]
                    if curr_piece.get_owner_id() == self.get_id():
                        for neighbor in neighbors.values():
                            if (isinstance(neighbor[0], Piece) and 
                                neighbor[0].get_owner_id() == self.get_id() and 
                                neighbor[0].get_type()[1] == curr_piece.get_type()[1]):
                                similar_resource_points += 1

                if any(id == player2.get_id() for id in owner_ids):
                    unique_colors = len(set(pt[0] for pt in piece_types if pt))
                    if unique_colors >= 2:
                        blocking_divercites += 1

                if not board_env.get((i, j)):
                    opponent_pieces = [pt for pt, id in zip(piece_types, owner_ids) 
                                    if id == player2.get_id()]
                    if len(set(p[0] for p in opponent_pieces if p)) >= 2:
                        opponent_potential_divercites += 1

        heuristic_score = (
            6 * blocking_divercites +
            5 * my_divercites +
            2 * similar_resource_points -
            3 * opponent_potential_divercites
        )

        base_score = state.scores[self.get_id()] - state.scores[player2.get_id()]
        
        return heuristic_score + base_score