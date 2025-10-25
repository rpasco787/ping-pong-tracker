from pydantic import BaseModel, Field, model_validator
from typing import List


class GameScore(BaseModel):
    home: int = Field(ge=0)
    away: int = Field(ge=0)

    @model_validator(mode="after")
    def no_ties_in_single_game(self):
        if self.home == self.away:
            raise ValueError("Game cannot end in a tie")
        return self


class MatchIn(BaseModel):
    played_at: str  # ISO 8601 string; we’ll parse/store as-is for Section 2
    home_id: int
    away_id: int
    games: List[GameScore] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_match_has_winner_and_ids(self):
        if self.home_id == self.away_id:
            raise ValueError("home_id must differ from away_id")

        home_wins = sum(1 for g in self.games if g.home > g.away)
        away_wins = len(self.games) - home_wins

        if home_wins == away_wins:
            raise ValueError("Match must have a winner (games cannot split evenly)")
        return self


class MatchOut(BaseModel):
    id: int
    played_at: str
    home_id: int
    away_id: int
    games: List[GameScore]
