import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "analysis_history.db"

st.set_page_config(page_title="Dataset Analysis Studio", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f6f8ff 0%, #eef4fb 100%); }
    .block-container { padding-top: 2rem; max-width: 1250px; }
    .hero { padding: 1.5rem 1.7rem; border-radius: 18px; color: white;
            background: linear-gradient(110deg, #172554, #2563eb); margin-bottom: 1rem; }
    .hero h1 { color: white; margin: 0; }
    .hero p { color: #dbeafe; margin: .45rem 0 0 0; }
    div[data-testid="stMetric"] { background: white; border: 1px solid #e2e8f0;
        padding: 14px; border-radius: 14px; box-shadow: 0 3px 12px #0f172a0a; }
    .section-note { color: #475569; font-size: .95rem; }
</style>
""", unsafe_allow_html=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                missing_cells INTEGER NOT NULL,
                duplicate_rows INTEGER NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_analysis(file_name, data):
    missing = int(data.isna().sum().sum())
    duplicates = int(data.duplicated().sum())
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO analysis_history
            (file_name, row_count, column_count, missing_cells, duplicate_rows)
            VALUES (?, ?, ?, ?, ?)""",
            (file_name, len(data), len(data.columns), missing, duplicates)
        )

init_db()

st.markdown("""
<div class="hero">
  <h1>📊 Dataset Analysis Studio</h1>
  <p>Explore data quality, summary statistics, and visual patterns in one place.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📁 Dataset")
    uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
    st.caption("No dataset? Use the included student performance demo dataset.")
    demo_path = APP_DIR / "data" / "sample_student_performance.csv"
    use_demo = st.button("Load demo dataset", use_container_width=True)
    st.divider()
    st.caption("Analysis history is stored locally in SQLite.")

if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
    st.session_state.file_name = ""

if uploaded is not None:
    try:
        st.session_state.dataframe = pd.read_csv(uploaded)
        st.session_state.file_name = uploaded.name
    except Exception as exc:
        st.error(f"Could not read this CSV file: {exc}")

if use_demo:
    st.session_state.dataframe = pd.read_csv(demo_path)
    st.session_state.file_name = demo_path.name

data = st.session_state.dataframe

if data is None:
    st.info("Upload a CSV file or choose **Load demo dataset** in the sidebar to begin.")
    st.subheader("What this application provides")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 🔎 Data overview\nRows, columns, data types, and sample records.")
    c2.markdown("### 🧹 Data quality\nMissing values and duplicate-row checks.")
    c3.markdown("### 📈 Visual insights\nInteractive charts and summary statistics.")
    st.stop()

if data.empty:
    st.warning("The selected CSV has no rows. Please upload a dataset containing records.")
    st.stop()

st.subheader(f"Analysis: {st.session_state.file_name}")
st.markdown('<p class="section-note">Review the dataset, check its quality, and explore its columns.</p>', unsafe_allow_html=True)

rows, cols = data.shape
missing_cells = int(data.isna().sum().sum())
duplicate_rows = int(data.duplicated().sum())
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total rows", f"{rows:,}")
m2.metric("Total columns", f"{cols:,}")
m3.metric("Missing cells", f"{missing_cells:,}")
m4.metric("Duplicate rows", f"{duplicate_rows:,}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Dataset Preview", "Data Quality", "Statistics", "Visualizations", "History"]
)

with tab1:
    st.write("First records")
    st.dataframe(data.head(20), use_container_width=True)
    st.write("Column information")
    info = pd.DataFrame({
        "Column": data.columns,
        "Data type": [str(dtype) for dtype in data.dtypes],
        "Non-null values": [int(data[col].notna().sum()) for col in data.columns]
    })
    st.dataframe(info, use_container_width=True)

with tab2:
    st.write("Missing values by column")
    missing = data.isna().sum().rename("Missing values").to_frame()
    missing["Missing percent"] = (missing["Missing values"] / len(data) * 100).round(2)
    st.dataframe(missing, use_container_width=True)
    st.write(f"Duplicate rows detected: **{duplicate_rows}**")
    if missing_cells == 0 and duplicate_rows == 0:
        st.success("No missing cells or duplicate rows were detected.")
    else:
        st.warning("Review the quality table before using this dataset for modelling.")

with tab3:
    numeric = data.select_dtypes(include="number")
    if numeric.empty:
        st.info("No numeric columns are available for descriptive statistics.")
    else:
        st.dataframe(numeric.describe().T.round(2), use_container_width=True)

with tab4:
    numeric_cols = data.select_dtypes(include="number").columns.tolist()
    all_cols = data.columns.tolist()
    if numeric_cols:
        chosen = st.selectbox("Choose a numeric column", numeric_cols)
        fig = px.histogram(data, x=chosen, title=f"Distribution of {chosen}", marginal="box")
        st.plotly_chart(fig, use_container_width=True)
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("X-axis", numeric_cols, index=0, key="x_axis")
            y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="y_axis")
            scatter = px.scatter(data, x=x_col, y=y_col, color=all_cols[-1] if data[all_cols[-1]].nunique() <= 12 and data[all_cols[-1]].dtype == "object" else None,
                                 title=f"{y_col} vs {x_col}")
            st.plotly_chart(scatter, use_container_width=True)
    else:
        st.info("Add numeric columns to the CSV to create numeric charts.")
    categorical = data.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical:
        cat = st.selectbox("Choose a category column", categorical)
        counts = data[cat].fillna("Missing").value_counts().reset_index()
        counts.columns = [cat, "Count"]
        st.plotly_chart(px.bar(counts, x=cat, y="Count", title=f"Count by {cat}"), use_container_width=True)

with tab5:
    st.write("Saved analysis runs (SQLite database)")
    with sqlite3.connect(DB_PATH) as conn:
        history = pd.read_sql_query("SELECT * FROM analysis_history ORDER BY analyzed_at DESC", conn)
    if history.empty:
        st.caption("No saved runs yet. Click the button below to save this analysis.")
    else:
        st.dataframe(history, use_container_width=True)
    if st.button("Save this analysis to history", type="primary"):
        save_analysis(st.session_state.file_name, data)
        st.success("Analysis summary saved to the local SQLite database.")
        st.rerun()

st.caption("Note: This is a demonstration project. Use the official internship dataset and exact instructions if VINIX provides them.")
