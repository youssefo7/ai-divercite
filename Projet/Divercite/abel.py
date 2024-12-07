from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.game.game_layout.board import Piece

import random
import time

class MyPlayer(PlayerDivercite):
    """
    Improved Player class for Divercite game implementing Minimax with Alpha-Beta Pruning,
    a more sophisticated heuristic, and dynamic search depth.
    """

    def __init__(self, piece_type: str, name: str = "MyImprovedPlayer"):
        super().__init__(piece_type, name)
        self.colors_used = []
        # Supprimer la table de transposition
        # self.transposition_table = {}
        self.start_time = None
        self.total_time_budget = 15*60  # 15 minutes

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        self.start_time = time.time()
        step = current_state.get_step()

        # Early strategy: try to place different colored cities in the first moves
        if step < 7:
            action = self.place_different_cities(current_state)
            if action is not None:
                return action

        # After the early phase: use minimax search
        max_depth = self.adaptive_depth(step, remaining_time)

        possible_actions = list(current_state.generate_possible_heavy_actions())
        if not possible_actions:
            return None

        best_action = random.choice(possible_actions)
        best_score = float('-inf') if self.is_maximizing_player(current_state) else float('inf')

        # Attempt iterative deepening
        random.shuffle(possible_actions)  # simple shuffle

        for depth in range(2, max_depth + 1):
            score, action_candidate = self.minimax(
                current_state=current_state,
                depth=depth,
                alpha=float('-inf'),
                beta=float('inf'),
                maximizing_player=self.is_maximizing_player(current_state),
                start_time=self.start_time,
                time_limit=remaining_time
            )

            if (self.is_maximizing_player(current_state) and score > best_score) or \
               (not self.is_maximizing_player(current_state) and score < best_score):
                best_score = score
                if action_candidate is not None:
                    best_action = action_candidate

            # Check time usage
            elapsed = time.time() - self.start_time
            if elapsed > 0.9 * remaining_time:
                break

        return best_action

    def place_different_cities(self, current_state: GameState) -> Action:
        possible_actions = list(current_state.generate_possible_heavy_actions())
        random.shuffle(possible_actions)

        current_rep = current_state.get_rep().get_env()

        for action in possible_actions:
            next_state = action.get_next_game_state()
            next_rep = next_state.get_rep().get_env()
            new_pieces = {pos: piece for pos, piece in next_rep.items() if pos not in current_rep}

            if new_pieces:
                (pos, piece) = list(new_pieces.items())[0]
                piece_type_full = piece.get_type()
                # Format: [R/G/B/Y][C/R][W/B]
                piece_color = piece_type_full[0]
                piece_kind = piece_type_full[1]
                # We want to place cities of distinct colors first
                if piece_kind == 'C' and piece_color not in self.colors_used:
                    self.colors_used.append(piece_color)
                    return action
        return None

    def adaptive_depth(self, step: int, remaining_time: float) -> int:
        if remaining_time < 60:
            return 2
        if step < 10:
            return 3
        elif step < 20:
            return 4
        elif step < 30:
            return 5
        elif step < 40:
            return 6
        else:
            return 6

    def is_maximizing_player(self, current_state: GameStateDivercite) -> bool:
        return current_state.next_player.get_id() == self.get_id()

    def minimax(self, current_state: GameStateDivercite, depth: int, alpha: float, beta: float,
                        maximizing_player: bool, start_time: float, time_limit: float):
        if time.time() - start_time > 0.95 * time_limit:
            return self.evaluate_state(current_state), None

        if depth == 0 or current_state.is_done():
            return self.evaluate_state(current_state), None

        possible_actions = list(current_state.generate_possible_heavy_actions())
        if not possible_actions:
            return self.evaluate_state(current_state), None

        possible_actions.sort(key=lambda a: self.quick_evaluation(a.get_next_game_state()), reverse=maximizing_player)

        best_action = None
        if maximizing_player:
            value = float('-inf')
            for action in possible_actions:
                next_state = action.get_next_game_state()
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, False, start_time, time_limit)
                if eval_score > value:
                    value = eval_score
                    best_action = action
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
        else:
            value = float('inf')
            for action in possible_actions:
                next_state = action.get_next_game_state()
                eval_score, _ = self.minimax(next_state, depth - 1, alpha, beta, True, start_time, time_limit)
                if eval_score < value:
                    value = eval_score
                    best_action = action
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return value, best_action

    def hash_state(self, state: GameStateDivercite) -> int:
        rep = state.get_rep().get_env()
        items = sorted(rep.items(), key=lambda x: x[0])
        board_tuple = tuple((pos, piece.get_type()) for pos, piece in items)
        key = (board_tuple, state.next_player.get_id(), state.get_step())
        return hash(key)

    def evaluate_state(self, state: GameStateDivercite) -> float:
        my_id = self.get_id()
        # color_to_id maps 'W' or 'B' to player_id
        color_to_id = {}
        for p in state.players:
            color_to_id[p.get_piece_type()] = p.get_id()

        opponent_id = [p.get_id() for p in state.players if p.get_id() != my_id][0]

        my_score = state.scores[my_id]
        opponent_score = state.scores[opponent_id]

        my_potential = self.evaluate_potential(state, my_id, color_to_id)
        opp_potential = self.evaluate_potential(state, opponent_id, color_to_id)

        return (my_score - opponent_score) + 0.5 * (my_potential - opp_potential)

    def evaluate_potential(self, state: GameStateDivercite, player_id: int, color_to_id: dict) -> float:
        board = state.get_rep().get_env()
        player_potential = 0.0

        for (i, j), piece in board.items():
            if isinstance(piece, Piece):
                piece_type_full = piece.get_type()
                # Format: [R/G/B/Y][C/R][W/B]
                c_color = piece_type_full[0]  # Color (R, G, B, Y)
                c_kind = piece_type_full[1]   # 'C' or 'R'
                c_player_color = piece_type_full[-1]  # 'W' or 'B'

                owner_id = color_to_id.get(c_player_color)
                if owner_id is None:
                    # Debug: Unknown player color
                    print(f"Debug: c_player_color {c_player_color} not found in color_to_id")
                    continue

                if c_kind == 'C' and owner_id == player_id:
                    neighbours = state.get_neighbours(i, j).values()
                    distinct_colors = set()
                    same_color_count = 0

                    for (_, (ii, jj)) in neighbours:
                        if (ii, jj) in board:
                            neigh_piece = board[(ii, jj)]
                            neigh_type = neigh_piece.get_type()
                            if len(neigh_type) == 3 and neigh_type[1] == 'R':  # Resource
                                r_color = neigh_type[0]
                                distinct_colors.add(r_color)
                                if r_color == c_color:
                                    same_color_count += 1

                    # Evaluate potential
                    if len(distinct_colors) == 4:
                        player_potential += 4.0
                    elif len(distinct_colors) == 3:
                        player_potential += 2.5
                    else:
                        player_potential += same_color_count * 0.5

        return player_potential

    def quick_evaluation(self, state: GameStateDivercite) -> float:
        my_id = self.get_id()
        opponent_id = [p.get_id() for p in state.players if p.get_id() != my_id][0]
        my_score = state.scores[my_id]
        opponent_score = state.scores[opponent_id]
        return my_score - opponent_score

