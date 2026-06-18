from pathlib import Path
import pandas as pd
import numpy as np
import re


def read_table(path: Path) -> pd.DataFrame:
    """Read a CSV or Excel file with robust CSV parsing."""
    suffix = path.suffix.lower()

    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)

    if suffix == ".csv":
        read_attempts = [
            {"sep": None, "engine": "python", "encoding": "utf-8-sig"},
            {"sep": ";", "engine": "python", "encoding": "utf-8-sig"},
            {"sep": ",", "engine": "python", "encoding": "utf-8-sig"},
            {"sep": "\t", "engine": "python", "encoding": "utf-8-sig"},
            {"sep": "|", "engine": "python", "encoding": "utf-8-sig"},
            {"sep": None, "engine": "python", "encoding": "latin1"},
            {"sep": ";", "engine": "python", "encoding": "latin1"},
            {"sep": ",", "engine": "python", "encoding": "latin1"},
        ]

        last_error = None

        for kwargs in read_attempts:
            try:
                df = pd.read_csv(path, **kwargs)
                if df.shape[1] >= 2:
                    return df
            except Exception as error:
                last_error = error

        try:
            return pd.read_csv(
                path,
                sep=None,
                engine="python",
                encoding="utf-8-sig",
                on_bad_lines="skip"
            )
        except Exception:
            raise last_error

    raise ValueError(f"Unsupported file type: {path}")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names."""
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df


def find_col(df: pd.DataFrame, candidates):
    """Find the first matching column from a candidate list."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def clean_team_name(name):
    """Normalize selected country and team names."""
    if pd.isna(name):
        return name

    name = str(name).strip()

    team_map = {
        "United States": "USA",
        "United States of America": "USA",
        "U.S.A.": "USA",
        "USMNT": "USA",

        "Iran": "IR Iran",
        "IR Iran": "IR Iran",

        "South Korea": "Korea Republic",
        "Korea Republic": "Korea Republic",

        "Turkey": "Türkiye",
        "Türkiye": "Türkiye",

        "Cape Verde": "Cabo Verde",
        "Cabo Verde": "Cabo Verde",

        "Ivory Coast": "Côte d'Ivoire",
        "Cote d'Ivoire": "Côte d'Ivoire",
        "Côte d'Ivoire": "Côte d'Ivoire",

        "Czech Republic": "Czechia",
        "Czechia": "Czechia",
    }

    return team_map.get(name, name)


def result_label(home_score, away_score):
    """Create a match result label."""
    if pd.isna(home_score) or pd.isna(away_score):
        return np.nan

    if home_score > away_score:
        return "home_win"

    if home_score < away_score:
        return "away_win"

    return "draw"


def split_teams_value(value):
    """Split a fixture teams string into two teams."""
    if pd.isna(value):
        return np.nan, np.nan

    text = str(value).strip()

    separators = [
        r"\s+vs\.?\s+",
        r"\s+v\s+",
        r"\s+VS\s+",
        r"\s+Vs\s+",
        r"\s*-\s*",
        r"\s+–\s+",
        r"\s+—\s+",
    ]

    for sep in separators:
        parts = re.split(sep, text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()

    return text, np.nan


def standardize_matches(all_matches: pd.DataFrame) -> pd.DataFrame:
    """Create a standardized historical match dataset."""
    df = normalize_columns(all_matches)

    col_map = {
        "date": ["date", "match_date", "datetime"],
        "home_team": ["home_team", "home", "team_home", "home_team_name", "team1", "team_1"],
        "away_team": ["away_team", "away", "team_away", "away_team_name", "team2", "team_2"],
        "home_score": ["home_score", "home_goals", "score_home", "home_team_score", "team1_score", "team_1_score"],
        "away_score": ["away_score", "away_goals", "score_away", "away_team_score", "team2_score", "team_2_score"],
        "tournament": ["tournament", "competition", "event"],
        "city": ["city"],
        "country": ["country", "location_country"],
        "neutral": ["neutral", "is_neutral"],
    }

    out = pd.DataFrame()

    for target, candidates in col_map.items():
        found = find_col(df, candidates)
        out[target] = df[found] if found else np.nan

    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    out["home_score"] = pd.to_numeric(out["home_score"], errors="coerce")
    out["away_score"] = pd.to_numeric(out["away_score"], errors="coerce")

    out = out.dropna(subset=["date", "home_team", "away_team"])
    out["home_team_clean"] = out["home_team"].apply(clean_team_name)
    out["away_team_clean"] = out["away_team"].apply(clean_team_name)
    out["result"] = out.apply(lambda r: result_label(r["home_score"], r["away_score"]), axis=1)
    out = out.sort_values("date").reset_index(drop=True)

    return out


def standardize_fixtures(fixtures: pd.DataFrame) -> pd.DataFrame:
    """Create a standardized fixture dataset."""
    df = normalize_columns(fixtures)

    col_map = {
        "match_no": ["match_no", "match_number", "match", "no", "id"],
        "date": ["date", "match_date", "datetime"],
        "stage": ["stage", "round", "phase"],
        "group": ["group", "group_name", "grp"],
        "team_a": ["team_a", "team1", "team_1", "home_team", "home", "team_a_name"],
        "team_b": ["team_b", "team2", "team_2", "away_team", "away", "team_b_name"],
        "teams": ["teams", "fixture", "match_teams"],
        "venue": ["venue", "stadium"],
        "city": ["city"],
        "country": ["country", "host_country"],
    }

    out = pd.DataFrame()

    for target, candidates in col_map.items():
        found = find_col(df, candidates)
        out[target] = df[found] if found else np.nan

    if out["team_a"].isna().all() and out["team_b"].isna().all() and not out["teams"].isna().all():
        split_pairs = out["teams"].apply(split_teams_value)
        out["team_a"] = split_pairs.apply(lambda x: x[0])
        out["team_b"] = split_pairs.apply(lambda x: x[1])

    out["date"] = pd.to_datetime(out["date"], errors="coerce")

    for col in ["stage", "group", "team_a", "team_b", "venue", "city", "country"]:
        out[col] = out[col].astype(str).str.strip()

    out = out[
        (out["team_a"].str.lower() != "nan") &
        (out["team_b"].str.lower() != "nan") &
        (out["team_a"] != "") &
        (out["team_b"] != "")
    ].copy()

    out["team_a_clean"] = out["team_a"].apply(clean_team_name)
    out["team_b_clean"] = out["team_b"].apply(clean_team_name)
    out["neutral"] = True

    keep_cols = [
        "match_no", "date", "stage", "group",
        "team_a", "team_b", "team_a_clean", "team_b_clean",
        "venue", "city", "country", "neutral"
    ]

    return out[keep_cols].reset_index(drop=True)


def create_teams_from_fixtures(fixtures: pd.DataFrame) -> pd.DataFrame:
    """Extract the participating teams from the fixture table."""
    a = fixtures[["team_a", "team_a_clean", "group"]].rename(
        columns={"team_a": "team", "team_a_clean": "team_clean"}
    )
    b = fixtures[["team_b", "team_b_clean", "group"]].rename(
        columns={"team_b": "team", "team_b_clean": "team_clean"}
    )

    teams = pd.concat([a, b], ignore_index=True)
    teams = teams.drop_duplicates().sort_values(["group", "team"]).reset_index(drop=True)

    return teams


def create_h2h_summary(fixtures: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Create head-to-head statistics for each fixture."""
    rows = []

    for _, f in fixtures.iterrows():
        team_a = f["team_a_clean"]
        team_b = f["team_b_clean"]

        h2h = matches[
            (
                (matches["home_team_clean"] == team_a) &
                (matches["away_team_clean"] == team_b)
            ) |
            (
                (matches["home_team_clean"] == team_b) &
                (matches["away_team_clean"] == team_a)
            )
        ].copy()

        team_a_wins = 0
        team_b_wins = 0
        draws = 0
        goals_a = 0
        goals_b = 0

        for _, m in h2h.iterrows():
            if m["home_team_clean"] == team_a:
                a_score = m["home_score"]
                b_score = m["away_score"]
            else:
                a_score = m["away_score"]
                b_score = m["home_score"]

            if pd.isna(a_score) or pd.isna(b_score):
                continue

            goals_a += a_score
            goals_b += b_score

            if a_score > b_score:
                team_a_wins += 1
            elif a_score < b_score:
                team_b_wins += 1
            else:
                draws += 1

        rows.append({
            "match_no": f.get("match_no", np.nan),
            "date": f.get("date", np.nan),
            "stage": f.get("stage", np.nan),
            "group": f.get("group", np.nan),
            "team_a": f["team_a"],
            "team_b": f["team_b"],
            "team_a_clean": team_a,
            "team_b_clean": team_b,
            "h2h_matches": len(h2h),
            "team_a_h2h_wins": team_a_wins,
            "draws": draws,
            "team_b_h2h_wins": team_b_wins,
            "team_a_h2h_goals": goals_a,
            "team_b_h2h_goals": goals_b,
            "team_a_avg_h2h_goals": goals_a / len(h2h) if len(h2h) else 0,
            "team_b_avg_h2h_goals": goals_b / len(h2h) if len(h2h) else 0,
        })

    return pd.DataFrame(rows)
