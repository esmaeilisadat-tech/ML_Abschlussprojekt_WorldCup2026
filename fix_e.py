import json
import re

with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for i, line in enumerate(cell['source']):
            # if this line has "except Exception:" and the next few lines use "e"
            if 'except Exception:' in line:
                # peek ahead
                uses_e = False
                for j in range(i+1, min(i+5, len(cell['source']))):
                    if ', e)' in cell['source'][j] or ' e ' in cell['source'][j]:
                        uses_e = True
                        break
                if uses_e:
                    line = line.replace('except Exception:', 'except Exception as e:')
            new_source.append(line)
        cell['source'] = new_source

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Fixed e undefined error")
