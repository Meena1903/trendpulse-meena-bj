"""
TrendPulse - Task 1: Fetch Data from API
------------------------------------------
This script pulls the current top stories from Hacker News, sorts each
story into one of 5 categories based on keywords found in its title,
and saves up to 25 stories per category (125 total) into a JSON file
inside a local data/ folder.

Hacker News API docs: https://github.com/HackerNews/API
No API key is required.
"""

import requests
import json
import os
import re
import time
from datetime import datetime

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------

# HN asks that requests identify themselves with a User-Agent header
HEADERS = {"User-Agent": "TrendPulse/1.0"}

TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

# How many story IDs to pull from the top stories list
NUM_IDS_TO_FETCH = 500

# Max stories we want to keep per category
MAX_PER_CATEGORY = 25

# Keyword list for each category (case-insensitive matching)
CATEGORY_KEYWORDS = {
    "technology": ["AI", "software", "tech", "code", "computer", "data",
                   "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election",
                  "climate", "attack", "global"],
    "sports": ["NFL", "NBA", "FIFA", "sport", "game", "team", "player",
               "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology",
                "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book",
                       "show", "award", "streaming"],
}


# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def get_top_story_ids(limit=NUM_IDS_TO_FETCH):
    """
    Fetches the list of top story IDs from Hacker News and returns
    the first `limit` of them. Returns an empty list if the request
    fails, so the rest of the script can still run gracefully.
    """
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()  # raises an error for bad status codes (4xx/5xx)
        story_ids = response.json()
        return story_ids[:limit]
    except requests.exceptions.RequestException as error:
        print(f"Failed to fetch top story IDs: {error}")
        return []


def get_story_details(story_id):
    """
    Fetches a single story's details by ID.
    Returns None if the request fails or the story has no data
    (e.g. it was deleted), so the caller can just skip it.
    """
    try:
        url = ITEM_URL.format(story_id)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as error:
        print(f"Failed to fetch story {story_id}: {error}")
        return None


def matches_category(title, keywords):
    """
    Checks whether a story title contains any of the given keywords.
    Matching is case-insensitive and uses word boundaries (\\b) so that
    short keywords like "AI" or "game" don't accidentally match inside
    unrelated words (e.g. "AI" should not match "certain").
    """
    if not title:
        return False
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, title, re.IGNORECASE):
            return True
    return False


def build_story_record(story, category):
    """
    Pulls out only the fields we care about from a raw HN story object
    and attaches the category we assigned plus a collection timestamp.
    """
    return {
        "post_id": story.get("id"),
        "title": story.get("title"),
        "category": category,
        "score": story.get("score", 0),
        "num_comments": story.get("descendants", 0),
        "author": story.get("by"),
        "collected_at": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------
# MAIN COLLECTION LOGIC
# ---------------------------------------------------------------------

def collect_trending_stories():
    """
    Main pipeline:
      1. Get the top story IDs once (they're the same list for every category).
      2. For each category, go through the IDs, fetch story details, and
         keep the story if its title matches that category's keywords,
         until we reach MAX_PER_CATEGORY or run out of IDs.
      3. Sleep 2 seconds after finishing each category loop (not per story).
    """
    story_ids = get_top_story_ids()
    if not story_ids:
        print("No story IDs were fetched — nothing to collect.")
        return []

    # Simple cache so that if the same story is looked at again for
    # another category, we don't hit the API a second time for it.
    # This keeps the "one sleep per category loop" rule cheap to run
    # while still following the required category-by-category structure.
    story_cache = {}

    all_collected_stories = []

    for category, keywords in CATEGORY_KEYWORDS.items():
        category_count = 0
        print(f"\nCollecting stories for category: {category}")

        for story_id in story_ids:
            if category_count >= MAX_PER_CATEGORY:
                break  # we already have enough stories for this category

            # Use cached story details if we've already fetched this ID
            if story_id in story_cache:
                story = story_cache[story_id]
            else:
                story = get_story_details(story_id)
                story_cache[story_id] = story

            if story is None:
                continue  # request failed or story unavailable, skip it

            title = story.get("title", "")
            if matches_category(title, keywords):
                record = build_story_record(story, category)
                all_collected_stories.append(record)
                category_count += 1

        print(f"  -> {category_count} stories collected for '{category}'")

        # One sleep per category loop, as required by the task spec
        time.sleep(2)

    return all_collected_stories


# ---------------------------------------------------------------------
# SAVE TO FILE
# ---------------------------------------------------------------------

def save_stories_to_json(stories):
    """
    Saves the collected stories list to data/trends_YYYYMMDD.json,
    creating the data/ folder first if it doesn't already exist.
    """
    os.makedirs("data", exist_ok=True)

    today_str = datetime.now().strftime("%Y%m%d")
    filepath = os.path.join("data", f"trends_{today_str}.json")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stories, f, indent=2)

    print(f"\nCollected {len(stories)} stories. Saved to {filepath}")


# ---------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    stories = collect_trending_stories()
    save_stories_to_json(stories)