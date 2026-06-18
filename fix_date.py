import json
with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("pd.to_datetime(model_dataset['date'])", "pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])")
content = content.replace("nr['date'] = pd.to_datetime(row['date'])", "nr['date'] = pd.to_datetime(row['date']).strftime('%Y-%m-%d')")

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/update_live_data.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("pd.to_datetime(model_dataset['date'])", "pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])")
content = content.replace("nr['date'] = pd.to_datetime(row['date'])", "nr['date'] = pd.to_datetime(row['date']).strftime('%Y-%m-%d')")

with open('src/update_live_data.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed dates successfully")
