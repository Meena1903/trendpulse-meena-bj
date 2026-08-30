"""
TrendPulse - Task 2: Clean the Data & Save as CSV
----------------------------------------------------
This script loads the raw JSON produced by Task 1, cleans it up with
Pandas (duplicates, missing values, wrong types, low-quality rows,
messy whitespace), and saves a tidy CSV to data/trends_clean.csv.
"""

import pandas as pd
import glob
import os

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

DATA_FOLDER = "data"
OUTPUT_CSV = os.path.join(DATA_FOLDER, "trends_clean.csv")

# Any story with fewer than this many upvotes is considered low quality
MIN_SCORE = 5


# ---------------------------------------------------------------------
# STEP 1 — LOAD THE JSON FILE
# ---------------------------------------------------------------------

def find_latest_trends_file():
    """
    Task 1 saves files as data/trends_YYYYMMDD.json, so the exact
    filename changes depending on the day it was run. Rather than
    hardcoding a date, this grabs the most recently modified file
    that matches the trends_*.json pattern (this also avoids
    accidentally picking up trends_clean.csv, since we're only
    globbing for .json files).
    """
    pattern = os.path.join(DATA_FOLDER, "trends_*.json")
    matching_files = glob.glob(pattern)

    if not matching_files:
        raise FileNotFoundError(
            f"No files matching '{pattern}' were found. "
            "Run task1_data_collection.py first."
        )

    # Pick the file that was modified most recently
    latest_file = max(matching_files, key=os.path.getmtime)
    return latest_file


def load_json_to_dataframe(filepath):
    """
    Loads the Task 1 JSON output into a Pandas DataFrame and prints
    how many rows were loaded, as required.
    """
    df = pd.read_json(filepath)
    print(f"Loaded {len(df)} stories from {filepath}")
    return df


# ---------------------------------------------------------------------
# STEP 2 — CLEAN THE DATA
# ---------------------------------------------------------------------

def clean_data(df):
    """
    Runs through each cleaning issue listed in the task brief, in
    order, printing the row count after each step that removes rows.
    """

    # --- Duplicates: same post_id shouldn't appear twice ---
    # keep="first" keeps the first occurrence and drops any later
    # duplicates of the same post_id
    df = df.drop_duplicates(subset="post_id", keep="first")
    print(f"After removing duplicates: {len(df)}")

    # --- Missing values: post_id, title, and score are all required ---
    # subset= means we only drop a row if ONE OF THESE THREE is missing,
    # not if some other column (like author) happens to be empty
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # --- Data types: score and num_comments must be integers ---
    # pd.to_numeric with errors="coerce" turns anything non-numeric into
    # NaN so it doesn't crash the script; num_comments might be missing
    # for some stories so we fill those with 0 before converting to int
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce").fillna(0)
    df["score"] = df["score"].astype(int)
    df["num_comments"] = df["num_comments"].astype(int)

    # post_id isn't mentioned in the brief's type-fix list, but pandas
    # silently upcasts an int column to float if it ever contained a
    # null (which we just dropped above), so without this fix IDs would
    # print as "1.0" instead of "1" in the final CSV. We already dropped
    # any missing post_id rows above, so this cast is always safe here.
    df["post_id"] = df["post_id"].astype(int)

    # --- Low quality: drop anything under the minimum score threshold ---
    df = df[df["score"] >= MIN_SCORE]
    print(f"After removing low scores: {len(df)}")

    # --- Whitespace: strip extra spaces from titles ---
    # .str.strip() removes leading/trailing whitespace; done last since
    # it doesn't affect row count, just the values themselves
    df["title"] = df["title"].str.strip()

    return df


# ---------------------------------------------------------------------
# STEP 3 — SAVE AS CSV
# ---------------------------------------------------------------------

def save_and_summarise(df):
    """
    Saves the cleaned DataFrame to CSV, prints a confirmation message,
    and prints a per-category breakdown of how many stories remain.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # index=False so Pandas doesn't add its own row-number column to the CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT_CSV}")

    print("\nStories per category:")
    category_counts = df["category"].value_counts()
    for category, count in category_counts.items():
        # ljust pads the category name so the numbers line up in a column
        print(f"  {category.ljust(15)}{count}")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    input_file = find_latest_trends_file()
    stories_df = load_json_to_dataframe(input_file)
    cleaned_df = clean_data(stories_df)
    save_and_summarise(cleaned_df)