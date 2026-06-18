import pandas as pd
import json

base_dataset = pd.read_csv('data/processed/model_dataset.csv')
base_dataset['date'] = pd.to_datetime(base_dataset['date'].astype(str).str.split().str[0])

# Extract 2022 World Cup
wc2022 = base_dataset[(base_dataset['tournament'].isin(['World Cup', 'FIFA World Cup'])) & (base_dataset['date'].dt.year == 2022)].copy()
wc2022.to_csv('data/processed/wc2022.csv', index=False)

# Extract 2026 World Cup
live_dataset = pd.read_csv('data/processed/model_dataset_live.csv')
live_dataset['date'] = pd.to_datetime(live_dataset['date'].astype(str).str.split().str[0])
wc2026 = live_dataset[(live_dataset['tournament'].isin(['World Cup', 'FIFA World Cup'])) & (live_dataset['date'].dt.year == 2026)].copy()
wc2026.to_csv('data/processed/wc2026.csv', index=False)

print(f"Created wc2022.csv with {len(wc2022)} rows")
print(f"Created wc2026.csv with {len(wc2026)} rows")

# Now fix the notebook to use these!
with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            # Replace 2022 loading logic
            if "wc2022 = model_dataset[(model_dataset['tournament']" in line:
                new_source.append("    wc2022 = pd.read_csv(DATA_DIR / 'wc2022.csv')\n")
                new_source.append("    wc2022['date'] = pd.to_datetime(wc2022['date'])\n")
                continue
            
            # Replace 2026 loading logic
            if "wc2026_actual = model_dataset[(model_dataset['tournament']" in line:
                new_source.append("    wc2026_actual = pd.read_csv(DATA_DIR / 'wc2026.csv')\n")
                new_source.append("    wc2026_actual['date'] = pd.to_datetime(wc2026_actual['date'])\n")
                continue
                
            # Remove any left-over model_dataset['date'] parsing since it's loaded properly
            if "model_dataset['date'] = pd.to_datetime" in line:
                new_source.append("    model_dataset['date'] = pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])\n")
                continue
                
            new_source.append(line)
        cell['source'] = new_source

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

# Add logic to the end of live update cell to also update wc2026.csv
with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "updated.to_csv(DATA_DIR / \"model_dataset_live.csv\", index=False)" in source:
            source = source.replace(
                "updated.to_csv(DATA_DIR / \"model_dataset_live.csv\", index=False)",
                "updated.to_csv(DATA_DIR / \"model_dataset_live.csv\", index=False)\n        \n        # آپدیت فایل مستقل جام جهانی 2026\n        wc2026 = updated[(updated['tournament'].isin(['World Cup', 'FIFA World Cup'])) & (pd.to_datetime(updated['date'].astype(str).str.split().str[0]).dt.year == 2026)]\n        wc2026.to_csv(DATA_DIR / 'wc2026.csv', index=False)\n"
            )
            cell['source'] = [line + '\n' for line in source.split('\n')]

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook updated!")
