
# ============================================================
# CINESTREAM DASHBOARD - FINAL APP (MODULES 1 TO 6)
# File: cinestream_app.py
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="CineStream Content Analytics",
    page_icon="🎬",
    layout="wide"
)

# ------------------------------------------------------------
# CACHED DATA LOADING + CLEANING FUNCTION
# Module 1 logic reused and cached for Module 6
# ------------------------------------------------------------
@st.cache_data
def load_and_clean_data(file_path="output/cleaned_cinestream.csv"):
    """
    Load CineStream catalog and perform all Module 1 cleaning steps.
    Returns cleaned DataFrame.
    """
    df = pd.read_csv(file_path)

    # Strip whitespace in text columns
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    # Standardize Type case
    if "Type" in df.columns:
        df["Type"] = df["Type"].str.title()

    # Drop duplicates
    df = df.drop_duplicates()

    # Replace out-of-range IMDbScore with NaN
    df.loc[(df["IMDbScore"] < 1) | (df["IMDbScore"] > 10), "IMDbScore"] = np.nan

    # Replace out-of-range CriticRating with NaN
    df.loc[(df["CriticRating"] < 1) | (df["CriticRating"] > 10), "CriticRating"] = np.nan

    # Replace absurd runtime with NaN
    # PRD mentions one absurd runtime value
    df.loc[df["RuntimeMinutes"] > 1000, "RuntimeMinutes"] = np.nan

    # Replace negative subscriber counts with 0
    df.loc[df["SubscribersGainedThousands"] < 0, "SubscribersGainedThousands"] = 0

    # Convert AddedDate to datetime
    df["AddedDate"] = pd.to_datetime(df["AddedDate"], errors="coerce")

    # Replace blank Director with NaN
    if "Director" in df.columns:
        df["Director"] = df["Director"].replace("", np.nan)

    # Derived columns
    df["Profit_Cr"] = df["RevenueCr"] - df["ProductionCostCr"]

    df["ROI_Pct"] = np.where(
        df["ProductionCostCr"] > 0,
        (df["Profit_Cr"] / df["ProductionCostCr"]) * 100,
        np.nan
    )

    df["Performance_Band"] = np.where(
        df["Profit_Cr"] > 20,
        "Hit",
        np.where(df["Profit_Cr"] < 0, "Flop", "Break-even")
    )

    return df


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
# If your CSV is in data/ folder, change to:
# df = load_and_clean_data("data/CineStream_Catalog.csv")
df = load_and_clean_data("output/cleaned_cinestream.csv")


# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------
st.title("🎬 CineStream Content Analytics Dashboard")
st.caption("Interactive dashboard to explore CineStream catalog performance across content, languages, money, and quality.")
st.markdown("---")

st.subheader("About the Dashboard")
st.markdown(
    """
This dashboard helps explore the **CineStream** content catalog using interactive filters.  
You can analyze titles by **genre, language, type, age rating, runtime, release quality, revenue, ROI, and audience performance**.
"""
)

# ------------------------------------------------------------
# SIDEBAR FILTERS (MODULE 4)
# FILTER FORM + APPLY BUTTON (MODULE 6)
# ------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    st.caption("The dashboard updates when you apply filters below.")

    with st.form("filter_form"):
        # Genre multiselect
        genre_options = sorted(df["Genre"].dropna().unique().tolist())
        selected_genres = st.multiselect(
            "Select Genre(s)",
            options=genre_options,
            default=genre_options
        )

        # Language multiselect
        language_options = sorted(df["Language"].dropna().unique().tolist())
        selected_languages = st.multiselect(
            "Select Language(s)",
            options=language_options,
            default=language_options
        )

        # Type selectbox
        type_options = ["All"] + sorted(df["Type"].dropna().unique().tolist())
        selected_type = st.selectbox(
            "Select Content Type",
            options=type_options
        )

        # AgeRating multiselect
        age_options = sorted(df["AgeRating"].dropna().unique().tolist())
        selected_age_ratings = st.multiselect(
            "Select Age Rating(s)",
            options=age_options,
            default=age_options
        )

        # IMDb slider
        imdb_series = df["IMDbScore"].dropna()
        imdb_min = 1.0 if imdb_series.empty else float(imdb_series.min())
        imdb_max = 10.0 if imdb_series.empty else float(imdb_series.max())

        selected_imdb_range = st.slider(
            "IMDb Score Range",
            min_value=1.0,
            max_value=10.0,
            value=(max(1.0, imdb_min), min(10.0, imdb_max)),
            step=0.1
        )

        # Runtime slider
        runtime_series = df["RuntimeMinutes"].dropna()
        runtime_min = 0 if runtime_series.empty else int(runtime_series.min())
        runtime_max = 500 if runtime_series.empty else int(runtime_series.max())

        selected_runtime_range = st.slider(
            "Runtime Range (Minutes)",
            min_value=runtime_min,
            max_value=runtime_max,
            value=(runtime_min, runtime_max)
        )

        # AddedDate range picker
        valid_dates = df["AddedDate"].dropna()
        if not valid_dates.empty:
            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()
            selected_date_range = st.date_input(
                "Added Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        else:
            selected_date_range = ()

        # Colour picker
        accent_color = st.color_picker(
            "Pick chart accent colour",
            "#E50914"
        )

        # Submit button
        apply_filters = st.form_submit_button("Apply filters")


# ------------------------------------------------------------
# FILTER DATA
# ------------------------------------------------------------
filtered_df = df.copy()

if selected_genres:
    filtered_df = filtered_df[filtered_df["Genre"].isin(selected_genres)]

if selected_languages:
    filtered_df = filtered_df[filtered_df["Language"].isin(selected_languages)]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]

if selected_age_ratings:
    filtered_df = filtered_df[filtered_df["AgeRating"].isin(selected_age_ratings)]

filtered_df = filtered_df[
    filtered_df["IMDbScore"].between(
        selected_imdb_range[0],
        selected_imdb_range[1],
        inclusive="both"
    )
]

filtered_df = filtered_df[
    filtered_df["RuntimeMinutes"].between(
        selected_runtime_range[0],
        selected_runtime_range[1],
        inclusive="both"
    )
]

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    filtered_df = filtered_df[
        filtered_df["AddedDate"].dt.date.between(start_date, end_date)
    ]

# ------------------------------------------------------------
# EMPTY STATE HANDLING (MODULE 6)
# ------------------------------------------------------------
if filtered_df.empty:
    st.warning("No records match the selected filters. Please change the filters and try again.")
    st.stop()

# ------------------------------------------------------------
# DOWNLOAD BUTTON
# ------------------------------------------------------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="filtered_cinestream.csv",
    mime="text/csv"
)

# ------------------------------------------------------------
# EXPANDER (MODULE 4)
# ------------------------------------------------------------
with st.expander("How this dashboard works"):
    st.markdown(
        """
- Use the **sidebar filters** to narrow the CineStream catalog.
- KPI cards update automatically for the filtered titles.
- Tabs break the analysis into **Overview**, **Genres & Languages**, **Money**, and **Quality Alerts**.
- You can also download the currently filtered dataset as a CSV file.
"""
    )

# ------------------------------------------------------------
# KPI CONTAINER (MODULE 4)
# ------------------------------------------------------------
with st.container():
    st.subheader("Key Performance Indicators")

    total_titles = len(filtered_df)
    total_views = filtered_df["ViewsMillions"].sum()
    total_watch_hours = filtered_df["WatchHoursMillions"].sum()
    avg_imdb = filtered_df["IMDbScore"].mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Titles", f"{total_titles:,}")

    with c2:
        st.metric("Total Views (Millions)", f"{total_views:,.2f}")

    with c3:
        st.metric("Total Watch Hours (Millions)", f"{total_watch_hours:,.2f}")

    with c4:
        st.metric("Average IMDb Score", f"{avg_imdb:.2f}" if pd.notnull(avg_imdb) else "N/A")

st.markdown("---")

# ------------------------------------------------------------
# SAMPLE DATA SECTION
# ------------------------------------------------------------
with st.container():
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Sample of Filtered Catalog")
        st.dataframe(filtered_df.head(10), use_container_width=True)

    with right:
        st.subheader("Top 5 Titles by Views")
        top5_views = (
            filtered_df[["Title", "Type", "Genre", "Language", "ViewsMillions"]]
            .sort_values(by="ViewsMillions", ascending=False)
            .head(5)
            .reset_index(drop=True)
        )
        st.table(top5_views)

        st.subheader("Example Title Record")
        example_row = filtered_df.iloc[0].copy()
        if pd.notnull(example_row["AddedDate"]):
            example_row["AddedDate"] = str(example_row["AddedDate"].date())
        else:
            example_row["AddedDate"] = None
        st.json(example_row.to_dict())

st.markdown("---")

# ------------------------------------------------------------
# TABS (MODULE 4)
# ------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Genres & Languages", "Money", "Quality Alerts"]
)

# ============================================================
# TAB 1 - OVERVIEW
# ============================================================
with tab1:
    st.header("Overview")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Chart 1: Titles added per month over time
    # --------------------------------------------------------
    with col1:
        st.subheader("Titles Added Per Month")

        monthly_titles = (
            filtered_df.dropna(subset=["AddedDate"])
            .assign(AddedMonth=lambda x: x["AddedDate"].dt.to_period("M").astype(str))
            .groupby("AddedMonth")
            .size()
            .reset_index(name="TitleCount")
        )

        if not monthly_titles.empty:
            monthly_titles = monthly_titles.sort_values("AddedMonth")
            monthly_titles = monthly_titles.set_index("AddedMonth")
            st.line_chart(monthly_titles["TitleCount"])
        else:
            st.info("No valid AddedDate data available for the current filters.")

    # --------------------------------------------------------
    # Chart 2: Count of titles per Type
    # --------------------------------------------------------
    with col2:
        st.subheader("Count of Titles by Type")

        type_counts = filtered_df["Type"].value_counts()
        if not type_counts.empty:
            st.bar_chart(type_counts)
        else:
            st.info("No content type data available.")

    # Optional extra summary
    st.markdown("### Filtered Dataset Summary")
    min_year = int(filtered_df["ReleaseYear"].min())
    max_year = int(filtered_df["ReleaseYear"].max())
    st.write(
        f"The current filtered view contains **{len(filtered_df)} titles** released between **{min_year}** and **{max_year}**."
    )

# ============================================================
# TAB 2 - GENRES & LANGUAGES
# ============================================================
with tab2:
    st.header("Genres & Languages")

    # --------------------------------------------------------
    # Best and worst performing language status messages
    # Module 6 requirement
    # --------------------------------------------------------
    lang_perf = (
        filtered_df.groupby("Language", as_index=False)[["ViewsMillions"]]
        .sum()
        .sort_values(by="ViewsMillions", ascending=False)
    )

    if not lang_perf.empty:
        best_lang = lang_perf.iloc[0]
        worst_lang = lang_perf.iloc[-1]

        st.success(
            f"Best-performing language by total views: {best_lang['Language']} "
            f"({best_lang['ViewsMillions']:.2f} million views)"
        )
        st.warning(
            f"Lowest-performing language by total views: {worst_lang['Language']} "
            f"({worst_lang['ViewsMillions']:.2f} million views)"
        )

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Chart 3: Top 10 Genres by Total Views (Matplotlib)
    # --------------------------------------------------------
    with col1:
        st.subheader("Top 10 Genres by Total Views")

        genre_views = (
            filtered_df.groupby("Genre")["ViewsMillions"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        if not genre_views.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.barh(genre_views["Genre"], genre_views["ViewsMillions"])
            ax.set_title("Top 10 Genres by Total Views")
            ax.set_xlabel("Total Views (Millions)")
            ax.set_ylabel("Genre")
            ax.invert_yaxis()
            st.pyplot(fig)
        else:
            st.info("No genre view data available.")

    # --------------------------------------------------------
    # Chart 4: Plotly Treemap Language -> Genre
    # --------------------------------------------------------
    with col2:
        st.subheader("Language → Genre Treemap by Views")

        treemap_df = (
            filtered_df.groupby(["Language", "Genre"], as_index=False)["ViewsMillions"]
            .sum()
        )

        if not treemap_df.empty:
            fig = px.treemap(
                treemap_df,
                path=["Language", "Genre"],
                values="ViewsMillions",
                title="Language → Genre by Total Views"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for treemap.")

# ============================================================
# TAB 3 - MONEY
# ============================================================
with tab3:
    st.header("Money")

    avg_roi = filtered_df["ROI_Pct"].mean()

    # --------------------------------------------------------
    # ROI status message (Module 6)
    # --------------------------------------------------------
    if pd.notnull(avg_roi):
        if avg_roi >= 0:
            st.info(f"Average ROI is positive at {avg_roi:.2f}%.")
        else:
            st.error(f"Average ROI is negative at {avg_roi:.2f}%.")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Chart 5: Scatter ProductionCostCr vs RevenueCr
    # --------------------------------------------------------
    with col1:
        st.subheader("Production Cost vs Revenue")

        money_df = filtered_df.dropna(
            subset=["ProductionCostCr", "RevenueCr", "Performance_Band", "Title"]
        )

        if not money_df.empty:
            fig = px.scatter(
                money_df,
                x="ProductionCostCr",
                y="RevenueCr",
                color="Performance_Band",
                hover_name="Title",
                title="Production Cost vs Revenue by Performance Band",
                labels={
                    "ProductionCostCr": "Production Cost (Cr)",
                    "RevenueCr": "Revenue (Cr)"
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost/revenue data available.")

    # --------------------------------------------------------
    # Chart 6: Average ROI by Genre (Matplotlib)
    # --------------------------------------------------------
    with col2:
        st.subheader("Average ROI by Genre")

        roi_by_genre = (
            filtered_df.groupby("Genre")["ROI_Pct"]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
        )

        if not roi_by_genre.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.bar(roi_by_genre["Genre"], roi_by_genre["ROI_Pct"])
            ax.set_title("Average ROI by Genre")
            ax.set_xlabel("Genre")
            ax.set_ylabel("Average ROI (%)")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.info("No ROI data available.")

# ============================================================
# TAB 4 - QUALITY ALERTS
# ============================================================
with tab4:
    st.header("Quality Alerts")

    # --------------------------------------------------------
    # Loss-making titles status message (Module 6)
    # --------------------------------------------------------
    loss_titles = filtered_df[filtered_df["Profit_Cr"] < 0]
    loss_count = len(loss_titles)

    if loss_count == 0:
        st.success("No titles are losing money in the current filtered view.")
    elif 1 <= loss_count <= 5:
        st.warning(f"{loss_count} title(s) are currently losing money in the filtered view.")
    else:
        st.error(f"{loss_count} titles are losing money in the filtered view.")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Chart 7: IMDbScore histogram with mean line
    # --------------------------------------------------------
    with col1:
        st.subheader("IMDb Score Distribution")

        imdb_data = filtered_df["IMDbScore"].dropna()

        if not imdb_data.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.hist(imdb_data, bins=10)
            ax.axvline(imdb_data.mean(), linestyle="--", linewidth=2)
            ax.set_title("Distribution of IMDb Scores")
            ax.set_xlabel("IMDb Score")
            ax.set_ylabel("Number of Titles")
            st.pyplot(fig)
        else:
            st.info("No IMDb score data available.")

    # --------------------------------------------------------
    # Chart 8: IMDbScore vs ViewsMillions scatter
    # --------------------------------------------------------
    with col2:
        st.subheader("IMDb Score vs Views")

        scatter_df = filtered_df.dropna(subset=["IMDbScore", "ViewsMillions"])

        if not scatter_df.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.scatter(scatter_df["IMDbScore"], scatter_df["ViewsMillions"])
            ax.set_title("IMDb Score vs Views")
            ax.set_xlabel("IMDb Score")
            ax.set_ylabel("Views (Millions)")
            st.pyplot(fig)
        else:
            st.info("No data available for IMDb vs Views scatter plot.")

    # --------------------------------------------------------
    # Optional table of loss-making titles
    # --------------------------------------------------------
    st.subheader("Loss-Making Titles Snapshot")
    if not loss_titles.empty:
        loss_display = (
            loss_titles[
                [
                    "Title", "Genre", "Language", "Type",
                    "ProductionCostCr", "RevenueCr", "Profit_Cr", "AgeRating"
                ]
            ]
            .sort_values("Profit_Cr")
            .head(10)
        )
        st.dataframe(loss_display, use_container_width=True)
    else:
        st.info("No loss-making titles to display.")

