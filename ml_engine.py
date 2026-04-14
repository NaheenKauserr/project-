import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import silhouette_score, r2_score, accuracy_score, confusion_matrix
import streamlit as st

@st.cache_data
def auto_ml(df, column_types):
    """
    Runs suitable basic ML algorithms based on column properties.
    Returns: list of dicts with keys: 'type', 'title', 'metric_name', 'metric_value', 'figure' (or None), 'extra'
    """
    results = []
    if df is None or len(df) < 10:
        return results

    def apply_sneat_theme(fig_to_style):
        fig_to_style.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(family="Inter", color="#4b4b4b", size=12),
            title_font=dict(size=16, color="#4b4b4b", family="Inter"),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#ebe9f1"),
            yaxis=dict(showgrid=True, gridcolor="#ebe9f1", zeroline=False, linecolor="rgba(0,0,0,0)"),
        )
        return fig_to_style

    num_cols = column_types.get("numeric", [])
    cat_cols = column_types.get("categorical", [])
    bool_cols = column_types.get("boolean", [])

    # Sample data to avoid freezing
    ml_df = df.dropna().copy()
    if len(ml_df) > 5000:
        ml_df = ml_df.sample(5000)
        
    if len(ml_df) < 10:
        return results

    # 1. Clustering: >=3 numeric cols
    if len(num_cols) >= 3:
        try:
            features = num_cols[:3]
            X = ml_df[features]
            
            # Simple scaling
            X_scaled = (X - X.mean()) / X.std()
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            ml_df['Cluster'] = [str(c) for c in labels]
            
            score = silhouette_score(X_scaled, labels)
            
            fig = px.scatter(ml_df, x=features[0], y=features[1], color='Cluster',
                            color_discrete_sequence=['#7367f0', '#28c76f', '#ea5455'],
                            title=f"K-Means Clustering on {features[0]} vs {features[1]}")
            fig = apply_sneat_theme(fig)
                            
            results.append({
                'type': 'Clustering',
                'title': 'K-Means Clustering (k=3)',
                'metric_name': 'Silhouette Score',
                'metric_value': f"{score:.3f}",
                'figure': fig,
                'extra': f"Features: {', '.join(features)}"
            })
        except Exception as e:
            print(f"Clustering failed: {e}")

    # 2. Regression: >=2 numeric cols
    if len(num_cols) >= 2:
        try:
            # Let's see if we have 2 highly correlated variables to do a 1D regression
            # or just take the first as target and next 1-3 as features
            target = num_cols[0]
            features = num_cols[1:4]
            
            X = ml_df[features]
            y = ml_df[target]
            
            model = LinearRegression()
            model.fit(X, y)
            preds = model.predict(X)
            
            r2 = r2_score(y, preds)
            
            fig = None
            if len(features) == 1:
                plot_df = pd.DataFrame({
                    'Actual': y,
                    'Feature': X.iloc[:, 0],
                    'Predicted': preds
                })
                fig = px.scatter(plot_df, x='Feature', y='Actual', title=f"Regression: {target} vs {features[0]}")
                fig.update_traces(marker_color="#7367f0")
                fig.add_scatter(x=plot_df['Feature'], y=plot_df['Predicted'], mode='lines', name='Prediction', line=dict(color='#28c76f'))
                fig = apply_sneat_theme(fig)
            else:
                # Actual vs Predicted plot
                plot_df = pd.DataFrame({'Actual': y, 'Predicted': preds})
                fig = px.scatter(plot_df, x='Actual', y='Predicted', title=f"Actual vs Predicted {target}")
                fig.update_traces(marker_color="#7367f0")
                fig = apply_sneat_theme(fig)
                
            results.append({
                'type': 'Regression',
                'title': f'Linear Regression for {target}',
                'metric_name': 'R² Score',
                'metric_value': f"{r2:.3f}",
                'figure': fig,
                'extra': f"Features: {', '.join(features)}"
            })
        except Exception as e:
            pass

    # 3. Classification: Binary Target
    # Check if we have a binary column (either boolean or cat with 2 uniques)
    bin_target = None
    if len(bool_cols) > 0:
        bin_target = bool_cols[0]
    else:
        for col in cat_cols:
            if ml_df[col].nunique() == 2:
                bin_target = col
                break
                
    if bin_target and len(num_cols) >= 1:
        try:
            features = num_cols[:3]
            X = ml_df[features]
            y = ml_df[bin_target]
            
            model = LogisticRegression(max_iter=1000)
            model.fit(X, y)
            preds = model.predict(X)
            
            acc = accuracy_score(y, preds)
            cm = confusion_matrix(y, preds)
            
            fig = px.imshow(cm, text_auto=True, title=f"Confusion Matrix for {bin_target}", color_continuous_scale=[[0, '#f8f7fa'], [1, '#7367f0']])
            fig = apply_sneat_theme(fig)
            
            results.append({
                'type': 'Classification',
                'title': f'Logistic Regression for {bin_target}',
                'metric_name': 'Accuracy',
                'metric_value': f"{acc:.2%}",
                'figure': fig,
                'extra': f"Features: {', '.join(features)}"
            })
        except Exception as e:
            pass

    # 4. Feature Importance (Random Forest)
    if len(num_cols) >= 3:
        try:
            target = num_cols[0]
            features = num_cols[1:6] # up to 5 features
            
            X = ml_df[features]
            y = ml_df[target]
            
            rf = RandomForestRegressor(n_estimators=50, random_state=42)
            rf.fit(X, y)
            
            imp_df = pd.DataFrame({
                'Feature': features,
                'Importance': rf.feature_importances_
            }).sort_values(by='Importance', ascending=True)
            
            fig = px.bar(imp_df, x='Importance', y='Feature', orientation='h', 
                         title=f"Feature Drivers for {target}")
            fig.update_traces(marker_color="#a59bfa")
            fig = apply_sneat_theme(fig)
            
            top_driver = imp_df.iloc[-1]['Feature']
            
            results.append({
                'type': 'Feature Importance',
                'title': f'Key Drivers Analysis for {target}',
                'metric_name': '#1 Driving Feature',
                'metric_value': top_driver,
                'figure': fig,
                'extra': f"Analyzed {len(features)} contributing variables"
            })
        except Exception:
            pass

    return results

