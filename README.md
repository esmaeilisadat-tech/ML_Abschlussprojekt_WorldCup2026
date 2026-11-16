# FIFA World Cup 2026: Match Outcome Prediction and Team Analysis

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://mlabschlussprojektworldcup2026-nry5tgeappwr4jbmjnxtmjg.streamlit.app/)
[![scikit-learn | XGBoost | LightGBM](https://img.shields.io/badge/ML-scikit--learn%20%7C%20XGBoost%20%7C%20LightGBM-orange.svg)](#models-and-results)

Final machine learning project (educx Data Science & AI training) that predicts FIFA World Cup 2026 match outcomes and scores, simulates the group stage and round of 32, and checks the predictions against real tournament results. All results are shown in an interactive Streamlit dashboard in English, German and Persian.

**Live demo:** [Open the Streamlit dashboard](https://mlabschlussprojektworldcup2026-nry5tgeappwr4jbmjnxtmjg.streamlit.app/). The free Streamlit tier puts inactive apps to sleep. If it does, click "Wake up" and wait about a minute.

## What the project does

1. **Data preparation:** cleans historical international match data and builds team-strength features for the 48 qualified teams.
2. **Outcome classification:** predicts win / draw / loss with Logistic Regression and Random Forest, and compares both against a majority-class baseline.
3. **Goal regression:** predicts goals per team with Poisson, Ridge, Random Forest, Gradient Boosting, XGBoost and LightGBM regressors, compared against a mean baseline.
4. **Tournament simulation:** predicts group standings, the best third-placed teams and the round-of-32 winners.
5. **Team profiling:** groups teams by playing profile with PCA, t-SNE, UMAP and K-Means.
6. **Real-world validation:** compares the predictions with the first completed World Cup 2026 matches.

## Models and results

**Outcome classification (held-out test set)**

| Model | Accuracy | Weighted F1 |
|---|---:|---:|
| Random Forest Classifier | 0.641 | 0.614 |
| Logistic Regression | 0.624 | 0.622 |
| Majority-class baseline | 0.582 | 0.428 |

**Validation on 12 completed World Cup 2026 matches**

| Model | Outcome accuracy | Total-goals MAE |
|---|---:|---:|
| Mean baseline | 0.58 | 1.61 |
| Poisson Regression | 0.58 | 1.95 |
| Ridge Regression | 0.58 | 2.14 |
| XGBoost Regressor | 0.58 | 2.21 |
| Random Forest Regressor | 0.50 | 2.38 |

**Interpretation:** the classifiers beat the majority baseline by about 4 to 6 accuracy points. On the small real-tournament sample, no regression model beat the simple mean baseline for goal error. Twelve matches are too few to draw strong conclusions, but the result shows how hard exact-score prediction is and why a baseline comparison matters. Full tables are in [`output/tables`](output/tables) and [`output/actual_worldcup2026_validation`](output/actual_worldcup2026_validation).

## Project structure

```text
├── app/          # Streamlit dashboard and EN/DE/FA translations
├── data/         # Match and team datasets used for training and prediction
├── notebooks/    # EDA, feature engineering, model training, simulation, validation
├── output/       # Trained models (.joblib), result tables and interactive figures
├── src/          # Data preparation and data update scripts
└── requirements.txt
```

## Run locally

```bash
git clone https://github.com/esmaeilisadat-tech/ML_Abschlussprojekt_WorldCup2026.git
cd ML_Abschlussprojekt_WorldCup2026
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The dashboard opens at http://localhost:8501.

## Author

**Mahdieh Sadat Esmaeili**: [GitHub](https://github.com/esmaeilisadat-tech) · [LinkedIn](https://www.linkedin.com/in/esmaeilisadat/)
