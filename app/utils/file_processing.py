import pandas as pd
import numpy as np
from io import BytesIO
import uuid
import os

UPLOAD_DIR = "processed_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_excel(file_content: bytes) -> tuple[str, str]:
    df = pd.read_excel(BytesIO(file_content))

    # Пример обработки данных
    processed_df = df.T
    processed_df['Total'] = np.sum(processed_df, axis=1)

    output = BytesIO()
    processed_df.to_excel(output, index=False)
    output.seek(0)

    filename = f"processed_{uuid.uuid4().hex}.xlsx"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(output.getvalue())

    return filename, file_path
