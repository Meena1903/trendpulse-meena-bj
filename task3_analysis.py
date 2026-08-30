"""
TrendPulse - Task 3: Analysis with Pandas & NumPy
-----------------------------------------------------
Loads the cleaned CSV from Task 2, explores it, computes stats with
NumPy, adds two derived columns (engagement, is_popular), and saves
the result to data/trends_analysed.csv for Task 4 to chart.
"""

import pandas as pd
import numpy as np
import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

INPUT_CSV = os.path.join("data", "trends_clean.csv")
OUTPUT_CSV = os.path.join("data", "trends_analysed.csv")


# ---------------------------------------------------------------------
# STEP 1 — LOAD AND EXPLORE
# ---------------------------------------------------------------------

def load_and_explore(filepath):
    """
    Loads the cleaned CSV and prints a quick first look at the data:
    the first 5 rows, the shape, and the plain average score/comments
    (this is a simple Pandas .mean() check before we do the more
    detailed NumPy stats in step 2).
    """
    df = pd.read_csv(filepath)

    print(f"Loaded data: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())

    avg_score = df["score"].mean()
    avg_comments = df["num_comments"].mean()
    print(f"\nAverage score   : {avg_score:,.0f}")
    print(f"Average comments: {avg_comments:,.0f}")

    return df


# ---------------------------------------------------------------------
# STEP 2 — BASIC ANALYSIS WITH NUMPY
# ---------------------------------------------------------------------

def numpy_stats(df):
    """
    Runs the required stats through NumPy directly (rather than the
    Pandas .mean()/.std() shortcuts) since the brief specifically asks
    for NumPy to be used here. .to_numpy() converts the score column
    into a plain NumPy array first.
    """
    scores = df["score"].to_numpy()

    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)
    max_score = np.max(scores)
    min_score = np.min(scores)

    print("\n--- NumPy Stats ---")
    print(f"Mean score   : {mean_score:,.0f}")
    print(f"Median score : {median_score:,.0f}")
    print(f"Std deviation: {std_score:,.0f}")
    print(f"Max score    : {max_score:,.0f}")
    print(f"Min score    : {min_score:,.0f}")

    # --- Which category has the most stories? ---
    # value_counts() sorts descending by default, so the first entry
    # (.index[0]) is the category with the highest count
    category_counts = df["category"].value_counts()
    top_category = category_counts.index[0]
    top_category_count = category_counts.iloc[0]
    print(f"\nMost stories in: {top_category} ({top_category_count} stories)")

    # --- Which story has the most comments? ---
    # idxmax() gives us the row label (index) of the highest num_comments
    # value, which we then use to look up that full row with .loc[]
    top_comment_idx = df["num_comments"].idxmax()
    top_comment_row = df.loc[top_comment_idx]
    print(f'Most commented story: "{top_comment_row["title"]}" '
          f'\u2014 {top_comment_row["num_comments"]:,} comments')

    return mean_score


# ---------------------------------------------------------------------
# STEP 3 — ADD NEW COLUMNS
# ---------------------------------------------------------------------

def add_new_columns(df, mean_score):
    """
    Adds the two derived columns required by the brief:
      - engagement: comments per upvote (using +1 in the denominator
        so a story with a score of 0 doesn't cause a divide-by-zero)
      - is_popular: whether a story scored above the average score
    """
    df["engagement"] = df["num_comments"] / (df["score"] + 1)
    df["is_popular"] = df["score"] > mean_score
    return df


# ---------------------------------------------------------------------
# STEP 4 — SAVE THE RESULT
# ---------------------------------------------------------------------

def save_result(df):
    """
    Saves the DataFrame (now with the 2 new columns) to
    data/trends_analysed.csv and confirms with a print message.
    """
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved to {OUTPUT_CSV}")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    stories_df = load_and_explore(INPUT_CSV)
    mean_score = numpy_stats(stories_df)
    stories_df = add_new_columns(stories_df, mean_score)
    save_result(stories_df)