

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from pathlib import Path
import joblib

# تنظیمات اصلی صفحه
st.set_page_config(
    page_title="World Cup ML Predictor",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)



import importlib
import translations
importlib.reload(translations)
from translations import TRANSLATIONS

lang = st.sidebar.selectbox("🌐 Language / Sprache / زبان", ["EN 🇬🇧", "DE 🇩🇪", "FA 🇮🇷"], index=0)
st.session_state.lang_code = lang.split()[0]

def _(text):
    if not isinstance(text, str):
        return text
    code = st.session_state.lang_code
    if code == "FA": return text
    return TRANSLATIONS.get(code, {}).get(text, text)

import os

# تعیین دقیق مسیر روت پروژه فارغ از اینکه فایل از کجا اجرا شده
BASE_DIR = Path(os.path.abspath(__file__)).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = OUTPUT_DIR / "models"
FIGURES_DIR = OUTPUT_DIR / "figures"
PREDICTIONS_DIR = OUTPUT_DIR / "predictions"

# --- توابع بارگذاری داده (استفاده از کش برای سرعت بالا) ---
def load_data():
    # بارگذاری فایل‌های پیش‌بینی
    try:
        group_standings = pd.read_csv(PREDICTIONS_DIR / "worldcup2026_predicted_group_standings.csv")
        rename_map = {'group': 'Group', 'team': 'Team', 'played': 'Played', 'wins': 'Won', 'draws': 'Drawn', 'losses': 'Lost', 'goals_for': 'GF', 'goals_against': 'GA', 'goal_difference': 'GD', 'points': 'Points'}
        group_standings = group_standings.rename(columns=rename_map)
        group_matches = pd.read_csv(PREDICTIONS_DIR / "worldcup2026_group_match_predictions.csv")
        r32_matches = pd.read_csv(PREDICTIONS_DIR / "worldcup2026_round_of_32_predictions.csv")
    except Exception:
        group_standings = group_matches = r32_matches = pd.DataFrame()
    
    # بارگذاری دیتاست اصلی برای بازیابی بازی‌های 2022 و شبیه‌ساز
    try:
        model_dataset = pd.read_csv(DATA_DIR / "model_dataset_live.csv")
        model_dataset['date'] = pd.to_datetime(model_dataset['date'].astype(str).str.split().str[0])
    except Exception:
        model_dataset = pd.DataFrame()
        
    # استخراج داده‌های واقعی جام جهانی 2026 از دل دیتابیس لایو!
    if not model_dataset.empty:
        actual_2026 = model_dataset[(model_dataset['date'] >= '2026-06-11') & (model_dataset['tournament'] == 'FIFA World Cup')].copy()
    else:
        actual_2026 = pd.DataFrame()
    
    return group_standings, group_matches, r32_matches, actual_2026, model_dataset

@st.cache_resource
def load_models():
    # بارگذاری مدل‌های ماشین لرنینگ
    try:
        model_goals_a = joblib.load(MODELS_DIR / "best_team_a_goals_model.joblib")
        model_goals_b = joblib.load(MODELS_DIR / "best_team_b_goals_model.joblib")
        model_result = joblib.load(MODELS_DIR / "best_match_result_model.joblib")
        return model_goals_a, model_goals_b, model_result
    except Exception:
        return None, None, None

# بارگذاری اولیه داده‌ها
group_standings, group_matches, r32_matches, actual_2026, model_dataset = load_data()
model_goals_a, model_goals_b, model_result = load_models()

# --- استایل‌های سفارشی CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1E3A8A; font-weight: bold; text-align: center; margin-bottom: 30px; }
    .sub-header { font-size: 1.5rem; color: #3B82F6; margin-top: 20px; border-bottom: 2px solid #3B82F6; padding-bottom: 5px; }
    .st-alert { margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)


# --- سایدبار برای ناوبری ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/3/36/2026_FIFA_World_Cup_logo.svg/1200px-2026_FIFA_World_Cup_logo.svg.png", width=150)
st.sidebar.title(_("ناوبری پروژه"))
page = st.sidebar.radio(_("یک بخش را انتخاب کنید:"), 
    [_("مقدمه و معرفی"), 
     _("تحلیل اکتشافی (EDA)"), 
     _("🧠 تحلیل پیشرفته (PCA و کلاسترینگ)"),
     _("بررسی مدل (ارزیابی فنی)"),
     _("بررسی جام جهانی 2022 (دوره قبل)"),
     _("اعتبارسنجی بازی‌های ۲۰۲۶ (از روز اول تا اکنون)"),
     _("پیش‌بینی کامل جام جهانی 2026"),
     _("شبیه‌ساز زنده مسابقات 🎮"),
     _("📝 ویرایشگر زنده داده‌ها (Google Sheet)"),
     _("📁 گالری تمامی خروجی‌ها (Archive)")]
)

st.sidebar.markdown("---")
st.sidebar.info(_("پروژه پایانی یادگیری ماشین - Educx"))

# ==========================================
# صفحات مختلف برنامه
# ==========================================

if page == _("مقدمه و معرفی"):
    st.markdown(_('<div class="main-header">پیش‌بینی جام جهانی ۲۰۲۶ با ماشین لرنینگ</div>'), unsafe_allow_html=True)
    st.write(_("سلام! به داشبورد تعاملی پروژه پیش‌بینی نتایج جام جهانی ۲۰۲۶ خوش آمدید. این پروژه به عنوان کار نهایی Educx پیاده‌سازی شده است."))
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(_('<div class="sub-header">اهداف پروژه</div>'), unsafe_allow_html=True)
        st.write(_("""
        * پیش‌بینی تعداد گل‌های هر تیم با استفاده از مدل‌های رگرسیون
        * پیش‌بینی نتیجه نهایی بازی (برد، باخت، مساوی) با مدل‌های طبقه‌بندی (Classification)
        * شبیه‌سازی کامل مرحله گروهی و حذفی جام جهانی ۲۰۲۶
        * اعتبارسنجی مدل با استفاده از نتایج واقعی مسابقات ۲۰۲۲ و مسابقات انجام شده ۲۰۲۶
        """))
    with col2:
        st.markdown(_('<div class="sub-header">تکنولوژی‌های استفاده شده</div>'), unsafe_allow_html=True)
        st.write(_("""
        * **زبان برنامه‌نویسی:** Python
        * **تحلیل داده:** Pandas, Numpy
        * **ماشین لرنینگ:** Scikit-Learn, Random Forest, XGBoost
        * **مصورسازی:** Matplotlib, Plotly, Streamlit
        """))
    
    st.info(_("👈 برای مشاهده نتایج و تحلیل‌ها، از منوی سمت چپ استفاده کنید."))

elif page == _("تحلیل اکتشافی (EDA)"):
    st.markdown(_('<div class="main-header">تحلیل اکتشافی داده‌ها (EDA)</div>'), unsafe_allow_html=True)
    st.write(_("در این بخش نگاهی به داده‌های تاریخی مسابقات فوتبال می‌اندازیم تا الگوهای موجود را درک کنیم."))
    
    tab1, tab2, tab3 = st.tabs([_("توزیع نتایج"), _("تیم‌های برتر"), _("روند زمانی")])
    
    with tab1:
        st.image(str(FIGURES_DIR / "eda_result_distribution.png"), use_column_width=True)
        st.write(_("بیشتر بازی‌های فوتبال در نهایت با برد تیم میزبان یا تیمی که روی کاغذ قوی‌تر است به پایان می‌رسند. در مسابقات بین‌المللی خنثی، این نسبت کمی متفاوت است."))
    
    with tab2:
        st.image(str(FIGURES_DIR / "eda_top_teams.png"), use_column_width=True)
        st.write(_("تیم‌هایی که بیشترین بازی را در تاریخ انجام داده‌اند."))
        
    with tab3:
        st.markdown(_('<div class="sub-header">روند تغییرات در طول زمان</div>'), unsafe_allow_html=True)
        try:
            df_plot = model_dataset.copy()
            df_plot['year'] = pd.to_datetime(df_plot['date']).dt.year
            df_plot['total_goals'] = df_plot['team_a_goals'] + df_plot['team_b_goals']
            
            matches_per_year = df_plot.groupby('year').size().reset_index(name='count')
            fig_matches = px.line(matches_per_year, x='year', y='count', markers=True, title=_("تعداد بازی‌های بین‌المللی فوتبال در هر سال"))
            st.plotly_chart(fig_matches, use_container_width=True)
            
            avg_goals = df_plot.groupby('year')['total_goals'].mean().reset_index(name='avg_goals')
            fig_goals = px.line(avg_goals, x='year', y='avg_goals', markers=True, title=_("میانگین گل در هر بازی بر اساس سال"))
            st.plotly_chart(fig_goals, use_container_width=True)
        except Exception:
            st.image(str(FIGURES_DIR / "eda_matches_per_year.png"), use_column_width=True)
            st.write(_("تعداد بازی‌های بین‌المللی فوتبال در طول زمان به شدت افزایش یافته است."))

elif page == _("بررسی مدل (ارزیابی فنی)"):
    st.markdown(_('<div class="main-header">📊 ارزیابی تخصصی مدل‌های یادگیری ماشین</div>'), unsafe_allow_html=True)
    st.write(_("در این پروژه از الگوریتم‌های مختلف ماشین لرنینگ (مانند Random Forest، XGBoost، Poisson Regression و ...) استفاده شده است. در اینجا ارزیابی و مقایسه عملکرد آن‌ها را مشاهده می‌کنید که برای ارائه کلاس یادگیری ماشین بسیار مناسب است."))
    
    tab_reg, tab_clf, tab_feat = st.tabs([_("📉 مقایسه مدل‌های رگرسیون"), _("🎯 مقایسه طبقه‌بندی (برد/باخت)"), _("🔑 مهم‌ترین ویژگی‌ها")])
    
    with tab_reg:
        st.markdown(_('<div class="sub-header">رتبه‌بندی الگوریتم‌های پیش‌بینی گل (Regression)</div>'), unsafe_allow_html=True)
        st.write(_("این نمودارها نشان می‌دهند که الگوریتم‌های درختی (Tree-based) مانند رندوم فارست چطور در مقابل رگرسیون‌های خطی کلاسیک عمل کرده‌اند. **(نمودارها کاملاً تعاملی هستند، موس را روی ستون‌ها ببرید!)**"))
        
        with st.expander(_("توضیحات ریاضی و کاربرد فوتبالی مدل‌های رگرسیون")):
            st.markdown(f"**{_('مدل Ridge Regression')}**")
            st.latex(r"\hat{g}_i = \mathbf{x}_i^T \boldsymbol{\beta}")
            st.latex(r"\text{Loss}(\boldsymbol{\beta}) = \sum_{i} (g_i - \hat{g}_i)^2 + \alpha \sum_{j} \beta_j^2")
            st.info(_(r"در این فرمول $g_i$ گل واقعی، $\hat{g}_i$ گل پیش‌بینی شده و $\beta_j$ اهمیت هر ویژگی است. جریمه $\alpha$ باعث می‌شود مدل به نویزهای فوتبال (مثل اتفاقات تصادفی) بیش از حد حساس نشود."))
            
            st.markdown(f"**{_('مدل Poisson Regression')}**")
            st.latex(r"P(G_i = k) = \frac{\lambda_i^k e^{-\lambda_i}}{k!}")
            st.info(_(r"چون تعداد گل‌ها اعداد شمارشی (۰، ۱، ۲...) هستند، این مدل فرض می‌کند گل‌ها از توزیع پواسون با نرخ $\lambda$ (متوسط گل مورد انتظار) پیروی می‌کنند."))
            
            st.markdown(f"**{_('مدل Gradient Boosting')}**")
            st.latex(r"F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \eta \cdot h_m(\mathbf{x})")
            st.info(_(r"این مدل قدم به قدم اشتباهات قبلی خود را جبران می‌کند. در فوتبال که روابط غیرخطی است (مثلاً تاثیر همزمان فرم اخیر و آمار رودررو)، این مدل بسیار عالی عمل می‌کند."))
        
        try:
            reg_table = pd.read_csv(OUTPUT_DIR / "regression_model_comparison_presentation" / "tables" / "goal_regression_model_comparison.csv")
            
            # مرتب‌سازی برای نمودارها
            reg_table_sorted_mae = reg_table.sort_values(by="mean_mae", ascending=False) # طولانی‌ترین بالا
            reg_table_sorted_r2 = reg_table.sort_values(by="mean_r2", ascending=True)  # کمترین بالا، بیشترین پایین
            
            c1, c2 = st.columns(2)
            with c1:
                fig_mae = px.bar(reg_table_sorted_mae, x="mean_mae", y="model", orientation='h', 
                                title=_("مقایسه خطای MAE (هرچه کمتر، مدل بهتر است)"),
                                text=reg_table_sorted_mae["mean_mae"].round(3),
                                color="mean_mae", color_continuous_scale="Reds")
                fig_mae.update_traces(marker_line_color='#2c3e50', marker_line_width=2, opacity=0.9)
                fig_mae.update_layout(yaxis_title=_("مدل"), xaxis_title=_("خطای میانگین قدر مطلق (MAE)"))
                st.plotly_chart(fig_mae, use_container_width=True)
                
            with c2:
                fig_r2 = px.bar(reg_table_sorted_r2, x="mean_r2", y="model", orientation='h', 
                               title=_("مقایسه امتیاز R2 (هرچه بیشتر، مدل بهتر است)"),
                               text=reg_table_sorted_r2["mean_r2"].round(3),
                               color="mean_r2", color_continuous_scale="Blues")
                fig_r2.update_traces(marker_line_color='#2c3e50', marker_line_width=2, opacity=0.9)
                fig_r2.update_layout(yaxis_title=_("مدل"), xaxis_title=_("ضریب تعیین (R2 Score)"))
                st.plotly_chart(fig_r2, use_container_width=True)
                
            # ساخت MSE از روی RMSE
            reg_table["mean_mse"] = reg_table["mean_rmse"] ** 2
            
            reg_table_sorted_rmse = reg_table.sort_values(by="mean_rmse", ascending=False)
            reg_table_sorted_mse = reg_table.sort_values(by="mean_mse", ascending=False)
            
            c3, c4 = st.columns(2)
            with c3:
                fig_rmse = px.bar(reg_table_sorted_rmse, x="mean_rmse", y="model", orientation='h', 
                                title=_("مقایسه خطای RMSE (هرچه کمتر، بهتر)"),
                                text=reg_table_sorted_rmse["mean_rmse"].round(3),
                                color="mean_rmse", color_continuous_scale="Oranges")
                fig_rmse.update_traces(marker_line_color='#2c3e50', marker_line_width=2, opacity=0.9)
                fig_rmse.update_layout(yaxis_title=_("مدل"), xaxis_title=_("جذر میانگین مربعات خطا (RMSE)"))
                st.plotly_chart(fig_rmse, use_container_width=True)
                
            with c4:
                fig_mse = px.bar(reg_table_sorted_mse, x="mean_mse", y="model", orientation='h', 
                               title=_("مقایسه خطای MSE (هرچه کمتر، بهتر)"),
                               text=reg_table_sorted_mse["mean_mse"].round(3),
                               color="mean_mse", color_continuous_scale="Purples")
                fig_mse.update_traces(marker_line_color='#2c3e50', marker_line_width=2, opacity=0.9)
                fig_mse.update_layout(yaxis_title=_("مدل"), xaxis_title=_("میانگین مربعات خطا (MSE)"))
                st.plotly_chart(fig_mse, use_container_width=True)
                
            st.write(_("جدول کامل مقایسه معیارهای خطا (MAE, RMSE, R2) برای مدل‌های مختلف:"))
            st.dataframe(reg_table, use_container_width=True)
            
            st.markdown(_('<hr><div class="sub-header">پراکندگی گل‌های واقعی در برابر پیش‌بینی‌شده (Scatter Plot)</div>'), unsafe_allow_html=True)
            st.write(_("نقاط روی نمودار پیش‌بینی‌های مدل را نشان می‌دهند. خط‌چین قرمز خط ایده‌آل (دقت ۱۰۰٪) است."))
            try:
                test_preds = pd.read_csv(OUTPUT_DIR / "regression_model_comparison_presentation" / "tables" / "best_model_test_predictions.csv")
                c_scat1, c_scat2 = st.columns(2)
                with c_scat1:
                    max_val_a = max(test_preds['team_a_goals'].max(), test_preds['pred_team_a_goals'].max())
                    fig_scat_a = px.scatter(test_preds, x='team_a_goals', y='pred_team_a_goals', opacity=0.6, 
                                            title=_("تیم میزبان (الف)"), 
                                            labels={'team_a_goals': _('گل واقعی'), 'pred_team_a_goals': _('گل پیش‌بینی شده')})
                    fig_scat_a.update_traces(marker=dict(line=dict(color='#2c3e50', width=1.5)), opacity=0.85)
                    fig_scat_a.add_shape(type="line", x0=0, y0=0, x1=max_val_a, y1=max_val_a, line=dict(color="red", dash="dash"))
                    st.plotly_chart(fig_scat_a, use_container_width=True)
                    
                with c_scat2:
                    max_val_b = max(test_preds['team_b_goals'].max(), test_preds['pred_team_b_goals'].max())
                    fig_scat_b = px.scatter(test_preds, x='team_b_goals', y='pred_team_b_goals', opacity=0.6, 
                                            title=_("تیم میهمان (ب)"), 
                                            labels={'team_b_goals': _('گل واقعی'), 'pred_team_b_goals': _('گل پیش‌بینی شده')})
                    fig_scat_b.update_traces(marker=dict(line=dict(color='#2c3e50', width=1.5)), opacity=0.85)
                    fig_scat_b.add_shape(type="line", x0=0, y0=0, x1=max_val_b, y1=max_val_b, line=dict(color="red", dash="dash"))
                    st.plotly_chart(fig_scat_b, use_container_width=True)
                    
                st.markdown(_('<hr><div class="sub-header">فضای سه‌بعدی پیش‌بینی‌ها (3D Scatter)</div>'), unsafe_allow_html=True)
                st.write(_("این یک نمودار کاملاً سه‌بعدی است. می‌توانید با استفاده از موس آن را در فضا بچرخانید!"))
                fig_3d = px.scatter_3d(test_preds, x='team_a_goals', y='team_b_goals', z='absolute_goal_error', 
                                       color='absolute_goal_error', opacity=0.9, size_max=15,
                                       title=_("نمای سه‌بعدی خطای مطلق بر اساس ترکیب گل‌های دو تیم"))
                fig_3d.update_traces(marker=dict(line=dict(color='#2c3e50', width=2)))
                st.plotly_chart(fig_3d, use_container_width=True)
            except Exception:
                st.warning(_("داده‌های پراکندگی گل‌ها یافت نشد."))
            
        except Exception:
            st.warning(_("داده‌های مقایسه رگرسیون برای رسم نمودار تعاملی یافت نشد."))

    with tab_clf:
        st.markdown(_('<div class="sub-header">دقت مدل‌های طبقه‌بندی در تشخیص برد، باخت و مساوی</div>'), unsafe_allow_html=True)
        try:
            clf_table = pd.read_csv(OUTPUT_DIR / "tables" / "classification_model_metrics.csv")
            
            df_melted = clf_table.melt(id_vars='model', value_vars=['accuracy', 'weighted_f1'], var_name=_('معیار'), value_name=_('امتیاز'))
            fig_clf = px.bar(df_melted, x='model', y=_('امتیاز'), color=_('معیار'), barmode='group', 
                             title=_("مقایسه مقادیر Accuracy و F1-Score برای مدل‌های طبقه‌بندی"),
                             text=_('امتیاز'), color_discrete_sequence=['#1f77b4', '#ff7f0e'])
            fig_clf.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            st.plotly_chart(fig_clf, use_container_width=True)
            
            st.dataframe(clf_table, use_container_width=True)
            
            st.markdown(_("**(ماتریس درهم‌ریختگی - Logistic Regression)**"))
            st.image(str(FIGURES_DIR / "classification_confusion_matrix.png"), use_column_width=True)
        except Exception:
            st.warning(_("داده‌های طبقه‌بندی یافت نشد."))

    with tab_feat:
        st.markdown(_('<div class="sub-header">ویژگی‌های کلیدی (Feature Importance)</div>'), unsafe_allow_html=True)
        st.write(_("ماشین لرنینگ یاد گرفته است که کدام پارامترها (مثل میانگین گل‌های بازی‌های اخیر، یا سابقه تقابل دو تیم) بیشترین وزن را در تعیین نتیجه بازی دارند."))
        try:
            st.image(str(OUTPUT_DIR / "regression_model_comparison_presentation" / "figures" / "15_best_model_feature_importance.png"), use_column_width=True)
        except Exception:
            try:
                st.image(str(FIGURES_DIR / "rf_feature_importance_top20.png"), use_column_width=True)
            except Exception:
                st.warning(_("تصویر Feature Importance یافت نشد."))

elif page == _("بررسی جام جهانی 2022 (دوره قبل)"):
    st.markdown(_('<div class="main-header">عملکرد مدل در جام جهانی ۲۰۲۲ قطر</div>'), unsafe_allow_html=True)
    st.write(_("برای اینکه ببینیم مدل ما چقدر خوب کار می‌کند، آن را روی مسابقات جام جهانی دوره قبل (2022) که نتایجش مشخص است، تست می‌کنیم."))
    
    if not model_dataset.empty and model_goals_a is not None:
        # فیلتر کردن داده‌های 2022
        try:
            wc2022 = pd.read_csv(DATA_DIR / 'wc2022.csv')
            wc2022['date'] = pd.to_datetime(wc2022['date'])
        except Exception:
            wc2022 = pd.DataFrame()
            
        if len(wc2022) > 0:
            with st.spinner(_("در حال محاسبه پیش‌بینی‌ها برای 64 مسابقه جام جهانی 2022...")):
                features_to_drop = ['team_a', 'team_b', 'date', 'team_a_goals', 'team_b_goals', 'result']
                X_2022 = wc2022.drop(columns=[c for c in features_to_drop if c in wc2022.columns])
                
                # پیش‌بینی
                wc2022['predicted_goals_a'] = np.round(model_goals_a.predict(X_2022)).astype(int)
                wc2022['predicted_goals_b'] = np.round(model_goals_b.predict(X_2022)).astype(int)
                
                # رفع مقادیر منفی احتمالی
                wc2022['predicted_goals_a'] = wc2022['predicted_goals_a'].apply(lambda x: max(0, x))
                wc2022['predicted_goals_b'] = wc2022['predicted_goals_b'].apply(lambda x: max(0, x))
                
                # مقایسه
                wc2022['exact_match'] = (wc2022['team_a_goals'] == wc2022['predicted_goals_a']) & (wc2022['team_b_goals'] == wc2022['predicted_goals_b'])
                
                # پیدا کردن برنده
                def get_winner(g_a, g_b):
                    if g_a > g_b: return "team_a_win"
                    elif g_b > g_a: return "team_b_win"
                    else: return "draw"
                    
                wc2022['predicted_result'] = wc2022.apply(lambda row: get_winner(row['predicted_goals_a'], row['predicted_goals_b']), axis=1)
                wc2022['result_correct'] = wc2022['result'] == wc2022['predicted_result']
                
            # نمایش نتایج کلی
            col1, col2, col3 = st.columns(3)
            col1.metric(_("تعداد مسابقات بررسی شده"), len(wc2022))
            col2.metric(_("دقت پیش‌بینی نتیجه (برد/مساوی)"), f"{(wc2022['result_correct'].mean()*100):.1f}%")
            col3.metric(_("دقت پیش‌بینی نتیجه دقیق"), f"{(wc2022['exact_match'].mean()*100):.1f}%")
            
            st.write(_("### نمونه بازی‌های پیش‌بینی شده در ۲۰۲۲"))
            display_df = wc2022[['date', 'team_a', 'team_b', 'team_a_goals', 'team_b_goals', 'predicted_goals_a', 'predicted_goals_b', 'result_correct']].tail(15).copy()
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
            display_df.columns = [_('تاریخ'), _('تیم الف'), _('تیم ب'), _('گل واقعی الف'), _('گل واقعی ب'), _('پیش‌بینی الف'), _('پیش‌بینی ب'), _('تشخیص درست برنده؟')]
            
            st.dataframe(display_df, use_container_width=True)
            
            # چارت مقایسه
            st.write(_("### مقایسه مجموع گل‌های واقعی و پیش‌بینی شده در چند بازی منتخب"))
            selected_games = wc2022.tail(15)
            fig = go.Figure()
            fig.add_trace(go.Bar(x=selected_games['team_a'] + " vs " + selected_games['team_b'], y=selected_games['team_a_goals'] + selected_games['team_b_goals'], name=_("مجموع گل واقعی"), marker_color='#1f77b4'))
            fig.add_trace(go.Bar(x=selected_games['team_a'] + " vs " + selected_games['team_b'], y=selected_games['predicted_goals_a'] + selected_games['predicted_goals_b'], name=_("مجموع گل پیش‌بینی شده"), marker_color='#ff7f0e'))
            fig.update_layout(barmode='group', xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(_("بازی‌های جام جهانی ۲۰۲۲ در فایل یافت نشد."))
    else:
        st.error(_("دیتاست مدل یا فایل‌های مدل برای ارزیابی لود نشدند."))

elif page == _("اعتبارسنجی بازی‌های ۲۰۲۶ (از روز اول تا اکنون)"):
    st.markdown(_('<div class="main-header">عملکرد مدل در بازی‌های انجام شده جام جهانی ۲۰۲۶ (زنده)</div>'), unsafe_allow_html=True)
    
    st.markdown(_("### 📊 پایگاه داده بازی‌های زنده (Live Matches)"))
    st.write(_("در جدول زیر (شبیه به گوگل‌شیت) داده‌های خامی که سیستم از آخرین بازی‌های واقعی دریافت کرده است را مشاهده می‌کنید:"))
    try:
        live_raw = pd.read_csv(BASE_DIR / "data" / "raw" / "live_new_matches.csv")
        st.dataframe(live_raw, use_container_width=True)
    except Exception:
        st.warning(_("فایل live_new_matches.csv یافت نشد."))
        
    st.markdown("---")
    st.markdown(_("### 🎯 ارزیابی پیش‌بینی‌های مدل"))
    
    if not actual_2026.empty and model_goals_a is not None:
        st.write(f"{_('در اینجا مقایسه پیش‌بینی‌های مدل ما با نتایج واقعی ')}{len(actual_2026)}{_(' مسابقه‌ای که تا امروز در جام جهانی ۲۰۲۶ برگزار شده است را مشاهده می‌کنید. (داده‌ها به صورت زنده از فایل آپدیت می‌شوند)')}")
        
        features_to_drop = ['team_a', 'team_b', 'date', 'team_a_goals', 'team_b_goals', 'result']
        X_2026 = actual_2026.drop(columns=[c for c in features_to_drop if c in actual_2026.columns])
        
        # پیش‌بینی
        actual_2026['pred_a'] = np.round(model_goals_a.predict(X_2026)).astype(int)
        actual_2026['pred_b'] = np.round(model_goals_b.predict(X_2026)).astype(int)
        
        def get_winner(g_a, g_b):
            if g_a > g_b: return "team_a_win"
            elif g_b > g_a: return "team_b_win"
            else: return "draw"
            
        actual_2026['pred_res'] = actual_2026.apply(lambda r: get_winner(r['pred_a'], r['pred_b']), axis=1)
        actual_2026['correct'] = actual_2026['result'] == actual_2026['pred_res']
        
        acc26 = actual_2026['correct'].mean() * 100
        
        col1, col2 = st.columns(2)
        col1.metric(_("تعداد بازی‌های زنده بررسی شده"), len(actual_2026))
        col2.metric(_("دقت تشخیص برنده در مسابقات ۲۰۲۶"), f"{acc26:.1f}%")
        
        display_df = actual_2026[['date', 'team_a', 'team_b', 'team_a_goals', 'team_b_goals', 'pred_a', 'pred_b', 'correct']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df.columns = [_('تاریخ'), _('تیم الف'), _('تیم ب'), _('گل واقعی الف'), _('گل واقعی ب'), _('پیش‌بینی الف'), _('پیش‌بینی ب'), _('تشخیص درست؟')]
        
        st.dataframe(display_df, use_container_width=True)
            
    else:
        st.warning(_("داده‌های بازی‌های زنده ۲۰۲۶ یافت نشد یا مدل‌ها لود نشده‌اند."))

elif page == _("پیش‌بینی کامل جام جهانی 2026"):
    st.markdown(_('<div class="main-header">پیش‌بینی کامل جام جهانی ۲۰۲۶</div>'), unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([_("مرحله گروهی (جدول رده‌بندی)"), _("مرحله حذفی (1/16 نهایی)")])
    
    with tab1:
        if not group_standings.empty:
            st.markdown(_('<div class="sub-header">جدول رده‌بندی گروه‌ها پس از شبیه‌سازی مسابقات</div>'), unsafe_allow_html=True)
            
            groups = group_standings['Group'].unique()
            selected_group = st.selectbox(_("یک گروه را انتخاب کنید:"), sorted(groups))
            
            df_group = group_standings[group_standings['Group'] == selected_group].sort_values(by=['Points', 'GD', 'GF'], ascending=False)
            
            # نمایش جدول با فرمت زیبا
            st.dataframe(df_group[['Team', 'Played', 'Won', 'Drawn', 'Lost', 'GF', 'GA', 'GD', 'Points']], use_container_width=True)
            
            # چارت امتیازی گروه
            fig = px.bar(df_group, x='Team', y='Points', color='Team', title=f"{_('امتیازات نهایی پیش‌بینی شده برای ')}{selected_group}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(_("فایل پیش‌بینی جدول گروه‌ها یافت نشد."))
            
    with tab2:
        if not r32_matches.empty:
            st.markdown(_('<div class="sub-header">پیش‌بینی مسابقات یک‌شانزدهم نهایی</div>'), unsafe_allow_html=True)
            st.dataframe(r32_matches[['team_a', 'team_b', 'predicted_team_a_goals_rounded', 'predicted_team_b_goals_rounded', 'predicted_result']], use_container_width=True)
            
            try:
                st.image(str(FIGURES_DIR / "wc2026_round_of_32_predicted_winners.png"), use_column_width=True)
            except Exception:
                pass
        else:
            st.warning(_("پیش‌بینی مراحل حذفی یافت نشد."))

elif page == _("شبیه‌ساز زنده مسابقات 🎮"):
    st.markdown(_('<div class="main-header">شبیه‌ساز زنده مسابقات جام جهانی</div>'), unsafe_allow_html=True)
    st.write(_("در این بخش می‌توانید در کلاس دو تیم را به صورت دلخواه انتخاب کنید تا مدل در لحظه نتیجه را پیش‌بینی کند!"))
    
    if not model_dataset.empty and model_goals_a is not None:
        # گرفتن لیست تیم‌ها
        teams = sorted(model_dataset['team_a'].unique().tolist())
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            team1 = st.selectbox(_("انتخاب تیم میزبان (Team A)"), teams, index=teams.index("Germany") if "Germany" in teams else 0)
        with col2:
            st.markdown("<h1 style='text-align: center; color: red; margin-top: 25px;'>VS</h1>", unsafe_allow_html=True)
        with col3:
            team2 = st.selectbox(_("انتخاب تیم میهمان (Team B)"), teams, index=teams.index("Brazil") if "Brazil" in teams else 1)
            
        if st.button(_("پیش‌بینی نتیجه 🚀"), use_container_width=True):
            if team1 == team2:
                st.error(_("لطفاً دو تیم متفاوت انتخاب کنید."))
            else:
                with st.spinner(_("مدل در حال تحلیل داده‌های تاریخی و پیش‌بینی است...")):
                    features_to_drop = ['team_a', 'team_b', 'date', 'team_a_goals', 'team_b_goals', 'result']
                    
                    t1_stats = model_dataset[model_dataset['team_a'] == team1].iloc[-1:] if len(model_dataset[model_dataset['team_a'] == team1]) > 0 else None
                    t2_stats = model_dataset[model_dataset['team_b'] == team2].iloc[-1:] if len(model_dataset[model_dataset['team_b'] == team2]) > 0 else None
                    
                    if t1_stats is not None and t2_stats is not None:
                        demo_X = t1_stats.drop(columns=[c for c in features_to_drop if c in t1_stats.columns]).copy()
                        
                        # در اینجا برخی ویژگی‌های تیمی B را برای دمو تنظیم می‌کنیم
                        for col in demo_X.columns:
                            if 'team_b' in col and col in t2_stats.columns:
                                demo_X[col] = t2_stats[col].values[0]
                        
                        goals_a = max(0, int(np.round(model_goals_a.predict(demo_X)[0])))
                        goals_b = max(0, int(np.round(model_goals_b.predict(demo_X)[0])))
                        
                        st.markdown("---")
                        st.markdown(_("<h2 style='text-align: center;'>نتیجه پیش‌بینی شده</h2>"), unsafe_allow_html=True)
                        
                        score_col1, score_col2, score_col3 = st.columns(3)
                        with score_col1:
                            st.markdown(f"<h1 style='text-align: center; color: #1E3A8A;'>{team1}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='text-align: center; font-size: 5rem;'>{goals_a}</h1>", unsafe_allow_html=True)
                        
                        with score_col2:
                            st.markdown("<h1 style='text-align: center; color: gray; margin-top: 50px;'>-</h1>", unsafe_allow_html=True)
                            
                        with score_col3:
                            st.markdown(f"<h1 style='text-align: center; color: #1E3A8A;'>{team2}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='text-align: center; font-size: 5rem;'>{goals_b}</h1>", unsafe_allow_html=True)
                            
                        if goals_a > goals_b:
                            st.success(f"{_('🏆 برنده پیش‌بینی شده: **')}{team1}**")
                        elif goals_b > goals_a:
                            st.success(f"{_('🏆 برنده پیش‌بینی شده: **')}{team2}**")
                        else:
                            st.info(_("🤝 نتیجه پیش‌بینی شده: **مساوی**"))
                    else:
                        st.error(_("اطلاعات کافی برای یکی از این تیم‌ها در دیتابیس موجود نیست."))
    else:
         st.error(_("مدل‌ها لود نشدند. نمی‌توان شبیه‌سازی زنده انجام داد."))

elif page == _("📝 ویرایشگر زنده داده‌ها (Google Sheet)"):
    st.markdown(_('<div class="main-header">📝 ویرایشگر زنده نتایج مسابقات (شبیه گوگل‌شیت)</div>'), unsafe_allow_html=True)
    st.write(_("در این صفحه می‌توانید نتایج بازی‌های جدید جام جهانی ۲۰۲۶ را درست مثل اکسل یا گوگل‌شیت به صورت دستی اضافه یا ویرایش کنید. تغییرات شما مستقیماً در دیتابیس لایو ذخیره خواهد شد!"))
    
    live_csv_path = BASE_DIR / "data" / "raw" / "live_new_matches.csv"

    try:
        df_live = pd.read_csv(live_csv_path)
    except Exception:
        df_live = pd.DataFrame(columns=['date', 'home_team', 'away_team', 'home_score', 'away_score', 'tournament', 'country', 'neutral'])
        
    edited_df = st.data_editor(df_live, num_rows="dynamic", use_container_width=True)
    
    if st.button(_("💾 ذخیره تغییرات در دیتابیس"), type="primary"):
        edited_df.to_csv(live_csv_path, index=False)
        with st.spinner(_("در حال پردازش داده‌ها و به‌روزرسانی مدل...")):
            import subprocess
            import sys
            try:
                subprocess.run([sys.executable, "src/update_live_data.py"], check=True, cwd=BASE_DIR)
                st.success(_("✅ تغییرات با موفقیت ذخیره و ویژگی‌های ماشین لرنینگ محاسبه شدند! مدل اکنون با دیتای جدید آماده است."))
                st.rerun()
            except Exception as e:
                st.error(f"Error updating model: {e}")

elif page == _("📁 گالری تمامی خروجی‌ها (Archive)"):
    st.markdown(_('<div class="main-header">📁 آرشیو کامل گراف‌ها و جداول مدل‌ها</div>'), unsafe_allow_html=True)
    st.write(_("در این بخش می‌توانید تمامی خروجی‌های تولید شده در پوشه `output` اعم از گراف‌های اختصاصی تک‌تک مدل‌ها و جداول داده‌ها را به صورت دسته‌بندی شده مشاهده کنید."))
    
    gallery_tab1, gallery_tab2 = st.tabs([_("🖼️ تصاویر و گراف‌های مدل‌ها"), _("📊 جداول داده‌ها (CSV)")])
    
    with gallery_tab1:
        st.markdown(_('<div class="sub-header">گراف‌های اختصاصی هر الگوریتم</div>'), unsafe_allow_html=True)
        figures_per_model_dir = OUTPUT_DIR / "regression_model_comparison_presentation" / "figures_per_model"
        
        if figures_per_model_dir.exists():
            model_folders = [f.name for f in figures_per_model_dir.iterdir() if f.is_dir()]
            if model_folders:
                selected_model = st.selectbox(_("یک الگوریتم را انتخاب کنید:"), model_folders)
                
                selected_model_dir = figures_per_model_dir / selected_model
                image_files = list(selected_model_dir.glob("*.png"))
                
                if image_files:
                    st.write(f"{_('نمایش **')}{len(image_files)}{_('** تصویر برای مدل `')}{selected_model}`:")
                    
                    cols = st.columns(2)
                    for i, img_path in enumerate(image_files):
                        with cols[i % 2]:
                            st.image(str(img_path), caption=img_path.name, use_column_width=True)
                else:
                    st.info(_("هیچ تصویری در این پوشه یافت نشد."))
            else:
                st.info(_("پوشه مدل‌ها خالی است."))
        else:
            st.error(_("مسیر تصاویر مدل‌ها یافت نشد."))
            
        st.markdown(_('<hr><div class="sub-header">سایر تصاویر اصلی پروژه‌</div>'), unsafe_allow_html=True)
        with st.expander(_("مشاهده سایر نمودارهای عمومی (شامل طبقه‌بندی و EDA)")):
            general_images = list(FIGURES_DIR.glob("*.png"))
            if general_images:
                cols_gen = st.columns(2)
                for i, img_path in enumerate(general_images):
                    with cols_gen[i % 2]:
                        st.image(str(img_path), caption=img_path.name, use_column_width=True)
            else:
                st.info(_("تصویری یافت نشد."))

    with gallery_tab2:
        st.markdown(_('<div class="sub-header">جستجو و نمایش جداول خروجی</div>'), unsafe_allow_html=True)
        all_csvs = list(OUTPUT_DIR.rglob("*.csv"))
        if all_csvs:
            csv_dict = {f"{f.parent.name}/{f.name}": f for f in all_csvs}
            selected_csv_key = st.selectbox(_("یک فایل CSV را برای مشاهده انتخاب کنید:"), sorted(list(csv_dict.keys())))
            
            selected_csv_path = csv_dict[selected_csv_key]
            st.write(f"{_('در حال نمایش فایل: `')}{selected_csv_path.name}`")
            try:
                df_to_show = pd.read_csv(selected_csv_path)
                st.dataframe(df_to_show, use_container_width=True)
            except Exception as e:
                st.error(f"{_('خطا در خواندن فایل: ')}{e}")
        else:
            st.info(_("هیچ فایل CSV در پوشه خروجی‌ها یافت نشد."))

elif page == _("🧠 تحلیل پیشرفته (PCA و کلاسترینگ)"):
    st.markdown(_('<div class="main-header">🧠 تحلیل پیشرفته تیم‌های جام جهانی ۲۰۲۶</div>'), unsafe_allow_html=True)
    st.write(_("در این بخش از تکنیک‌های یادگیری بدون نظارت (Unsupervised Learning) مانند PCA و t-SNE برای بصری‌سازی الگوهای پنهان در قدرت و ضعف تیم‌های ملی استفاده شده است. همچنین با استفاده از الگوریتم K-Means، تیم‌ها به دسته‌های مختلف (خوشه‌بندی) تقسیم شده‌اند."))
    
    tab_pca, tab_tsne, tab_umap, tab_kmeans = st.tabs([_("PCA (کاهش ابعاد)"), _("t-SNE (الگوهای پیچیده)"), "UMAP", "K-Means Clustering"])
    
    interactives_dir = OUTPUT_DIR / "regression_model_comparison_presentation" / "interactive_figures"
    
    with tab_pca:
        st.write(_("نمودار **تعاملی PCA**: این الگوریتم ده‌ها ویژگی ماشین‌لرنینگی تیم‌ها را ترکیب کرده تا آن‌ها را روی یک نمودار دو بعدی نشان دهد. تیم‌هایی که به هم نزدیک‌ترند، سبک بازی و قدرت مشابهی دارند."))
        with st.expander(_("📐 پشت‌صحنه ریاضیات: کاهش ابعاد (PCA)")):
            st.write(_("الگوریتم PCA با محاسبه ماتریس کوواریانس و یافتن بردارهای ویژه (Eigenvectors)، ابعاد داده‌ها را کاهش می‌دهد تا بتوانیم آن‌ها را روی نمودار دو بعدی رسم کنیم:"))
            st.latex(r"C v = \lambda v")
            st.write(_("در اینجا C ماتریس کوواریانس، $v$ بردار ویژه و $\\lambda$ مقدار ویژه است."))
        try:
            with open(interactives_dir / "16_team_profile_pca_map_interactive.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=650, scrolling=True)
        except Exception:
            st.error(_("فایل نمودار یافت نشد."))

    with tab_tsne:
        st.write(_("الگوریتم **t-SNE**: این مدل با حفظ فواصل محلی، تیم‌های هم‌سطح را بسیار دقیق‌تر از PCA در کنار هم قرار می‌دهد:"))
        with st.expander(_("توضیحات ریاضی t-SNE و UMAP")):
            st.latex(r"\text{minimize } KL(P || Q) = \sum_{i} \sum_{j} p_{ij} \log \frac{p_{ij}}{q_{ij}}")
            st.write(_(r"این روش‌ها با حفظ همسایگی‌های محلی و کمینه کردن واگرایی $KL$ کار می‌کنند."))
            st.info(_(r"در فوتبال، این یعنی تیم‌هایی که سبک بازی بسیار شبیه به هم دارند (مثلاً هر دو شدیداً دفاعی هستند) روی نقشه به هم می‌چسبند، حتی اگر در کل قدرت متفاوتی داشته باشند."))
        try:
            with open(interactives_dir / "17_team_profile_tsne_map_interactive.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=650, scrolling=True)
        except Exception:
            st.error(_("فایل نمودار یافت نشد."))

    with tab_umap:
        st.write(_("الگوریتم **UMAP**: یکی از مدرن‌ترین الگوریتم‌های کاهش ابعاد که هم ساختار محلی و هم ساختار کلی داده‌ها را حفظ می‌کند."))
        with st.expander(_("توضیحات ریاضی t-SNE و UMAP")):
            st.latex(r"\text{minimize } KL(P || Q) = \sum_{i} \sum_{j} p_{ij} \log \frac{p_{ij}}{q_{ij}}")
            st.write(_(r"این روش‌ها با حفظ همسایگی‌های محلی و کمینه کردن واگرایی $KL$ کار می‌کنند."))
            st.info(_(r"در فوتبال، این یعنی تیم‌هایی که سبک بازی بسیار شبیه به هم دارند (مثلاً هر دو شدیداً دفاعی هستند) روی نقشه به هم می‌چسبند، حتی اگر در کل قدرت متفاوتی داشته باشند."))
        try:
            with open(interactives_dir / "18_team_profile_umap_map_interactive.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=650, scrolling=True)
        except Exception:
            st.error(_("فایل نمودار یافت نشد."))

    with tab_kmeans:
        st.write(_("دسته‌بندی (**Clustering**) تیم‌ها به کمک الگوریتم K-Means بر اساس ویژگی‌های استخراج شده. در اینجا ماشین به صورت کاملاً خودکار تیم‌ها را به کلاس‌های مختلف (مثلاً مدعیان قهرمانی، تیم‌های متوسط، ضعیف) تقسیم کرده است:"))
        with st.expander(_("توضیحات ریاضی K-Means Clustering")):
            st.latex(r"\text{Objective:} \quad \min_{\mu_1, \dots, \mu_K} \sum_{k=1}^{K} \sum_{\mathbf{x}_i \in C_k} || \mathbf{x}_i - \boldsymbol{\mu}_k ||^2")
            st.write(_(r"این الگوریتم فاصله $x_i$ (پروفایل تیم) تا مرکز خوشه $\mu_k$ را کمینه می‌کند."))
            st.info(_(r"در این پروژه ۴۸ تیم جام جهانی به ۵ گروه تاکتیکی و قدرتی مختلف تقسیم شده‌اند تا بتوانیم تیم‌های هم‌سطح را شناسایی کنیم."))
        try:
            with open(interactives_dir / "19_team_clustering_kmeans_interactive.html", 'r', encoding='utf-8') as f:
                components.html(f.read(), height=650, scrolling=True)
        except Exception:
            st.error(_("فایل نمودار یافت نشد."))
