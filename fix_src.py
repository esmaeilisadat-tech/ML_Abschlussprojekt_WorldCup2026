import pandas as pd

with open('src/update_live_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'updated.to_csv(DATA_DIR / "model_dataset_live.csv", index=False)',
    'updated.to_csv(DATA_DIR / "model_dataset_live.csv", index=False)\n        wc2026 = updated[(updated[\'tournament\'].isin([\'World Cup\', \'FIFA World Cup\'])) & (pd.to_datetime(updated[\'date\'].astype(str).str.split().str[0]).dt.year == 2026)]\n        wc2026.to_csv(DATA_DIR / \'wc2026.csv\', index=False)'
)

with open('src/update_live_data.py', 'w', encoding='utf-8') as f:
    f.write(content)
