from io import BytesIO
import pandas as pd
from app.schemas.investments_results import (  # Исправлен импорт
    InvestmentStatisticsSchema,
    EnterpriseDetail, OptimizationResult
)


class InvestmentOptimizer:

    @classmethod
    def load_data_from_excel_bytes(cls, file_bytes):
        excel_io = BytesIO(file_bytes)
        df = pd.read_excel(excel_io, header=None)
        profit_table = df.values.tolist()
        investments = [row[0] for row in profit_table]
        profits = [row[1:] for row in profit_table]
        return investments, profits

    @classmethod
    def get_profit(cls, profits, investments, e, x):
        i = investments.index(x)
        return profits[i][e]

    @classmethod
    def optimize_investments(cls, investments, profits):
        num_enterprises = len(profits[0])
        num_invest_levels = len(investments)

        dp = [[0] * num_invest_levels for _ in range(num_enterprises + 1)]
        choice = [[0] * num_invest_levels for _ in range(num_enterprises + 1)]

        for i in range(1, num_enterprises + 1):
            for j in range(num_invest_levels):
                best_profit = 0
                best_k = 0
                for k in range(j + 1):
                    current_profit = dp[i - 1][j - k] + cls.get_profit(
                        profits, investments, i - 1, investments[k])
                    if current_profit > best_profit:
                        best_profit = current_profit
                        best_k = k
                dp[i][j] = best_profit
                choice[i][j] = best_k

        max_profit = dp[num_enterprises][num_invest_levels - 1]
        distribution = [0] * num_enterprises
        remaining_j = num_invest_levels - 1
        for i in range(num_enterprises, 0, -1):
            k = choice[i][remaining_j]
            distribution[i - 1] = investments[k]
            remaining_j -= k

        return max_profit, distribution

    @classmethod
    def get_investment_stats(cls, investments, profits, distribution):
        total_investment = sum(distribution)
        enterprise_details = []
        total_profit = 0

        for i, invest in enumerate(distribution):
            profit = cls.get_profit(profits, investments, i, invest)
            total_profit += profit
            enterprise_details.append(EnterpriseDetail(
                enterprise_id=i + 1,
                investment=invest,
                profit=profit,
                roi=(profit / invest if invest > 0 else 0)
            ))

        return InvestmentStatisticsSchema(
            total_investment=total_investment,
            total_profit=total_profit,
            roi=total_profit / total_investment if total_investment > 0 else 0,
            enterprises=enterprise_details
        )

    @classmethod
    def run_investment_optimization(cls, file_bytes):
        investments, profits = cls.load_data_from_excel_bytes(file_bytes)
        max_profit, distribution = cls.optimize_investments(investments, profits)
        statistics = cls.get_investment_stats(investments, profits, distribution)

        return OptimizationResult(
            max_profit=max_profit,
            distribution=distribution,
            statistics=statistics
        )
