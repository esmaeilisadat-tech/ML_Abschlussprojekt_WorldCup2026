import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import warnings
import re
warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def clean_team_name(name):
    if pd.isna(name): return name
    name = str(name).strip()
    team_map = {
        "United States": "USA", "U.S.A.": "USA", "USMNT": "USA",
        "Iran": "IR Iran", "South Korea": "Korea Republic",
        "Turkey": "Türkiye", "Cape Verde": "Cabo Verde",
        "Ivory Coast": "Côte d'Ivoire", "Cote d'Ivoire": "Côte d'Ivoire",
        "Czech Republic": "Czechia", "England": "England" # Add others if needed
    }
    return team_map.get(name, name)

def scrape_yahoo_sports_2026():
    """Scrapes the 2026 FIFA World Cup Wikipedia page for recent results."""
    url = "https://sports.yahoo.com/soccer/world-cup/scoreboard/"
    print("در حال دریافت نتایج زنده از سایت معتبر Yahoo Sports...")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        
        matches = []
        # Find all football boxes (Wikipedia uses class 'footballbox' for match results)
        boxes = soup.find_all("div", class_="footballbox")
        
        for box in boxes:
            date_th = box.find("th", class_="fdate")
            home_th = box.find("th", class_="fhome")
            score_th = box.find("th", class_="fscore")
            away_th = box.find("th", class_="faway")
            
            if date_th and home_th and score_th and away_th:
                date_str = date_th.get_text(strip=True).split(' ')[0] # naive split
                home_team = home_th.get_text(strip=True)
                away_team = away_th.get_text(strip=True)
                score_str = score_th.get_text(strip=True)
                
                # Check if match has been played (score contains numbers)
                if 'v' in score_str.lower() or not any(c.isdigit() for c in score_str):
                    continue
                    
                score_parts = score_str.split('–')
                if len(score_parts) != 2:
                    score_parts = score_str.split('-')
                    
                if len(score_parts) == 2:
                    try:
                        home_score = int(score_parts[0].strip())
                        away_score = int(re.sub(r'\D', '', score_parts[1].strip()[:2])) # remove extra chars like (a.e.t.)
                        
                        matches.append({
                            "date": pd.to_datetime("2026-06-11"), # Mocking date since Wiki dates can be complex
                            "home_team": home_team,
                            "away_team": away_team,
                            "home_score": home_score,
                            "away_score": away_score,
                            "tournament": "FIFA World Cup",
                            "country": "United States",
                            "neutral": True
                        })
                    except:
                        pass
        
        df = pd.DataFrame(matches)
        if not df.empty:
            df['home_team'] = df['home_team'].apply(clean_team_name)
            df['away_team'] = df['away_team'].apply(clean_team_name)
            return df
        return pd.DataFrame()
    except Exception as e:
        print("خطا در اسکرپ کردن ویکی‌پدیا:", e)
        return pd.DataFrame()

def result_label(home_score, away_score):
    if home_score > away_score: return "team_a_win"
    if home_score < away_score: return "team_b_win"
    return "draw"




def run_live_update():
    print("شروع پروسه آپدیت زنده...")
    
    # 1. Try to scrape
    scraped_df = scrape_yahoo_sports_2026()
    
    # 2. Check if user provided manual updates
    live_csv_path = DATA_DIR / "raw" / "live_new_matches.csv"
    manual_df = pd.DataFrame()
    if live_csv_path.exists():
        manual_df = pd.read_csv(live_csv_path)
        
    # Combine scraped and manual, preferring manual
    new_matches = pd.concat([manual_df, scraped_df]).drop_duplicates(subset=['home_team', 'away_team'])
    
    if new_matches.empty:
        print("بازی جدیدی یافت نشد.")
        # Create a copy of model_dataset to model_dataset_live just in case
        pd.read_csv(DATA_DIR / "processed" / "model_dataset.csv").to_csv(DATA_DIR / "processed" / "model_dataset_live.csv", index=False)
        return
        
    print(f"{len(new_matches)} بازی جدید پیدا شد. در حال محاسبه ویژگی‌ها...")
    
    # 3. Load historical base dataset
    model_dataset = pd.read_csv(DATA_DIR / "processed" / "model_dataset.csv")
    model_dataset['date'] = pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])
    
    # Very simple integration: we will just append the new matches with mock feature values 
    # taking the latest stats of the team from model_dataset and applying the new result.
    # Recomputing the entire 50k rows history in a live presentation is too slow.
    
    new_rows = []
    for _, row in new_matches.iterrows():
        t1 = row['home_team']
        t2 = row['away_team']
        
        t1_stats = model_dataset[model_dataset['team_a'] == t1].iloc[-1:] if len(model_dataset[model_dataset['team_a'] == t1]) > 0 else None
        t2_stats = model_dataset[model_dataset['team_b'] == t2].iloc[-1:] if len(model_dataset[model_dataset['team_b'] == t2]) > 0 else None
        
        if t1_stats is not None and t2_stats is not None:
            new_row = t1_stats.copy()
            new_row['date'] = pd.to_datetime(row['date'])
            new_row['team_b'] = t2
            new_row['team_a_goals'] = row['home_score']
            new_row['team_b_goals'] = row['away_score']
            new_row['result'] = result_label(row['home_score'], row['away_score'])
            new_row['tournament'] = row['tournament']
            new_row['neutral'] = row['neutral']
            
            # Transfer team b stats
            for col in new_row.columns:
                if 'team_b' in col and col not in ['team_b', 'team_b_goals']:
                    new_row[col] = t2_stats[col].values[0]
                    
            new_rows.append(new_row)
            
    if new_rows:
        updated_dataset = pd.concat([model_dataset, pd.concat(new_rows)]).reset_index(drop=True)
        updated_dataset.to_csv(DATA_DIR / "processed" / "model_dataset_live.csv", index=False)
        print("✅ دیتابیس زنده (model_dataset_live.csv) با موفقیت آپدیت شد!")
    else:
        print("هیچ دیتای جدیدی اضافه نشد.")
        model_dataset.to_csv(DATA_DIR / "processed" / "model_dataset_live.csv", index=False)

if __name__ == "__main__":
    run_live_update()
