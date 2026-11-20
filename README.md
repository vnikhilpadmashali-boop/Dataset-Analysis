# Dataset Analysis Studio

A responsive Streamlit application for exploring CSV datasets. It includes dataset preview, data-quality checks, descriptive statistics, interactive visualizations, and a local SQLite analysis-history database.

## Features
- Upload a CSV file or load the included demonstration dataset.
- View row/column counts, data types, and sample records.
- Identify missing values and duplicate rows.
- Generate descriptive statistics for numeric columns.
- Explore numeric distributions, scatter plots, and category counts.
- Save analysis summaries in a local SQLite database.
- Responsive layout with custom CSS styling.

## Tech stack
- Python
- Streamlit
- Pandas
- Plotly
- SQLite

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

6. Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Included demo data
`data/sample_student_performance.csv` is synthetic demonstration data. It is not official VINIX data. Replace it with the official dataset if VINIX provides one, and follow any additional task instructions.

## GitHub upload
Create a public GitHub repository (unless your internship coordinator specifies otherwise), then upload:
- `app.py`
- `requirements.txt`
- `README.md`
- `data/sample_student_performance.csv`

Do not upload `analysis_history.db`, `.venv`, or `__pycache__`.

## Suggested submission summary
Developed a CSV dataset analysis application using Python and Streamlit. The application provides dataset preview, data type inspection, missing-value and duplicate checks, descriptive statistics, and interactive visualizations. SQLite is used to store analysis history. Custom CSS is applied to improve layout and responsiveness.
