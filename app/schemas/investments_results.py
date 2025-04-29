from pydantic import BaseModel
from typing import List


class EnterpriseDetail(BaseModel):
    enterprise_id: int
    investment: float
    profit: float
    roi: float


class InvestmentStatisticsSchema(BaseModel):
    total_investment: float
    total_profit: float
    roi: float
    enterprises: List[EnterpriseDetail]


class OptimizationResult(BaseModel):
    max_profit: float
    distribution: List[float]
    statistics: InvestmentStatisticsSchema
