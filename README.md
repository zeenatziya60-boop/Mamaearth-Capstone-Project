# Mamaearth E-commerce Data Analysis & GenAI Capstone

## Project Overview
This project analyzes Mamaearth e-commerce data using SQL, Python, and Generative AI to understand revenue trends, product category performance, customer ratings, and product returns.

## Dataset
The project uses order, customer, and product datasets covering January to June 2026.

## Tools and Technologies
- Python
- Pandas
- Matplotlib
- MySQL
- Google Colab
- Google Gemini API

## Key Findings
- Total orders analysed: 180
- Total revenue: 99,860.20 (12 orders had missing discount information; these discounts were treated as 0% for revenue calculation).
- Overall return rate: 25.00%.
- Haircare generated the highest revenue: 39,069.10.
- Skincare had the highest return rate: 31.67%.
- January 2026 had the highest monthly revenue before excluding quantity outliers: 29,582.10.
- April 2026 had the lowest monthly revenue: 9,495.30.
- Two quantity outliers were identified and flagged, not removed.
- COD orders had a 43.64% return rate, compared with 16.80% for non-COD orders.
## Project Structure
- `sql/` — Database schema, seed data, and business analysis queries
- `data/` — Source CSV files and cleaned order data
- `analysis/` — Python analysis and GenAI notebooks
- `visualizations/` — Revenue and return-rate charts
- `narrator/` — Structured findings and generated business narrative
- `README.md` — Project overview and documentation
- `requirements.txt` — Python dependencies

## GenAI Analysis
Google Gemini was used to generate a business analysis narrative based on structured findings. A numeric accuracy check was performed on seven key values.

## Recommendations
1. Investigate the reasons behind skincare returns.
2. Review Babycare customer ratings and feedback.
3. Explore ways to improve PersonalCare product visibility.

## Note
The findings and recommendations describe observed patterns in the available dataset and do not establish proven causes.
## How to Run the Project

### 1. SQL Reports

Run `sql/schema.sql` to create the tables, load the source CSV files using `sql/seed_data.sql`, and execute `sql/reports.sql` to generate the business reports. The SQL reports use all 180 raw orders.

### 2. Python Data Analysis

Install the required libraries:

```bash
pip install -r requirements.txt
```

Run the analysis and visualization scripts from the project root:

```bash
python analysis/clean_and_eda.py
python analysis/visualize.py
```

The analysis script loads the raw customer, product, and order CSV files, performs data cleaning, detects duplicate orders, analyzes returns and revenue, and generates `narrator/findings.json`. The visualization script generates the return-rate and outlier-corrected monthly revenue charts.

### 3. GenAI Narrative

To use Google Gemini, set your free-tier API key as the `GEMINI_API_KEY` environment variable, then run:

```bash
python narrator/generate_narrative.py
```

If no API key is configured, the script should use its offline fallback. The generated narrative and numeric accuracy check are saved in the `narrator/` folder.

### Reproducibility

Run the scripts in the order described above. The SQL analysis uses the raw dataset, while the Python analysis independently cleans the CSV files. The findings and narrative should be regenerated from the latest analysis outputs.
