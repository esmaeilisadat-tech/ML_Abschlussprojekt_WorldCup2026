import json
import re

with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            # Replace !pip with %pip
            line = line.replace('!pip install', '%pip install')
            
            # Remove unused plotly imports
            if 'import plotly.express as px' in line or 'import plotly.graph_objects as go' in line:
                continue
                
            # Fix single line ifs
            if line.strip().startswith('if pd.isna(name): return name'):
                new_source.append('    if pd.isna(name):\n')
                new_source.append('        return name\n')
                continue
            if line.strip().startswith('if home_score > away_score: return "team_a_win"'):
                new_source.append('    if home_score > away_score:\n')
                new_source.append('        return "team_a_win"\n')
                continue
            if line.strip().startswith('if home_score < away_score: return "team_b_win"'):
                new_source.append('    if home_score < away_score:\n')
                new_source.append('        return "team_b_win"\n')
                continue
                
            # Fix bare except
            if line.strip() == 'except: pass':
                new_source.append('                    except Exception:\n')
                new_source.append('                        pass\n')
                continue
                
            # Fix unused e in except Exception as e:
            if line.strip() == 'except Exception as e:':
                line = line.replace('except Exception as e:', 'except Exception:')
                
            # Fix f-string without placeholders
            if 'print(f"✅ {len(df_new)}' not in line and 'print(f"' in line:
                line = re.sub(r'print\(f"([^"{}]*)"\)', r'print("\1")', line)
                
            # Fix empty f-string (the warning says f-string without placeholders at col 26)
            # Actually, let's just do a generic replace for empty f-strings:
            line = re.sub(r'f"([^"{}]*)"', r'"\1"', line)
            line = re.sub(r"f'([^'{}]*)'", r"'\1'", line)
            
            new_source.append(line)
            
        cell['source'] = new_source

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook cleaned!")
