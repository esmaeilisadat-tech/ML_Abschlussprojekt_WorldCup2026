# 🏆 FIFA World Cup 2026 - Machine Learning Predictions & Tactical Analysis

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn%20%7C%20XGBoost-orange.svg)]()

A comprehensive Data Science and Machine Learning project analyzing and predicting the outcomes of the **FIFA World Cup 2026**. This project features a fully interactive, tri-lingual (English, German, Persian) web dashboard built with Streamlit.



## 🔴 Live Demo
[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mlabschlussprojektworldcup2026-nry5tgeappwr4jbmjnxtmjg.streamlit.app/)

**Click the badge above to interact with the live Machine Learning Dashboard!**
## 🌟 Key Features
* **🏆 Predictive Modeling**: Advanced Regression and Classification models (Random Forest, XGBoost, Poisson Regression) to predict exact match scores and winners.
* **🧠 Unsupervised Learning**: Deep tactical analysis of teams using PCA, t-SNE, UMAP, and K-Means Clustering to group teams by playstyle and strength.
* **🌍 Tri-lingual Interface**: Instantly switch the entire dashboard and all mathematical explanations between 🇬🇧 English, 🇩🇪 Deutsch, and 🇮🇷 Persian.
* **📊 Interactive Visualizations**: Plotly-powered interactive maps, correlation heatmaps, and residual plots.
* **📐 Mathematical Transparency**: Every ML model comes with an interactive $ formula block explaining the math behind it in football terms!

## 📂 Project Structure
`	ext
├── app/                  # Streamlit dashboard and multi-language translations
├── data/                 # FIFA datasets used for training and predictions
├── notebooks/            # Jupyter notebooks for EDA and model training
├── output/               # Trained models (.joblib), tables, and interactive figures
├── src/                  # Python scripts for data preparation and pipeline execution
└── Mathematical_Analysis_and_Notebook_Explanation_LaTeX.pdf  # Comprehensive mathematical documentation
`

## 🚀 How to Run Locally

1. **Clone the repository**:
   `ash
   git clone https://github.com/esmaeilisadat-tech/ML_Abschlussprojekt_WorldCup2026.git
   cd ML_Abschlussprojekt_WorldCup2026
   `

2. **Install requirements** (ensure you have Python 3.11+):
   `ash
   pip install -r requirements.txt
   `
   *(Note: If 
equirements.txt is missing, standard packages are pandas, numpy, scikit-learn, xgboost, lightgbm, plotly, streamlit, umap-learn)*

3. **Run the Dashboard**:
   `ash
   streamlit run app/streamlit_app.py
   `
   *The application will open in your default browser at http://localhost:8501.*

## 👨‍💻 Author
**esmaeilisadat-tech**  
Email: [esmaeili.sadat@gmail.com](mailto:esmaeili.sadat@gmail.com)
