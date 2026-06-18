import json

with open('notebooks/08_final_presentation_dashboard.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # In the 2022 cell, make sure model_dataset is loaded
        if "wc2022 = pd.read_csv(DATA_DIR / 'wc2022.csv')" in source:
            if 'model_dataset = pd.read_csv(DATA_DIR / "model_dataset_live.csv")' not in source:
                new_source = source.replace(
                    "wc2022 = pd.read_csv(DATA_DIR / 'wc2022.csv')",
                    "model_dataset = pd.read_csv(DATA_DIR / \"model_dataset_live.csv\")\n    model_dataset['date'] = pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])\n    wc2022 = pd.read_csv(DATA_DIR / 'wc2022.csv')"
                )
                cell['source'] = [line + '\n' for line in new_source.split('\n')]
                
        # Fix the 2026 cell in case it still has the old code
        if "wc2026_actual = model_dataset[(model_dataset['tournament']" in source or "wc2026_actual = pd.read_csv(DATA_DIR / 'wc2026.csv')" in source:
            if "if not wc2026_actual.empty:" in source:
                # Replace the entire cell source with the clean version
                clean_2026 = """try:
    # لود کردن فایل مجزای ۲۰۲۶
    wc2026_actual = pd.read_csv(DATA_DIR / 'wc2026.csv')
    wc2026_actual['date'] = pd.to_datetime(wc2026_actual['date'])
    
    if not wc2026_actual.empty:
        X_2026 = wc2026_actual.drop(columns=[c for c in features_to_drop if c in wc2026_actual.columns])
        wc2026_actual['pred_a'] = np.round(model_goals_a.predict(X_2026)).astype(int)
        wc2026_actual['pred_b'] = np.round(model_goals_b.predict(X_2026)).astype(int)
        wc2026_actual['pred_res'] = wc2026_actual.apply(lambda r: get_winner(r['pred_a'], r['pred_b']), axis=1)
        wc2026_actual['correct'] = wc2026_actual['result'] == wc2026_actual['pred_res']
        
        acc26 = wc2026_actual['correct'].mean() * 100
        display(Markdown(f"<div style='background-color:#cce5ff; padding:10px; border-radius:5px;'><b>دقت تشخیص برنده در {len(wc2026_actual)} بازی اخیر ۲۰۲۶: {acc26:.1f}%</b></div>"))
        display(wc2026_actual[['date', 'team_a', 'team_b', 'team_a_goals', 'team_b_goals', 'pred_a', 'pred_b', 'correct']])
    else:
        print("هنوز هیچ دیتای واقعی برای جام جهانی ۲۰۲۶ در دیتابیس ثبت نشده است.")
except Exception as e:
    print("خطا در محاسبه دقت:", e)
"""
                cell['source'] = [line + '\n' for line in clean_2026.split('\n')]

with open('notebooks/08_final_presentation_dashboard.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Notebook entirely fixed on disk!")
