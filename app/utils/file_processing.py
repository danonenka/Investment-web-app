from io import BytesIO
import pandas as pd
import uuid
import os
from .investments_optimizer import InvestmentOptimizer
from ..schemas.investments_results import OptimizationResult

UPLOAD_DIR = "processed_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_excel(file_content: bytes) -> tuple[str, str, OptimizationResult]:
    result = InvestmentOptimizer.run_investment_optimization(file_content)

    report_data = {
        'Предприятие': [f"Предприятие {i + 1}" for i in range(len(result.distribution))],
        'Инвестиции (млн)': result.distribution,
        'Прибыль (млн)': [e.profit for e in result.statistics.enterprises],
        'ROI (%)': [round(e.roi * 100, 2) for e in result.statistics.enterprises]
    }
    df = pd.DataFrame(report_data)

    # Сохраняем отчет
    filename = f"report_{uuid.uuid4().hex}.xlsx"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, index=False)
        summary_df = pd.DataFrame({
            'Метрика': ['Общая сумма инвестиций', 'Общая прибыль', 'ROI'],
            'Значение': [
                result.statistics.total_investment,  # Исправлено
                result.statistics.total_profit,  # Исправлено
                f"{round(result.statistics.roi * 100, 2)}%"  # Исправлено
            ]
        })
        summary_df.to_excel(writer, sheet_name='Итоги', index=False)

    return filename, file_path, result