import json
import traceback
import sys

def main():
    try:
        with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
            nb = json.load(f)
            
        for i, cell in enumerate(nb['cells']):
            if 'outputs' in cell:
                for out in cell['outputs']:
                    if out.get('output_type') == 'error':
                        print(f"Cell {i} Error:", out.get('ename'), out.get('evalue'))
                        for line in out.get('traceback', []):
                            print(line)
                            
                    elif out.get('output_type') == 'stream':
                        text = "".join(out.get('text', []))
                        if 'error' in text.lower() or 'traceback' in text.lower() or 'exception' in text.lower() or 'خطا' in text:
                            print(f"Cell {i} Output:", text)
                            
    except Exception as e:
        print("Failed to read notebook:", e)

if __name__ == '__main__':
    main()
