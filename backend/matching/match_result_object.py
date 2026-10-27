from dataclasses import dataclass
from typing import Literal, Optional, Tuple

MatchStatus = Literal["match", "ambiguous", "not found"]

@dataclass(frozen=True)
class MatchResult:
    status: MatchStatus
    concept: Optional[str] = None
    candidates: Tuple[str, ...] = ()
    label_kind: Optional[str] = None
    simplified_key: Optional[str] = None
    score: Optional[float] = None
    method: str = "exact"