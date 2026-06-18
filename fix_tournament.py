import json

with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("== 'FIFA World Cup'", "in ['World Cup', 'FIFA World Cup']")

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed tournament names successfully")
