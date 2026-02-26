# 🍕 ABC & XYZ Restaurant Chain Merger Analysis

> **An end-to-end data analytics project** — data cleaning, SQL database, interactive dashboard, automated reporting, and AI-powered revenue forecasting.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey?logo=sqlite)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![Prophet](https://img.shields.io/badge/Prophet-Forecasting-orange)
![PowerPoint](https://img.shields.io/badge/PowerPoint-Auto--Generated-blue?logo=microsoft)

---

## 📌 Project Overview

This project analyses the merger of two fictional fast-casual restaurant chains — **ABC** and **XYZ** — using real-world data analytics techniques. As the lead analyst, I built a complete analytics pipeline from raw Excel files to an AI-powered interactive dashboard and automated business reports.

The project was designed to answer four key stakeholder questions:

| Stakeholder | Question |
|---|---|
| 💰 Finance | Which chain is more profitable? |
| 📣 Marketing | Who are our customers and when do they spend? |
| 🛒 Sales | Which products sell best and which should be removed? |
| 💻 IT | What data quality issues exist and how do we fix them? |

---

## 🎯 Key Findings

- 📊 **Combined revenue: $161M** across 40,000 transactions and 544 locations
- 🏆 **Pizza and Salads** are the most profitable categories ($33M and $31M respectively)
- 🌍 **Florida, New York and California** generate 49% of total profit
- 🌸 **Spring** is the peak season ($105M) — Fall is the weakest ($4M)
- 🚀 **12-month forecast** projects continued growth into 2026
- ⚠️ **9.76% of ABC records** had corrupted dates — identified and documented

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python (Pandas, NumPy) | Data cleaning & transformation |
| SQLite | Relational database storage |
| Matplotlib & Seaborn | Static chart generation |
| Plotly | Interactive dashboard charts |
| Streamlit | Live interactive web dashboard |
| Prophet (Meta) | Machine learning revenue forecasting |
| python-docx | Automated Word report generation |
| PptxGenJS | Automated PowerPoint generation |

---

## 📁 Project Structure

```
Restruant_Project/
│
├── raw/                          ← Original Excel files (ABC.xlsx, XYZ.xlsx)
│
├── data/                         ← Cleaned data and databases
│   ├── abc_2025.csv
│   ├── xyz_2025.csv
│   ├── merged_2025.csv
│   └── restaurant_2025.db
│
├── script/                       ← All Python and JS scripts
│   ├── 01_clean_and_merge.py     ← Data cleaning pipeline
│   ├── 02_load_database.py       ← SQLite database loader
│   ├── 03_analysis.py            ← Exploratory analysis & charts
│   ├── 04_generate_report.py     ← Auto Word report (original)
│   ├── 05_generate_pptx.js       ← Auto PowerPoint (original)
│   ├── 06_dashboard.py           ← Streamlit interactive dashboard
│   ├── 07a_generate_2025_data.py ← 2024-2025 dataset generator
│   ├── 07b_forecasting.py        ← Prophet forecasting model
│   ├── 08_update_report.py       ← Updated Word report (2025)
│   └── 09_update_pptx.js         ← Updated PowerPoint (2025)
│
├── outputs/                      ← All deliverables
│   ├── charts/                   ← 14 PNG visualizations
│   ├── Part_One_Report.docx      ← Word report (auto-generated)
│   ├── Part_Two_Presentation.pptx← PowerPoint (auto-generated)
│   └── revenue_forecast_2025_2026.csv
│
├── screenshots/                  ← Dashboard & chart previews
│
├── README.md                     ← This file
└── LICENSE                       ← Copyright © 2025 Assumpta Nwadinigwe
```

---

## 🚀 How to Run This Project

### 1. Install Dependencies
```bash
pip install pandas numpy openpyxl matplotlib seaborn plotly streamlit prophet python-docx
npm install -g pptxgenjs
```

### 2. Clean & Merge Data
```bash
python script/01_clean_and_merge.py
```

### 3. Load Database
```bash
python script/02_load_database.py
```

### 4. Generate Charts
```bash
python script/03_analysis.py
```

### 5. Generate Updated 2024-2025 Dataset
```bash
python script/07a_generate_2025_data.py
```

### 6. Run Revenue Forecasting
```bash
python script/07b_forecasting.py
```

### 7. Generate Word Report
```bash
python script/08_update_report.py
```

### 8. Generate PowerPoint
```bash
node script/09_update_pptx.js
```

### 9. Launch Interactive Dashboard
```bash
streamlit run script/06_dashboard.py
```
Then open `http://localhost:8501` in your browser.

---

## 📊 Dashboard Features

The Streamlit dashboard has **4 interactive pages:**

| Page | Features |
|---|---|
| 🏠 Overview | KPI cards, revenue trend, seasonal chart, gender split |
| 📦 Products | Best/worst sellers, category profitability, full data table |
| 🗺️ Regional | Top states by profit, ABC vs XYZ by region |
| 🤖 AI Query | Type any question in plain English and get data + chart |

All charts support **live filtering** by chain, season, gender and purchase method.

---

## 📈 Revenue Forecast

Using **Facebook Prophet**, the model was trained on 18 months of historical data and projects the next 12 months of revenue:

- Forecast period: **July 2025 – June 2026**
- Model type: Multiplicative seasonality
- Confidence interval: 95%
- Spring 2026 projected as peak revenue period

---

## 🧹 Data Quality Issues Found & Fixed

| Issue | Dataset | Rows Affected | Action Taken |
|---|---|---|---|
| Corrupted dates (1970 epoch) | ABC | 1,952 (9.76%) | Set to NaT, documented |
| 100% null cost column | XYZ | 20,000 (100%) | Column dropped |
| Inconsistent category names | Both | All rows | Standardised to 7 categories |
| No chain identifier | Both | All rows | Added 'chain' column |

---

## 👩🏽‍💻 About the Author

**Assumpta Nwadinigwe**
Data Analyst | Python | SQL | Streamlit | Power BI

🔗 [LinkedIn](https://www.linkedin.com/in/assumptaassumynwadinigwe)
🐦 [X / Twitter](https://twitter.com/Assumptashuga)

---

## 📄 License

Copyright © 2025 Assumpta Nwadinigwe. All rights reserved.

This project was created by Assumpta Nwadinigwe. You are welcome to view and learn from this work. You may not copy, reproduce, or present this project as your own without explicit written permission from the author and full credit attribution.

See the [LICENSE](LICENSE) file for full details.
