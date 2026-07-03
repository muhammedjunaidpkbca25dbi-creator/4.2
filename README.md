# 🎬 CineStream Content Analytics Dashboard

## Project Overview

CineStream Content Analytics is an interactive **Streamlit dashboard** built as a BCA data analytics project.
The dashboard analyzes a fictional OTT streaming platform catalog containing movies, series, documentaries, and stand-up specials. It helps users explore content performance using filters, KPIs, charts, and quality alerts.

This project is based on the **CineStream catalog dataset** and answers business questions related to:

* genre and language performance
* watch behaviour and audience completion
* revenue and ROI
* title quality and ratings
* loss-making content analysis

---

## Objectives

The dashboard is designed to answer the following questions:

1. Which genres and languages drive the most views and watch hours?
2. Are big-budget productions earning back their production cost?
3. How is the content mix distributed across Movies, Series, Documentaries, and Stand-up specials?
4. Which content categories perform best by language and genre?
5. Do higher IMDb scores translate into more views?
6. Which titles are losing money and need attention?

---

## Project Features

### 1. Data Cleaning and Preparation

The dataset is cleaned before analysis:

* removed duplicate rows
* stripped trailing spaces from text columns
* standardized the `Type` column
* converted `AddedDate` into datetime format
* replaced invalid IMDb and Critic ratings with `NaN`
* handled negative subscriber values
* created derived columns:

  * `Profit_Cr`
  * `ROI_Pct`
  * `Performance_Band`

### 2. KPI Dashboard

The app displays:

* **Total Titles**
* **Total Views (Millions)**
* **Total Watch Hours (Millions)**
* **Average IMDb Score**

### 3. Interactive Filters

Users can filter the dashboard using:

* Genre
* Language
* Type
* Age Rating
* IMDb score range
* Runtime range
* Added date range

### 4. Dashboard Tabs

The app is divided into four sections:

* **Overview**
* **Genres & Languages**
* **Money**
* **Quality Alerts**

### 5. Visualizations

The dashboard includes multiple charts such as:

* line chart for titles added per month
* bar chart for content type distribution
* top genres by views
* language → genre treemap
* production cost vs revenue scatter plot
* average ROI by genre
* IMDb score histogram
* IMDb score vs views scatter plot

### 6. Smart Status Messages

The app displays status alerts for:

* loss-making titles
* positive/negative ROI
* best-performing and worst-performing languages
* empty filtered results

---

## Dataset Information

**Dataset Name:** `CineStream_Catalog.csv`

The dataset contains content catalog details such as:

* title
* type
* genre
* language
* country
* director
* release year
* added date
* runtime
* IMDb score
* watch hours
* views
* production cost
* revenue
* subscribers gained
* critic rating

---

## Project Structure

```text
CineStream/
│
├── data/
│   └── CineStream_Catalog.csv
│
├── notebooks/
│   └── m1_explore.ipynb
│
├── outputs/
│   └── cleaned_cinestream.csv
│
├── cinestream_app.py
├── requirements.txt
└── README.md
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd CineStream
```

### 2. Install required libraries

```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run cinestream_app.py
```

---

## Technologies Used

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Matplotlib**
* **Plotly**

---

## Output

The final project provides:

* an interactive OTT analytics dashboard
* cleaned CineStream dataset
* business insights through visual analytics
* a deployable Streamlit application

---

## Author

**Muhammed Junaid PK**
BCA Data Analytics Project
