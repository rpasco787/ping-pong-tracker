from typing import Dict, List, TypedDict


class Player(TypedDict):
    id: int
    name: str
    email: str | None
    wins: int
    losses: int
    points: int


class GameScore(TypedDict):
    home: int
    away: int


class Match(TypedDict):
    id: int
    played_at: str
    home_id: int
    away_id: int
    games: List[GameScore]


WIN_POINTS = 3  # scoring rule: 3 points per match win (simple, adjustable)


class InMemoryStore:
    def __init__(self) -> None:
        self.players: Dict[int, Player] = {}
        self.matches: List[Match] = []
        self._player_seq = 0
        self._match_seq = 0

    def next_player_id(self) -> int:
        self._player_seq += 1
        return self._player_seq

    def next_match_id(self) -> int:
        self._match_seq += 1
        return self._match_seq


store = InMemoryStore()


def compute_winner(games: List[GameScore]) -> str:
    """Return 'home' or 'away' based on who won more games."""
    home_wins = sum(1 for g in games if g["home"] > g["away"])
    away_wins = len(games) - home_wins
    return "home" if home_wins > away_wins else "away"
