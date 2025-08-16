from typing import List
from pydantic import BaseModel, Field, conlist

class EvalCriterionScore(BaseModel):
    name: str = Field(..., description="Criterion label, e.g., 'Faithfulness'")
    score: float = Field(..., ge=1, le=5, description="Score 1-5")
    justification: str = Field(..., description="One concise sentence explaining the score")

class EvaluationReport(BaseModel):
    # v2 uses min_length / max_length (not min_items / max_items)
    criteria: conlist(EvalCriterionScore, min_length=3, max_length=6)
    overall: float = Field(..., ge=1, le=5, description="Weighted average 1–5")
    # <-- add this:
    recommendations: List[str] = Field(default_factory=list, description="Actionable fixes")
