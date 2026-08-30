"""
TrendPulse - Task 4: Visualisations
----------------------------------------
Loads the analysed CSV from Task 3 and builds 3 Matplotlib charts
(top stories, stories per category, score vs comments), plus a
combined dashboard figure. All charts are saved as PNGs in outputs/.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

INPUT_CSV = os.path.join("data", "trends_analysed.csv")
OUTPUT_FOLDER = "outputs"

MAX_TITLE_LENGTH = 50  # titles longer than this get truncated with "..."


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def shorten_title(title):
    """
    Truncates a story title to MAX_TITLE_LENGTH characters so long
    titles don't overwhelm the y-axis labels on Chart 1.
    """
    title = str(title)
    if len(title) > MAX_TITLE_LENGTH:
        return title[:MAX_TITLE_LENGTH].rstrip() + "..."
    return title


# ---------------------------------------------------------------------
# STEP 1 — SETUP
# ---------------------------------------------------------------------

def load_data(filepath):
    """Loads the analysed CSV from Task 3 into a DataFrame."""
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows from {filepath}")
    return df


# ---------------------------------------------------------------------
# STEP 2 — CHART 1: TOP 10 STORIES BY SCORE
# ---------------------------------------------------------------------

def make_top_stories_chart(df):
    """
    Horizontal bar chart of the top 10 highest-scoring stories.
    """
    top10 = df.sort_values("score", ascending=False).head(10)

    # Shorten long titles so the y-axis labels stay readable
    labels = [shorten_title(t) for t in top10["title"]]

    fig, ax = plt.subplots(figsize=(10, 6))

    # invert_yaxis() so the highest score ends up at the top of the
    # chart instead of the bottom, which reads more naturally
    ax.barh(labels, top10["score"], color="steelblue")
    ax.invert_yaxis()

    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score")
    ax.set_ylabel("Story Title")

    fig.tight_layout()  # stops long titles getting cut off at the edge
    fig.savefig(os.path.join(OUTPUT_FOLDER, "chart1_top_stories.png"))
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------
# STEP 3 — CHART 2: STORIES PER CATEGORY
# ---------------------------------------------------------------------

def make_category_chart(df):
    """
    Bar chart of how many stories fall into each category, with each
    bar getting its own colour.
    """
    category_counts = df["category"].value_counts()

    # A small fixed colour list so each bar is visibly different;
    # cycles back around if there were ever more than 5 categories
    bar_colours = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(category_counts.index, category_counts.values,
           color=bar_colours[:len(category_counts)])

    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Stories")

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FOLDER, "chart2_categories.png"))
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------
# STEP 4 — CHART 3: SCORE VS COMMENTS
# ---------------------------------------------------------------------

def make_scatter_chart(df):
    """
    Scatter plot of score vs num_comments, split by colour into
    popular (is_popular == True) and non-popular stories.
    """
    popular = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plotting the two groups as separate scatter calls is what gives
    # us a clean legend with two labelled entries
    ax.scatter(not_popular["score"], not_popular["num_comments"],
               color="gray", alpha=0.6, label="Not Popular")
    ax.scatter(popular["score"], popular["num_comments"],
               color="crimson", alpha=0.7, label="Popular")

    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Comments")
    ax.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FOLDER, "chart3_scatter.png"))
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------
# BONUS — COMBINED DASHBOARD
# ---------------------------------------------------------------------

def make_dashboard(df):
    """
    Rebuilds all 3 charts side by side in a single figure using
    plt.subplots(1, 3), so the dashboard is one self-contained image.
    """
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    ax1, ax2, ax3 = axes

    # --- Panel 1: Top 10 stories ---
    top10 = df.sort_values("score", ascending=False).head(10)
    labels = [shorten_title(t) for t in top10["title"]]
    ax1.barh(labels, top10["score"], color="steelblue")
    ax1.invert_yaxis()
    ax1.set_title("Top 10 Stories by Score")
    ax1.set_xlabel("Score")
    ax1.set_ylabel("Story Title")

    # --- Panel 2: Stories per category ---
    category_counts = df["category"].value_counts()
    bar_colours = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]
    ax2.bar(category_counts.index, category_counts.values,
            color=bar_colours[:len(category_counts)])
    ax2.set_title("Stories per Category")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Number of Stories")
    ax2.tick_params(axis="x", rotation=30)  # angled labels so they don't overlap

    # --- Panel 3: Score vs comments scatter ---
    popular = df[df["is_popular"] == True]
    not_popular = df[df["is_popular"] == False]
    ax3.scatter(not_popular["score"], not_popular["num_comments"],
                color="gray", alpha=0.6, label="Not Popular")
    ax3.scatter(popular["score"], popular["num_comments"],
                color="crimson", alpha=0.7, label="Popular")
    ax3.set_title("Score vs Comments")
    ax3.set_xlabel("Score")
    ax3.set_ylabel("Number of Comments")
    ax3.legend()

    fig.suptitle("TrendPulse Dashboard", fontsize=16, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FOLDER, "dashboard.png"))
    plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    stories_df = load_data(INPUT_CSV)

    make_top_stories_chart(stories_df)
    make_category_chart(stories_df)
    make_scatter_chart(stories_df)
    make_dashboard(stories_df)

    print(f"All charts saved to {OUTPUT_FOLDER}/")